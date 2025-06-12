import yaml
from app.models.server import Server


def generate_inventory(servers: list[Server], inventory_path: str) -> None:
    """
    Génère un fichier inventory.yml Ansible à partir d'une liste de serveurs.
    """
    inventory = {
        "all": {
            "hosts": {},
        }
    }

    for server in servers:
        inventory["all"]["hosts"][server.name] = {
            "ansible_host": server.ip_address,
            "ansible_port": server.ssh_port,
            "ansible_user": server.ssh_user,
            "ansible_ssh_private_key_file": server.ssh_private_key_path,
        }

    # Écriture dans le fichier YAML
    with open(inventory_path, "w") as f:
        yaml.dump(inventory, f, sort_keys=False)
