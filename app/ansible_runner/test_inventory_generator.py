from app.ansible_runner.paths import get_inventory_path, ensure_group_dirs_exist
from app.ansible_runner.inventory_generator import generate_inventory
from app.models.server import Server


# Données fictives pour test
server1 = Server(
    id=1,
    name="server-1",
    ip_address="192.168.1.10",
    ssh_port=22,
    ssh_user="root",
    ssh_private_key_path="/home/nouhassi/.ssh/id_rsa",
    operating_system_id=1,
    environment_id=1,
    project_id=1,
)

server2 = Server(
    id=2,
    name="server-2",
    ip_address="192.168.1.11",
    ssh_port=22,
    ssh_user="admin",
    ssh_private_key_path="/home/nouhassi/.ssh/id_rsa",
    operating_system_id=1,
    environment_id=1,
    project_id=1,
)

# ID fictifs pour test
execution_id = 1
group_id = 1

# Création des dossiers requis
ensure_group_dirs_exist(execution_id, group_id)

# Génération de l'inventory
inventory_path = get_inventory_path(execution_id, group_id)
generate_inventory([server1, server2], str(inventory_path))

print(f"Inventory YAML créé ici : {inventory_path.resolve()}")
