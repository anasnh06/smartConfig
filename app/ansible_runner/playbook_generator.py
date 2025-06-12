from pathlib import Path
from typing import Any, Optional
import yaml

from app.models.configuration import Configuration
from app.models.template import Template
from app.models.template_configuration import TemplateConfiguration


def generate_playbook(
    elements: list[dict[str, Any]],  # Chaque dict contient: type, id, order (optionnel), name (optionnel), command, description
    configs: list[Configuration],
    templates: list[Template],
    template_confs: list[TemplateConfiguration],
    playbook_path: Path,
    group_name: Optional[str] = None,
    group_id: Optional[int] = None,
) -> None:
    """
    Génère un playbook Ansible avec les éléments triés (config, template, manuel).
    - Ajoute les tags depuis les descriptions (config, manuel)
    - Gère les noms explicites avec fallback
    - Inclut les commentaires TemplateConfiguration dans le nom
    """

    tasks = []

    # Index pour accès rapide
    config_map = {c.id: c for c in configs}
    template_map = {t.id: t for t in templates}
    template_conf_map: dict[int, list[TemplateConfiguration]] = {}
    for tc in template_confs:
        template_conf_map.setdefault(tc.template_id, []).append(tc)

    # Trier tous les éléments principaux
    sorted_elements = sorted(elements, key=lambda e: (e.get("order") is None, e.get("order")))

    for element in sorted_elements:
        el_type = element.get("type")
        el_id = element.get("id")

        if el_type == "configuration":
            if el_id not in config_map:
                raise ValueError(f"❌ Configuration ID {el_id} introuvable.")
            config = config_map[el_id]
            task = {
                "name": f"[config:{config.id}] {config.name}",
                "shell": config.command,
            }
            if getattr(config, "description", None):
                task["tags"] = [config.description]
            tasks.append(task)

        elif el_type == "template":
            if el_id not in template_map:
                raise ValueError(f"❌ Template ID {el_id} introuvable.")
            template = template_map[el_id]
            template_tasks = template_conf_map.get(template.id, [])
            template_tasks_sorted = sorted(template_tasks, key=lambda c: (c.order is None, c.order))

            for tc in template_tasks_sorted:
                config = config_map.get(tc.configuration_id)
                if not config:
                    raise ValueError(f"❌ Config ID {tc.configuration_id} introuvable dans Template {template.id}.")
                task_name = f"[template:{template.id}] {config.name}"
                if tc.comment:
                    task_name += f" - {tc.comment}"
                task = {
                    "name": task_name,
                    "shell": config.command,
                }
                if getattr(config, "description", None):
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
    playbook_title = group_name.strip() if group_name else f"Group {group_id if group_id is not None else 'Unknown'}"

    playbook = [
        {
            "name": playbook_title,
            "hosts": "all",
            "gather_facts": False,
            "tasks": tasks,
        }
    ]

    # Écriture fichier
    with open(playbook_path, "w") as f:
        yaml.dump(playbook, f, sort_keys=False)
