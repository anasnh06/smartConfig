from pathlib import Path
from app.ansible_runner.paths import ensure_group_dirs_exist, get_playbook_path
from app.ansible_runner.playbook_generator import generate_playbook
from app.models.configuration import Configuration
from app.models.template import Template
from app.models.template_configuration import TemplateConfiguration

# === 1️⃣ Données factices ===

config1 = Configuration(id=1, name="Install Nginx", command="apt install nginx -y", description="Installer nginx")
config2 = Configuration(id=2, name="Start Nginx", command="systemctl start nginx", description="Démarrer nginx")
config3 = Configuration(id=3, name="Echo Hello", command="echo Hello", description=None)

template1 = Template(id=1, name="Web Template")

tc1 = TemplateConfiguration(template_id=1, configuration_id=1, order=2, comment="Installer proprement")
tc2 = TemplateConfiguration(template_id=1, configuration_id=2, order=3, comment="Démarrer le service")

# === 2️⃣ Scénario mixte ===

elements = [
    {"type": "manual", "command": "uptime", "name": "Uptime Check", "order": 1, "description": "Afficher uptime"},
    {"type": "configuration", "id": 3, "order": 2},
    {"type": "template", "id": 1, "order": 3},
    {"type": "manual", "command": "df -h", "order": 4},
]

# === 3️⃣ Identifiants de test ===

execution_id = 1
group_id = 1

# === 4️⃣ Création des dossiers nécessaires ===

ensure_group_dirs_exist(execution_id, group_id)

# === 5️⃣ Génération du fichier playbook ===

playbook_path = get_playbook_path(execution_id, group_id)

generate_playbook(
    elements=elements,
    configs=[config1, config2, config3],
    templates=[template1],
    template_confs=[tc1, tc2],
    playbook_path=playbook_path,
    group_name="Test Group",
    group_id=group_id
)

print(f"✅ Playbook généré ici : {playbook_path.resolve()}")

# === 6️⃣ Affichage direct du contenu pour vérification ===

print("\n=== Contenu du playbook généré ===\n")
print(playbook_path.read_text(encoding="utf-8"))
