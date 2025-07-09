from pathlib import Path
from typing import Any, Optional
import yaml

from app.models.configuration import Configuration
from app.models.template import Template
from app.models.template_configuration import TemplateConfiguration

def generate_playbook(
    elements: list[dict[str, Any]],
    configs: list[Configuration],
    templates: list[Template],
    template_confs: list[TemplateConfiguration],
    playbook_path: Path,
    group_name: Optional[str] = None,
    group_id: Optional[int] = None,
) -> None:
    """
    Génère un playbook Ansible unique pour le groupe,
    permettant de récupérer stdout/stderr par SC.
    """
    tasks = []
    config_map = {c.id: c for c in configs}
    template_map = {t.id: t for t in templates}
    template_conf_map: dict[int, list[TemplateConfiguration]] = {}
    for tc in template_confs:
        template_conf_map.setdefault(tc.template_id, []).append(tc)

    sorted_elements = sorted(elements, key=lambda e: (e.get("order") is None, e.get("order")))

    sc_idx = 0

    for element in sorted_elements:
        el_type = element.get("type")
        el_id = element.get("id")

        if el_type == "configuration":
            config = config_map.get(el_id)
            if not config:
                raise ValueError(f"❌ Configuration ID {el_id} introuvable.")
            sc_idx += 1
            task_name = f"[configuration:{config.id}] {config.name}"
            tasks.append({
                "name": task_name,
                "shell": config.command,
                "register": f"result_{sc_idx}",
                "tags": [f"sc_config_{config.id}"]
            })
            tasks.append({
                "debug": {"var": f"result_{sc_idx}"}
            })

        elif el_type == "manual":
            command_str = element.get("command", "").strip()
            if not command_str:
                raise ValueError("❌ Commande manuelle vide.")
            sc_idx += 1
            custom_name = element.get("name") or "Commande personnalisée"
            task_name = f"[manual] {custom_name}"
            tasks.append({
                "name": task_name,
                "shell": command_str,
                "register": f"result_{sc_idx}",
                "tags": [f"sc_manual_{sc_idx}"]
            })
            tasks.append({
                "debug": {"var": f"result_{sc_idx}"}
            })

        elif el_type == "template":
            template = template_map.get(el_id)
            if not template:
                raise ValueError(f"❌ Template ID {el_id} introuvable.")
            template_tasks = sorted(template_conf_map.get(template.id, []), key=lambda c: (c.order is None, c.order))

            for tc in template_tasks:
                config = config_map.get(tc.configuration_id)
                if not config:
                    raise ValueError(f"❌ Config ID {tc.configuration_id} introuvable dans Template {template.id}.")
                sc_idx += 1
                task_name = (
                    f"[template:{template.id}] {template.name} → "
                    f"[configuration:{config.id}] {config.name}"
                )
                if tc.comment:
                    task_name += f" - {tc.comment}"

                tasks.append({
                    "name": task_name,
                    "shell": config.command,
                    "register": f"result_{sc_idx}",
                    "tags": [f"sc_template_{template.id}_{config.id}"]
                })
                tasks.append({
                    "debug": {"var": f"result_{sc_idx}"}
                })

        else:
            raise ValueError(f"❌ Type d'élément inconnu : {el_type}")

    playbook_title = f"Group {group_id}" if group_id else group_name or "Unnamed Group"

    playbook = [{
        "name": playbook_title,
        "hosts": "all",
        "gather_facts": False,
        "tasks": tasks,
    }]

    with open(playbook_path, "w", encoding="utf-8", newline="\n") as f:
        yaml.dump(playbook, f, sort_keys=False)
