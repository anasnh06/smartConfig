from __future__ import annotations
import json
import os
from typing import Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from pathlib import Path
import asyncio
import logging
from redis.asyncio import Redis
from app.core.redis import get_redis_client

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

logger = logging.getLogger(__name__)

class ExecutionRunnerService:
    def __init__(self, db: Session):
        self.db = db
        self.redis: Optional[Redis] = None

    async def ensure_redis(self):
        if self.redis is None:
            from app.core.redis import get_redis_client
            self.redis = get_redis_client()

    async def notify(self, execution_id: int, payload: dict):
        await self.ensure_redis()
        await self.redis.publish(f"execution:{execution_id}", json.dumps(payload))
        logger.info(f"[REDIS] 📤 Publié sur execution:{execution_id} → {payload}")
        await manager.broadcast_json(execution_id, payload)

    def create_execution(self, title: Optional[str], created_by: Optional[int]) -> Execution:
        execution = Execution(title=title, created_by=created_by)
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        logger.info(f"[Execution] ➕ Créée : ID={execution.id}")
        return execution

    def create_group(self, execution: Execution, name: Optional[str], servers: list[Server], elements: list[dict[str, Any]], configs: list[Configuration], templates: list[Template], template_confs: list[TemplateConfiguration], created_by: Optional[int]) -> ExecutionGroup:
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

    def create_server_template(self, server_id: int, template_id: int, created_by: Optional[int]) -> ServerTemplate:
        st = ServerTemplate(server_id=server_id, template_id=template_id, created_by=created_by)
        self.db.add(st)
        self.db.commit()
        self.db.refresh(st)
        logger.info(f"[ServerTemplate] ➕ Server={server_id} → Template={template_id} (ID={st.id})")
        return st

    def create_server_configurations(self, group: ExecutionGroup, servers: list[Server], elements: list[dict[str, Any]], created_by: Optional[int], server_template_map: Optional[dict[tuple[int, int], int]] = None) -> list[ServerConfiguration]:
        server_confs: list[ServerConfiguration] = []
        template_conf_map: dict[int, list[TemplateConfiguration]] = {}
        for tc in self.db.query(TemplateConfiguration).all():
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
                elif el_type == "manual":
                    sc = ServerConfiguration(
                        server_id=server.id,
                        execution_group_id=group.id,
                        created_by=created_by,
                        status="pending",
                        source="manual",
                        custom_command=element.get("command", "").strip()
                    )
                elif el_type == "template":
                    st_id = server_template_map.get((server.id, el_id)) if server_template_map else None
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
                        continue
                    continue
                else:
                    continue
                self.db.add(sc)
                server_confs.append(sc)

        self.db.commit()
        logger.info(f"[ServerConfigurations] ➕ {len(server_confs)} créés pour Group={group.id}")
        return server_confs

    async def launch_group(self, group_id: int) -> None:
        group = self.db.query(ExecutionGroup).filter_by(id=group_id).first()
        if not group:
            logger.error(f"[ExecutionGroup] ❌ Introuvable : ID={group_id}")
            return

        execution = group.execution
        group.status = "running"
        group.started_at = datetime.now(timezone.utc)
        self.db.commit()
        logger.info(f"[ExecutionGroup] ▶️ Lancement : ID={group.id}")

        playbook_path = Path(group.playbook_path)
        inventory_path = Path(group.inventory_path)
        group_log_path = get_group_log_path(execution.id, group.id)

        cmd = ["ansible-playbook", str(playbook_path), "-i", str(inventory_path), "-e", "ansible_python_interpreter=/usr/bin/python3"]
        env = os.environ.copy()
        env["ANSIBLE_STDOUT_CALLBACK"] = "json"

        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, env=env)
        stdout_bytes, _ = await process.communicate()
        stdout = stdout_bytes.decode()

        group_log_path.write_text(stdout, encoding="utf-8")
        # Ajout : notification du stdout du groupe via WebSocket
        await self.notify(execution.id, {
            "event": "group_stdout",
            "group_id": group.id,
            "stdout": stdout,
        })

        if process.returncode != 0:
            group.status = "failed"
            group.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            return

        try:
            result_json = json.loads(stdout)
        except json.JSONDecodeError:
            group.status = "failed"
            group.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            return

        sc_list = sorted(group.server_configurations, key=lambda sc: sc.id)
        result_counter = 0

        for play in result_json.get("plays", []):
            for task in play.get("tasks", []):
                for host_result in task.get("hosts", {}).values():
                    if result_counter >= len(sc_list):
                        continue
                    sc = sc_list[result_counter]
                    sc.return_code = host_result.get("rc")
                    sc.stdout = host_result.get("stdout", "")
                    sc.stderr = host_result.get("stderr", "")
                    sc.status = "success" if sc.return_code == 0 else "failed"
                    sc.started_at = group.started_at
                    sc.finished_at = datetime.now(timezone.utc)

                    log_dir = get_log_dir(execution.id, group.id)
                    log_file = log_dir / f"server_{sc.server_id}_sc_{sc.id}.log"
                    log_file.write_text(
                        f"=== STDOUT ===\n{sc.stdout}\n=== STDERR ===\n{sc.stderr}\n=== RC ===\n{sc.return_code}\n",
                        encoding="utf-8"
                    )
                    sc.log_path = str(log_file)
                    self.db.commit()

                    await self.notify(execution.id, {
                        "event": "server_config_update",
                        "group_id": group.id,
                        "server_config_id": sc.id,
                        "server_id": sc.server.id,
                        "status": sc.status,
                        "return_code": sc.return_code,
                        "finished_at": sc.finished_at.isoformat(),
                    })
                    result_counter += 1

        group.finished_at = datetime.now(timezone.utc)
        self.update_group_status(group.id)
        self.update_server_template_statuses(group)
        self.update_execution_status(execution.id)

        await self.notify(execution.id, {
            "event": "group_finished",
            "group_id": group.id,
            "status": group.status,
        })

    async def launch_execution(self, execution_id: int) -> None:
        execution = self.db.query(Execution).filter_by(id=execution_id).first()
        if not execution:
            return

        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        self.db.commit()

        for group in execution.execution_groups:
            await self.launch_group(group.id)

        self.update_execution_status(execution.id)
        await self.notify(execution.id, {
            "event": "execution_status_update",
            "execution_id": execution.id,
            "status": execution.status,
        })

    def update_group_status(self, group_id: int) -> None:
        group = self.db.query(ExecutionGroup).filter_by(id=group_id).first()
        if not group:
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

    def update_execution_status(self, execution_id: int) -> None:
        execution = self.db.query(Execution).filter_by(id=execution_id).first()
        if not execution:
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

    def update_server_template_statuses(self, group: ExecutionGroup) -> None:
        template_map: dict[int, list[ServerConfiguration]] = {}
        for sc in group.server_configurations:
            if sc.server_template_id:
                template_map.setdefault(sc.server_template_id, []).append(sc)

        for st_id, scs in template_map.items():
            st = self.db.query(ServerTemplate).filter_by(id=st_id).first()
            if not st:
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

    async def create_and_launch_execution(self, title: Optional[str], groups_data: list[dict[str, Any]], created_by: Optional[int]) -> Execution:
        execution = self.create_execution(title=title, created_by=created_by)

        configs = self.db.query(Configuration).all()
        templates = self.db.query(Template).all()
        template_confs = self.db.query(TemplateConfiguration).all()

        all_server_template_map: dict[tuple[int, int], int] = {}

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

        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        self.db.commit()

        from app.tasks.execution import run_group_task
        for group in execution.execution_groups:
            run_group_task.delay(group.id)
            logger.info(f"[Execution] 🚀 Dispatch Celery: Group ID={group.id} dans Execution ID={execution.id}")

        logger.info(f"[Execution] ✅ Créée et lancée via Celery : Execution ID={execution.id}")
        # Ajout : notification WebSocket du démarrage de l'exécution
        await self.notify(execution.id, {
            "event": "execution_status_update",
            "execution_id": execution.id,
            "status": execution.status,
        })
        return execution
