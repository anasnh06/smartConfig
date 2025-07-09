import yaml
from app.models.server import Server


def generate_inventory(servers: list[Server], inventory_path: str) -> None:
    """
    Génère un fichier inventory.ini Ansible correct.
    """
    with open(inventory_path, "w", newline="\n") as f:
        f.write("[all]\n")
        for server in servers:
            line = (
                f"server_{server.id} "
                f"ansible_host={server.ip_address} "
                f"ansible_port={server.ssh_port} "
                f"ansible_user={server.ssh_user} "
                f"ansible_ssh_private_key_file={server.ssh_private_key_path}\n"
            )
            f.write(line)

