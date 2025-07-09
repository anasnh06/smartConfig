from pathlib import Path

# Racine des fichiers générés (modifiable facilement en prod/dev)
BASE_DIR = Path("generated/executions")


def get_execution_dir(execution_id: int) -> Path:
    """
    Retourne le dossier pour une exécution donnée.
    Exemple : generated/executions/42/
    """
    return BASE_DIR / str(execution_id)


def get_group_dir(execution_id: int, group_id: int) -> Path:
    """
    Retourne le sous-dossier d’un groupe d’exécution donné.
    Exemple : generated/executions/42/group_7/
    """
    return get_execution_dir(execution_id) / f"group_{group_id}"


def get_inventory_path(execution_id: int, group_id: int) -> Path:
    """
    Chemin complet du fichier inventory généré pour ce groupe.
    Exemple : .../group_7/inventory.ini
    """
    return get_group_dir(execution_id, group_id) / "inventory.ini"


def get_playbook_path(execution_id: int, group_id: int) -> Path:
    """
    Chemin du fichier playbook.yml généré dynamiquement.
    """
    return get_group_dir(execution_id, group_id) / "playbook.yml"


def get_log_dir(execution_id: int, group_id: int) -> Path:
    """
    Dossier contenant les logs d'exécution pour ce groupe.
    Exemple : .../group_7/logs/
    """
    return get_group_dir(execution_id, group_id) / "logs"


def ensure_group_dirs_exist(execution_id: int, group_id: int) -> None:
    """
    S’assure que tous les dossiers nécessaires existent pour un groupe :
    dossier groupe, logs, etc.
    """
    get_log_dir(execution_id, group_id).mkdir(parents=True, exist_ok=True)


def get_group_log_path(execution_id: int, group_id: int) -> Path:
    """
    Retourne le chemin du fichier log global du groupe.
    Exemple : .../group_7/group.log
    """
    return get_group_dir(execution_id, group_id) / "group.log"



