from __future__ import annotations
from typing import Optional, Any

from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path
import asyncio
import subprocess
from app.websockets.manager import manager

from app.models import (
    Execution, ExecutionGroup, ServerTemplate, ServerConfiguration,
    Server, Configuration, Template, TemplateConfiguration
)
from app.ansible_runner.inventory_generator import generate_inventory
from app.ansible_runner.playbook_generator import generate_playbook
from app.ansible_runner.paths import (
    get_inventory_path, get_playbook_path,
    ensure_group_dirs_exist, get_log_dir
)
import logging

logger = logging.getLogger(__name__)

class ExecutionRunnerService:
    def __init__(self, db: Session):
        self.db = db

    def create_execution(
        self,
        title: Optional[str],
        created_by: Optional[int],
        replayed_from_id: Optional[int] = None
    ) -> Execution:
        """
        Crée une nouvelle exécution avec traçabilité.
        """
        execution = Execution(
            title=title,
            created_by=created_by,
            replayed_from_id=replayed_from_id
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        logger.info(f"[Execution] ➕ Créée : ID={execution.id}")
        return execution

    def create_group(
        self,
        execution: Execution,
        name: Optional[str],
        servers: list[Server],
        elements: list[dict[str, Any]],
        configs: list[Configuration],
        templates: list[Template],
        template_confs: list[TemplateConfiguration],
        created_by: Optional[int],
        replayed_from_id: Optional[int] = None
    ) -> ExecutionGroup:
        """
        Crée un groupe d'exécution avec inventaire et playbook.
        """
        group = ExecutionGroup(
            execution_id=execution.id,
            name=name or f"group_{len(execution.execution_groups) + 1}",
            status="pending",
            created_by=created_by,
            replayed_from_id=replayed_from_id
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)

        ensure_group_dirs_exist(execution.id, group.id)
        inventory_path = get_inventory_path(execution.id, group.id)
        playbook_path = get_playbook_path(execution.id, group.id)

        generate_inventory(servers, str(inventory_path))
        generate_playbook(elements, configs, templates, template_confs, playbook_path, group.name, group.id)

        group.inventory_path = str(inventory_path)
        group.playbook_path = str(playbook_path)
        self.db.commit()

        logger.info(f"[ExecutionGroup] ➕ Créé : ID={group.id}, Exécution={execution.id}")
        return group

    def create_server_template(
        self,
        server_id: int,
        template_id: int,
        created_by: Optional[int],
        replayed_from_id: Optional[int] = None
    ) -> ServerTemplate:
        """
        Crée un lien Server ↔ Template (ServerTemplate).
        """
        st = ServerTemplate(
            server_id=server_id,
            template_id=template_id,
            created_by=created_by,
            replayed_from_id=replayed_from_id
        )
        self.db.add(st)
        self.db.commit()
        self.db.refresh(st)
        logger.info(f"[ServerTemplate] ➕ Attaché : Server={server_id} → Template={template_id}")
        return st

    def create_server_configurations(
        self,
        group: ExecutionGroup,
        servers: list[Server],
        elements: list[dict[str, Any]],
        created_by: Optional[int],
        server_template_map: Optional[dict[tuple[int, int], int]] = None
    ) -> list[ServerConfiguration]:
        """
        Crée tous les ServerConfiguration liés à un groupe et ses serveurs.
        """
        server_confs: list[ServerConfiguration] = []
        for server in servers:
            for element in elements:
                el_type = element.get("type")
                el_id = element.get("id")
                sc = ServerConfiguration(
                    server_id=server.id,
                    execution_group_id=group.id,
                    status="pending",
                    created_by=created_by,
                    replayed_from_id=element.get("replayed_from_id")
                )

                if el_type == "configuration":
                    sc.configuration_id = el_id
                    sc.source = "configuration"

                elif el_type == "manual":
                    sc.source = "manual"
                    sc.custom_command = element.get("command", "")

                elif el_type == "template":
                    sc.source = "template"
                    if server_template_map:
                        key = (server.id, el_id)
                        sc.server_template_id = server_template_map.get(key)

                server_confs.append(sc)
                self.db.add(sc)

        self.db.commit()
        logger.info(f"[ServerConfigurations] ➕ {len(server_confs)} créés pour Groupe={group.id}")
        return server_confs


    async def launch_group(self, group_id: int) -> None:
        """
        Exécute un groupe via Ansible et met à jour les statuts en temps réel.
        """
        group = self.db.query(ExecutionGroup).filter_by(id=group_id).first()
        if not group:
            logger.error(f"[ExecutionGroup] ❌ Inexistant : ID={group_id}")
            return

        execution = group.execution
        group.status = "running"
        group.started_at = datetime.utcnow()
        self.db.commit()

        total = len(group.server_configurations)

        for idx, sc in enumerate(group.server_configurations, start=1):
            try:
                sc.status = "running"
                sc.started_at = datetime.utcnow()
                self.db.commit()

                log_dir = get_log_dir(execution.id, group.id)
                log_file = log_dir / f"server_{sc.server_id}_conf_{sc.id}.log"

                result = await asyncio.to_thread(
                    subprocess.run,
                    [
                        "ansible-playbook",
                        str(Path(group.playbook_path)),
                        "-i", str(Path(group.inventory_path)),
                        "-l", sc.server.name,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                sc.status = "success" if result.returncode == 0 else "failed"
                sc.return_code = result.returncode
                sc.stdout = result.stdout
                sc.stderr = result.stderr
                sc.finished_at = datetime.utcnow()
                log_file.write_text(result.stdout + "\n" + result.stderr)
                sc.log_path = str(log_file)
                self.db.commit()

                # Envoi complet
                await manager.broadcast_json(execution.id, {
                    "event": "server_config_update",
                    "group_id": group.id,
                    "group_name": group.name,
                    "server_config_id": sc.id,
                    "server_id": sc.server.id,
                    "server_name": sc.server.name,
                    "status": sc.status,
                    "return_code": sc.return_code,
                    "source": sc.source,
                    "configuration_id": sc.configuration_id,
                    "server_template_id": sc.server_template_id,
                    "custom_command": sc.custom_command,
                    "started_at": sc.started_at.isoformat() if sc.started_at else None,
                    "finished_at": sc.finished_at.isoformat() if sc.finished_at else None,
                })

                # Progression du groupe
                completed = sum(1 for s in group.server_configurations if s.status in ["success", "failed"])
                percent = int(completed / total * 100) if total > 0 else 0

                await manager.broadcast_json(execution.id, {
                    "event": "group_progress",
                    "group_id": group.id,
                    "group_name": group.name,
                    "completed": completed,
                    "total": total,
                    "percent": percent,
                })

            except Exception as e:
                logger.exception(f"[Ansible] ❌ Erreur sur ServerConfig {sc.id} : {e}")
                sc.status = "failed"
                sc.stderr = str(e)
                sc.finished_at = datetime.utcnow()
                self.db.commit()

        group.finished_at = datetime.utcnow()
        self.update_group_status(group.id)
        self.update_server_template_statuses(group)
        self.update_execution_status(execution.id)

        await manager.broadcast_json(execution.id, {
            "event": "group_finished",
            "group_id": group.id,
            "group_name": group.name,
            "status": group.status,
        })

        # Progression de l'exécution
        total_sc = sum(len(g.server_configurations) for g in execution.execution_groups)
        completed_sc = sum(
            1 for g in execution.execution_groups for s in g.server_configurations if s.status in ["success", "failed"]
        )
        percent = int(completed_sc / total_sc * 100) if total_sc > 0 else 0

        await manager.broadcast_json(execution.id, {
            "event": "execution_progress",
            "execution_id": execution.id,
            "completed": completed_sc,
            "total": total_sc,
            "percent": percent,
        })

        logger.info(f"[ExecutionGroup] ✅ Terminé : ID={group.id} → {group.status}")


    async def launch_execution(self, execution_id: int) -> None:
        """
        Lance l'exécution complète (tous les groupes un par un).
        """
        execution = self.db.query(Execution).filter_by(id=execution_id).first()
        if not execution:
            logger.error(f"[Execution] ❌ Introuvable : ID={execution_id}")
            return

        execution.status = "running"
        execution.started_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"[Execution] ▶️ Lancement : ID={execution.id}")

        for group in execution.execution_groups:
            await self.launch_group(group.id)

        await manager.broadcast_json(execution.id, {
            "event": "execution_status_update",
            "execution_id": execution.id,
            "status": execution.status,
        })

    def update_group_status(self, group_id: int) -> None:
        """
        Met à jour le statut d'un groupe en fonction des ServerConfigurations.
        """
        group = self.db.query(ExecutionGroup).filter_by(id=group_id).first()
        if not group:
            return

        statuses = [sc.status for sc in group.server_configurations if sc.status]
        if all(s == "success" for s in statuses):
            group.status = "success"
        elif any(s == "success" for s in statuses):
            group.status = "partial"
        else:
            group.status = "failed"

        group.started_at = min((sc.started_at for sc in group.server_configurations if sc.started_at), default=None)
        group.finished_at = max((sc.finished_at for sc in group.server_configurations if sc.finished_at), default=None)
        self.db.commit()

        logger.info(f"[Group] 🔁 Statut mis à jour : {group.status}")

    def update_execution_status(self, execution_id: int) -> None:
        """
        Met à jour le statut global d'une exécution en fonction de ses groupes.
        """
        execution = self.db.query(Execution).filter_by(id=execution_id).first()
        if not execution:
            return

        statuses = [g.status for g in execution.execution_groups if g.status]
        if any(s == "running" for s in statuses):
            execution.status = "running"
        elif all(s == "success" for s in statuses):
            execution.status = "success"
        elif any(s == "success" for s in statuses):
            execution.status = "partial"
        else:
            execution.status = "failed"

        execution.started_at = min((g.started_at for g in execution.execution_groups if g.started_at), default=None)
        execution.finished_at = max((g.finished_at for g in execution.execution_groups if g.finished_at), default=None)
        self.db.commit()

        logger.info(f"[Execution] 🔁 Statut mis à jour : {execution.status}")

    def update_server_template_statuses(self, group: ExecutionGroup) -> None:
        """
        Met à jour le statut de chaque ServerTemplate du groupe.
        """
        mapping: dict[int, list[ServerConfiguration]] = {}
        for sc in group.server_configurations:
            if sc.server_template_id:
                mapping.setdefault(sc.server_template_id, []).append(sc)

        for st_id, scs in mapping.items():
            st = self.db.query(ServerTemplate).filter_by(id=st_id).first()
            if not st:
                continue

            statuses = [sc.status for sc in scs]
            if all(s == "success" for s in statuses):
                st.status = "success"
            elif any(s == "success" for s in statuses):
                st.status = "partial"
            else:
                st.status = "failed"

            st.started_at = min((sc.started_at for sc in scs if sc.started_at), default=None)
            st.finished_at = max((sc.finished_at for sc in scs if sc.finished_at), default=None)
            self.db.commit()

            logger.info(f"[ServerTemplate] 🔁 Statut mis à jour : ID={st.id} → {st.status}")

    # def replay_execution(self, original_execution_id: int, created_by: Optional[int]) -> Execution:
    #     """
    #     Rejoue une exécution existante en copiant tous les groupes et les éléments associés.
    #     """
    #     original_execution = self.db.query(Execution).filter_by(id=original_execution_id).first()
    #     if not original_execution:
    #         raise ValueError("Original Execution not found")

    #     new_execution = self.create_execution(
    #         title=f"{original_execution.title} (Replay)",
    #         created_by=created_by,
    #         replayed_from_id=original_execution.id
    #     )

    #     for original_group in original_execution.execution_groups:
    #         original_servers = [sc.server for sc in original_group.server_configurations]
    #         original_elements = []
    #         for sc in original_group.server_configurations:
    #             if sc.source == "configuration":
    #                 original_elements.append({
    #                     "type": "configuration",
    #                     "id": sc.configuration_id,
    #                     "replayed_from_id": sc.id
    #                 })
    #             elif sc.source == "template":
    #                 original_elements.append({
    #                     "type": "template",
    #                     "id": sc.server_template.template_id,
    #                     "replayed_from_id": sc.id
    #                 })
    #             elif sc.source == "manual":
    #                 original_elements.append({
    #                     "type": "manual",
    #                     "command": sc.custom_command,
    #                     "replayed_from_id": sc.id
    #                 })

    #         configs = self.db.query(Configuration).all()
    #         templates = self.db.query(Template).all()
    #         template_confs = self.db.query(TemplateConfiguration).all()

    #         new_group = self.create_group(
    #             execution=new_execution,
    #             name=original_group.name,
    #             servers=original_servers,
    #             elements=original_elements,
    #             configs=configs,
    #             templates=templates,
    #             template_confs=template_confs,
    #             created_by=created_by,
    #             replayed_from_id=original_group.id
    #         )

    #         server_template_map = {}
    #         for sc in original_group.server_configurations:
    #             if sc.source == "template" and sc.server_template:
    #                 st = self.create_server_template(
    #                     server_id=sc.server_id,
    #                     template_id=sc.server_template.template_id,
    #                     created_by=created_by,
    #                     replayed_from_id=sc.server_template.id
    #                 )
    #                 server_template_map[(sc.server_id, st.template_id)] = st.id

    #         self.create_server_configurations(
    #             group=new_group,
    #             servers=original_servers,
    #             elements=original_elements,
    #             created_by=created_by,
    #             server_template_map=server_template_map
    #         )

    #     self.db.commit()
    #     logger.info(f"[Execution] 🔁 Replay créé : ID={new_execution.id}")
    #     return new_execution

    # def replay_group(self, original_group_id: int, created_by: Optional[int]) -> Execution:
    #     """
    #     Rejoue un groupe d'exécution précis (cas spécial).
    #     """
    #     original_group = self.db.query(ExecutionGroup).filter_by(id=original_group_id).first()
    #     if not original_group:
    #         raise ValueError("Original Group not found")

    #     original_execution = original_group.execution

    #     new_execution = self.create_execution(
    #         title=f"{original_execution.title or 'Execution'} - Group Replay",
    #         created_by=created_by,
    #         replayed_from_id=original_execution.id
    #     )

    #     original_servers = [sc.server for sc in original_group.server_configurations]

    #     original_elements = []
    #     for sc in original_group.server_configurations:
    #         if sc.source == "configuration":
    #             original_elements.append({
    #                 "type": "configuration",
    #                 "id": sc.configuration_id,
    #                 "replayed_from_id": sc.id
    #             })
    #         elif sc.source == "template":
    #             original_elements.append({
    #                 "type": "template",
    #                 "id": sc.server_template.template_id,
    #                 "replayed_from_id": sc.id
    #             })
    #         elif sc.source == "manual":
    #             original_elements.append({
    #                 "type": "manual",
    #                 "command": sc.custom_command,
    #                 "replayed_from_id": sc.id
    #             })

    #     configs = self.db.query(Configuration).all()
    #     templates = self.db.query(Template).all()
    #     template_confs = self.db.query(TemplateConfiguration).all()

    #     new_group = self.create_group(
    #         execution=new_execution,
    #         name=original_group.name + " (Replay)",
    #         servers=original_servers,
    #         elements=original_elements,
    #         configs=configs,
    #         templates=templates,
    #         template_confs=template_confs,
    #         created_by=created_by,
    #         replayed_from_id=original_group.id
    #     )

    #     server_template_map = {}
    #     for sc in original_group.server_configurations:
    #         if sc.source == "template" and sc.server_template:
    #             st = self.create_server_template(
    #                 server_id=sc.server_id,
    #                 template_id=sc.server_template.template_id,
    #                 created_by=created_by,
    #                 replayed_from_id=sc.server_template.id
    #             )
    #             server_template_map[(sc.server_id, st.template_id)] = st.id

    #     self.create_server_configurations(
    #         group=new_group,
    #         servers=original_servers,
    #         elements=original_elements,
    #         created_by=created_by,
    #         server_template_map=server_template_map
    #     )

    #     logger.info(f"[Replay] Groupe ID={original_group_id} rejoué dans Exécution ID={new_execution.id}")
    #     return new_execution


    # def replay_server_template(self, original_id: int, created_by: Optional[int]) -> Execution:
    #     original = self.db.query(ServerTemplate).filter_by(id=original_id).first()
    #     if not original:
    #         raise ValueError("ServerTemplate not found")

    #     execution = self.create_execution(
    #         title=f"Replay ServerTemplate {original.id}",
    #         created_by=created_by,
    #         replayed_from_id=None
    #     )

    #     group = self.create_group(
    #         execution=execution,
    #         name=f"Replay ST {original.id}",
    #         servers=[original.server],
    #         elements=[{
    #             "type": "template",
    #             "id": original.template_id
    #         }],
    #         configs=[],
    #         templates=self.db.query(Template).all(),
    #         template_confs=self.db.query(TemplateConfiguration).all(),
    #         created_by=created_by
    #     )

    #     self.create_server_template(
    #         server_id=original.server_id,
    #         template_id=original.template_id,
    #         created_by=created_by,
    #         replayed_from_id=original.id
    #     )

    #     self.create_server_configurations(
    #         group=group,
    #         servers=[original.server],
    #         elements=[{
    #             "type": "template",
    #             "id": original.template_id
    #         }],
    #         created_by=created_by,
    #         server_template_map={(original.server_id, original.template_id): original.id}
    #     )

    #     return execution

    # def replay_server_configuration(self, original_id: int, created_by: Optional[int]) -> Execution:
    #     original = self.db.query(ServerConfiguration).filter_by(id=original_id).first()
    #     if not original:
    #         raise ValueError("ServerConfiguration not found")

    #     execution = self.create_execution(
    #         title=f"Replay ServerConfiguration {original.id}",
    #         created_by=created_by,
    #         replayed_from_id=None
    #     )

    #     group = self.create_group(
    #         execution=execution,
    #         name=f"Replay SC {original.id}",
    #         servers=[original.server],
    #         elements=[{
    #             "type": original.source,
    #             "id": original.configuration_id if original.source == "configuration" else None,
    #             "command": original.custom_command if original.source == "manual" else None
    #         }],
    #         configs=self.db.query(Configuration).all(),
    #         templates=self.db.query(Template).all(),
    #         template_confs=self.db.query(TemplateConfiguration).all(),
    #         created_by=created_by
    #     )

    #     self.create_server_configurations(
    #         group=group,
    #         servers=[original.server],
    #         elements=[{
    #             "type": original.source,
    #             "id": original.configuration_id if original.source == "configuration" else None,
    #             "command": original.custom_command if original.source == "manual" else None
    #         }],
    #         created_by=created_by
    #     )

    #     return execution

    async def create_and_launch_execution(
        self,
        title: Optional[str],
        groups_data: list[dict[str, Any]],
        created_by: Optional[int],
    ) -> Execution:
        """
        Crée une exécution complète + groupes + server_configurations + server_templates.
        Lance ensuite chaque groupe via Celery pour parallélisme.
        """
        execution = self.create_execution(title=title, created_by=created_by)

        configs = self.db.query(Configuration).all()
        templates = self.db.query(Template).all()
        template_confs = self.db.query(TemplateConfiguration).all()

        all_server_template_map = {}

        for group_data in groups_data:
            servers = group_data["servers"]
            elements = group_data["elements"]

            group = self.create_group(
                execution=execution,
                name=group_data.get("name"),
                servers=servers,
                elements=elements,
                configs=configs,
                templates=templates,
                template_confs=template_confs,
                created_by=created_by,
            )

            server_template_map = {}
            for server in servers:
                for el in elements:
                    if el["type"] == "template":
                        key = (server.id, el["id"])
                        if key not in all_server_template_map:
                            st = self.create_server_template(
                                server_id=server.id,
                                template_id=el["id"],
                                created_by=created_by
                            )
                            server_template_map[key] = st.id
                            all_server_template_map[key] = st.id
                        else:
                            server_template_map[key] = all_server_template_map[key]

            self.create_server_configurations(
                group=group,
                servers=servers,
                elements=elements,
                created_by=created_by,
                server_template_map=server_template_map
            )

        # Mise à jour status global
        execution.status = "running"
        execution.started_at = datetime.utcnow()
        self.db.commit()

        # Dispatch Celery pour chaque groupe
        from app.tasks.execution import run_group_task
        for group in execution.execution_groups:
            run_group_task.delay(group.id)

        logger.info(f"[Execution] ▶️ Tous les groupes dispatch Celery : Execution ID={execution.id}")

        return execution




