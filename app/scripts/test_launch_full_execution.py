import requests

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
LAUNCH_ENDPOINT = f"{BASE_URL}/api/v1/execution-runners/launch/full"

# 1️⃣ Login automatique avec ton user
login_data = {
    "username": "anas",
    "password": "anas1234"
}

try:
    login_response = requests.post(LOGIN_ENDPOINT, data=login_data)
    login_response.raise_for_status()
    token_data = login_response.json()
    ACCESS_TOKEN = token_data["access_token"]
    print("✅ Connexion réussie, token récupéré.")
except requests.exceptions.RequestException as e:
    print("❌ Erreur lors de la connexion :", e)
    if e.response is not None:
        print("➡️ Status Code:", e.response.status_code)
        print("➡️ Response:", e.response.text)
    exit(1)

# 2️⃣ Construction du payload de test
data = {
    "title": "🧪 Test Full Execution Backend",
    "groups": [
        {
            "name": "Groupe Configurations Directes",
            "servers": [{"id": 1}],
            "elements": [
                {"type": "configuration", "id": 4, "order": 1},
                {"type": "configuration", "id": 5, "order": 2},
                {"type": "configuration", "id": 6, "order": 3}
            ]
        },
        {
            "name": "Groupe Mixte avec Template",
            "servers": [{"id": 1}],
            "elements": [
                {"type": "manual", "command": "echo 'Hello from manual test'", "name": "Echo Test", "description": "Test echo", "order": 1},
                {"type": "configuration", "id": 4, "order": 2},
                {"type": "template", "id": 4, "order": 3},
                {"type": "manual", "command": "uptime", "name": "Check Uptime", "order": 4}
            ]
        }
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# 3️⃣ Lancement de l'exécution
try:
    response = requests.post(LAUNCH_ENDPOINT, json=data, headers=headers)
    response.raise_for_status()
    print("✅ Exécution lancée avec succès.")
    print("➡️ Status Code:", response.status_code)
    print("➡️ Response:", response.json())
except requests.exceptions.RequestException as e:
    print("❌ Erreur lors du lancement de l'exécution :", e)
    if e.response is not None:
        print("➡️ Status Code:", e.response.status_code)
        print("➡️ Response:", e.response.text)
