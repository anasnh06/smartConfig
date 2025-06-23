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
    Génère un playbook Ansible complet et lisible.
    - Affichage explicite des IDs et noms
    - Nommage clair pour config, template→config, manuel
    """

    tasks = []

    # Index rapides
    config_map = {c.id: c for c in configs}
    template_map = {t.id: t for t in templates}
    template_conf_map: dict[int, list[TemplateConfiguration]] = {}
    for tc in template_confs:
        template_conf_map.setdefault(tc.template_id, []).append(tc)

    # Tri des éléments par `order`
    sorted_elements = sorted(elements, key=lambda e: (e.get("order") is None, e.get("order")))

    for element in sorted_elements:
        el_type = element.get("type")
        el_id = element.get("id")

        if el_type == "configuration":
            config = config_map.get(el_id)
            if not config:
                raise ValueError(f"❌ Configuration ID {el_id} introuvable.")
            task = {
                "name": f"[configuration:{config.id}] {config.name}",
                "shell": config.command,
            }
            if config.description:
                task["tags"] = [config.description]
            tasks.append(task)

        elif el_type == "template":
            template = template_map.get(el_id)
            if not template:
                raise ValueError(f"❌ Template ID {el_id} introuvable.")
            template_tasks = template_conf_map.get(template.id, [])
            template_tasks_sorted = sorted(template_tasks, key=lambda c: (c.order is None, c.order))

            for tc in template_tasks_sorted:
                config = config_map.get(tc.configuration_id)
                if not config:
                    raise ValueError(f"❌ Config ID {tc.configuration_id} introuvable dans Template {template.id}.")
                task_name = (
                    f"[template:{template.id}] {template.name} → "
                    f"[configuration:{config.id}] {config.name}"
                )
                if tc.comment:
                    task_name += f" - {tc.comment}"
                task = {
                    "name": task_name,
                    "shell": config.command,
                }
                if config.description:
                    task["tags"] = [config.description]
                tasks.append(task)

        elif el_type == "manual":
            command_str = element.get("command", "").strip()
            if not command_str:
                raise ValueError("❌ Commande manuelle vide.")
            custom_name = element.get("name") or "Commande personnalisée"
            task = {
                "name": f"[manual] {custom_name}",
                "shell": command_str,
            }
            if desc := element.get("description"):
                task["tags"] = [desc]
            tasks.append(task)

        else:
            raise ValueError(f"❌ Type d'élément inconnu : {el_type}")

    # Nom global du playbook
    if group_id is not None:
        playbook_title = f"Group {group_id}"
        if group_name:
            playbook_title += f" - {group_name.strip()}"
    else:
        playbook_title = group_name.strip() if group_name else "Unnamed Group"

    playbook = [
        {
            "name": playbook_title,
            "hosts": "all",
            "gather_facts": False,
            "tasks": tasks,
        }
    ]

    # Écriture du fichier YAML
    with open(playbook_path, "w") as f:
        yaml.dump(playbook, f, sort_keys=False)
