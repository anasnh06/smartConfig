from __future__ import annotations
import os
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
    ensure_group_dirs_exist, get_log_dir, get_group_log_path
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
    ) -> Execution:
        """
        Crée une exécution avec titre et traçabilité.
        """
        execution = Execution(
            title=title,
            created_by=created_by,
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
    ) -> ExecutionGroup:
        """
        Crée un groupe avec inventaire et playbook générés proprement.
        """
        group = ExecutionGroup(
            execution_id=execution.id,
            name=name or f"group_{len(execution.execution_groups) + 1}",
            created_by=created_by,
            status="pending"
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

        logger.info(f"[ExecutionGroup] ➕ Créé : ID={group.id} pour Execution={execution.id}")
        return group


    def create_server_template(
        self,
        server_id: int,
        template_id: int,
        created_by: Optional[int],
    ) -> ServerTemplate:
        """
        Crée et trace un ServerTemplate (server-template).
        """
        st = ServerTemplate(
            server_id=server_id,
            template_id=template_id,
            created_by=created_by,
        )
        self.db.add(st)
        self.db.commit()
        self.db.refresh(st)
        logger.info(f"[ServerTemplate] ➕ Server={server_id} → Template={template_id} (ID={st.id})")
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
        Crée tous les ServerConfigurations du groupe avec granularité par configuration,
        même lors d'exécution via Template.
        """
        server_confs: list[ServerConfiguration] = []

        # Construction map rapide Template → [TemplateConfiguration]
        template_conf_map: dict[int, list[TemplateConfiguration]] = {}
        template_confs = self.db.query(TemplateConfiguration).all()
        for tc in template_confs:
            template_conf_map.setdefault(tc.template_id, []).append(tc)

        for server in servers:
            for element in elements:
                el_type = element.get("type")
                el_id = element.get("id")

                if el_type == "configuration":
                    sc = ServerConfiguration(
                        server_id=server.id,
                        execution_group_id=group.id,
                        created_by=created_by,
                        status="pending",
                        source="configuration",
                        configuration_id=el_id
                    )
                    self.db.add(sc)
                    server_confs.append(sc)
                    logger.info(
                        f"[ServerConfig] ➕ Conf directe : SC_ID={sc.id} | Server={server.id} | Conf={el_id}"
                    )

                elif el_type == "manual":
                    sc = ServerConfiguration(
                        server_id=server.id,
                        execution_group_id=group.id,
                        created_by=created_by,
                        status="pending",
                        source="manual",
                        custom_command=element.get("command", "").strip()
                    )
                    self.db.add(sc)
                    server_confs.append(sc)
                    logger.info(
                        f"[ServerConfig] ➕ Manual : SC_ID={sc.id} | Server={server.id}"
                    )

                elif el_type == "template":
                    # Récupération server_template_id pour trace
                    st_id = None
                    if server_template_map:
                        key = (server.id, el_id)
                        st_id = server_template_map.get(key)

                    # Créer un SC par configuration dans le template
                    for tc in sorted(template_conf_map.get(el_id, []), key=lambda c: (c.order is None, c.order)):
                        sc = ServerConfiguration(
                            server_id=server.id,
                            execution_group_id=group.id,
                            created_by=created_by,
                            status="pending",
                            source="template",
                            server_template_id=st_id,
                            configuration_id=tc.configuration_id
                        )
                        self.db.add(sc)
                        server_confs.append(sc)
                        logger.info(
                            f"[ServerConfig] ➕ Template : SC_ID={sc.id} | Server={server.id} | "
                            f"Template={el_id} | Conf={tc.configuration_id} | ST_ID={st_id}"
                        )

        self.db.commit()
        logger.info(f"[ServerConfigurations] ➕ {len(server_confs)} créés pour Group={group.id}")
        return server_confs




    async def launch_group(self, group_id: int) -> None:
        """
        Exécute le playbook unique du groupe en utilisant le callback JSON,
        parse le résultat JSON, met à jour la DB pour chaque SC,
        génère un log individuel SC, et envoie les WS de suivi.
        """
        import json

        group = self.db.query(ExecutionGroup).filter_by(id=group_id).first()
        if not group:
            logger.error(f"[ExecutionGroup] ❌ Introuvable : ID={group_id}")
            return

        execution = group.execution
        group.status = "running"
        group.started_at = datetime.utcnow()
        self.db.commit()

        playbook_path = Path(group.playbook_path)
        inventory_path = Path(group.inventory_path)
        group_log_path = get_group_log_path(execution.id, group.id)

        cmd = [
            "ansible-playbook",
            str(playbook_path),
            "-i", str(inventory_path),
            "-e", "ansible_python_interpreter=/usr/bin/python3"
        ]

        env = os.environ.copy()
        env["ANSIBLE_STDOUT_CALLBACK"] = "json"

        # Exécution en récupérant le JSON complet
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
            text=True
        )
        stdout, _ = await process.communicate()

        # Sauvegarde le log global
        group_log_path.write_text(stdout, encoding="utf-8")

        try:
            result_json = json.loads(stdout)
        except json.JSONDecodeError as e:
            logger.exception(f"[ExecutionGroup] ❌ JSON decode failed: {e}")
            group.status = "failed"
            group.finished_at = datetime.utcnow()
            self.db.commit()
            return

        sc_list_sorted = sorted(group.server_configurations, key=lambda sc: sc.id)
        result_counter = 0

        for play in result_json.get("plays", []):
            for task in play.get("tasks", []):
                for host, host_result in task.get("hosts", {}).items():
                    # Nous récupérons uniquement les résultats shell/debug contenant stdout/rc
                    if "stdout" in host_result and "rc" in host_result:
                        if result_counter >= len(sc_list_sorted):
                            logger.warning(f"[ExecutionGroup] Résultat en trop, SC manquant. Ignoré.")
                            continue

                        sc = sc_list_sorted[result_counter]
                        sc.return_code = host_result.get("rc")
                        sc.stdout = host_result.get("stdout", "")
                        sc.stderr = host_result.get("stderr", "")
                        sc.status = "success" if sc.return_code == 0 else "failed"
                        sc.finished_at = datetime.utcnow()

                        # Créer le log individuel SC
                        log_dir = get_log_dir(execution.id, group.id)
                        log_file = log_dir / f"server_{sc.server_id}_sc_{sc.id}.log"
                        log_content = (
                            f"Server ID: {sc.server_id}\n"
                            f"Configuration ID: {sc.configuration_id or 'N/A'}\n"
                            f"ServerConfiguration ID: {sc.id}\n"
                            f"=== STDOUT ===\n{sc.stdout}\n"
                            f"=== STDERR ===\n{sc.stderr}\n"
                            f"=== RC ===\n{sc.return_code}\n"
                        )
                        log_file.write_text(log_content, encoding="utf-8")
                        sc.log_path = str(log_file)

                        self.db.commit()

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

                        result_counter += 1

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

        logger.info(f"[ExecutionGroup] ✅ Terminé : ID={group.id} → {group.status}")




    async def launch_execution(self, execution_id: int) -> None:
        """
        Lance tous les groupes d'une exécution séquentiellement.
        """
        execution = self.db.query(Execution).filter_by(id=execution_id).first()
        if not execution:
            logger.error(f"[Execution] ❌ Introuvable : ID={execution_id}")
            return

        execution.status = "running"
        execution.started_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"[Execution] ▶️ Lancement Execution ID={execution.id}")

        for group in execution.execution_groups:
            await self.launch_group(group.id)

        # Final WS update
        self.update_execution_status(execution.id)
        await manager.broadcast_json(execution.id, {
            "event": "execution_status_update",
            "execution_id": execution.id,
            "status": execution.status,
        })

        logger.info(f"[Execution] ✅ Tous les groupes terminés pour Execution ID={execution.id} → {execution.status}")


    def update_group_status(self, group_id: int) -> None:
        """
        Met à jour le statut du groupe selon les ServerConfigurations associées.
        """
        group = self.db.query(ExecutionGroup).filter_by(id=group_id).first()
        if not group:
            logger.error(f"[Group] ❌ Inexistant : ID={group_id}")
            return

        statuses = [sc.status for sc in group.server_configurations if sc.status]

        if not statuses:
            group.status = "pending"
        elif all(s == "success" for s in statuses):
            group.status = "success"
        elif any(s == "running" for s in statuses):
            group.status = "running"
        elif any(s == "success" for s in statuses):
            group.status = "partial"
        elif all(s == "failed" for s in statuses):
            group.status = "failed"
        else:
            group.status = "partial"

        group.started_at = min((sc.started_at for sc in group.server_configurations if sc.started_at), default=None)
        group.finished_at = max((sc.finished_at for sc in group.server_configurations if sc.finished_at), default=None)
        self.db.commit()

        logger.info(f"[Group] 🔁 ID={group.id} Statut mis à jour → {group.status}")


    def update_execution_status(self, execution_id: int) -> None:
        """
        Met à jour le statut de l'exécution en fonction de ses groupes associés.
        """
        execution = self.db.query(Execution).filter_by(id=execution_id).first()
        if not execution:
            logger.error(f"[Execution] ❌ Inexistant : ID={execution_id}")
            return

        statuses = [g.status for g in execution.execution_groups if g.status]

        if not statuses:
            execution.status = "pending"
        elif any(s == "running" for s in statuses):
            execution.status = "running"
        elif all(s == "success" for s in statuses):
            execution.status = "success"
        elif any(s == "success" for s in statuses):
            execution.status = "partial"
        elif all(s == "failed" for s in statuses):
            execution.status = "failed"
        else:
            execution.status = "partial"

        execution.started_at = min((g.started_at for g in execution.execution_groups if g.started_at), default=None)
        execution.finished_at = max((g.finished_at for g in execution.execution_groups if g.finished_at), default=None)
        self.db.commit()

        logger.info(f"[Execution] 🔁 ID={execution.id} Statut mis à jour → {execution.status}")


    def update_server_template_statuses(self, group: ExecutionGroup) -> None:
        """
        Met à jour le statut de chaque ServerTemplate lié aux ServerConfigurations du groupe.
        """
        # Mapping ServerTemplate ID → ServerConfigurations associées
        template_map: dict[int, list[ServerConfiguration]] = {}
        for sc in group.server_configurations:
            if sc.server_template_id:
                template_map.setdefault(sc.server_template_id, []).append(sc)

        for st_id, scs in template_map.items():
            st = self.db.query(ServerTemplate).filter_by(id=st_id).first()
            if not st:
                logger.warning(f"[ServerTemplate] ⚠️ Introuvable : ID={st_id}")
                continue

            statuses = [sc.status for sc in scs if sc.status]

            if not statuses:
                st.status = "pending"
            elif all(s == "success" for s in statuses):
                st.status = "success"
            elif any(s == "running" for s in statuses):
                st.status = "running"
            elif any(s == "success" for s in statuses):
                st.status = "partial"
            elif all(s == "failed" for s in statuses):
                st.status = "failed"
            else:
                st.status = "partial"

            self.db.commit()
            logger.info(f"[ServerTemplate] 🔁 Statut mis à jour : ID={st.id} → {st.status}")



    async def create_and_launch_execution(
        self,
        title: Optional[str],
        groups_data: list[dict[str, Any]],
        created_by: Optional[int],
    ) -> Execution:
        """
        Crée une exécution complète avec ses groupes, server_configurations et server_templates,
        puis lance chaque groupe via Celery en parallèle.
        """
        # 1️⃣ Création de l'exécution
        execution = self.create_execution(title=title, created_by=created_by)

        # 2️⃣ Préchargement des données nécessaires
        configs = self.db.query(Configuration).all()
        templates = self.db.query(Template).all()
        template_confs = self.db.query(TemplateConfiguration).all()

        # Pour éviter duplications ServerTemplate
        all_server_template_map: dict[tuple[int, int], int] = {}

        # 3️⃣ Création des groupes, server_templates et server_configurations
        for group_data in groups_data:
            server_ids = [s["id"] for s in group_data["servers"]]
            servers = self.db.query(Server).filter(Server.id.in_(server_ids)).all()
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

            server_template_map: dict[tuple[int, int], int] = {}

            for server in servers:
                for el in elements:
                    if el["type"] == "template":
                        key = (server.id, el["id"])
                        if key not in all_server_template_map:
                            st = self.create_server_template(
                                server_id=server.id,
                                template_id=el["id"],
                                created_by=created_by,
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
                server_template_map=server_template_map,
            )

        # 4️⃣ Marquer l'exécution comme "running"
        execution.status = "running"
        execution.started_at = datetime.utcnow()
        self.db.commit()

        # 5️⃣ Dispatch Celery par groupe
        from app.tasks.execution import run_group_task

        for group in execution.execution_groups:
            run_group_task.delay(group.id)
            logger.info(f"[Execution] 🚀 Dispatch Celery: Group ID={group.id} dans Execution ID={execution.id}")

        logger.info(f"[Execution] ✅ Créée et lancée via Celery : Execution ID={execution.id}")

        return execution




    