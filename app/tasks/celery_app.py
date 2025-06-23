from celery import Celery

# Création de l'application Celery avec un nom unique
celery_app = Celery("smartconfig_execution")

# Configuration de base (le broker Redis doit être lancé sur ce port/local)
celery_app.conf.broker_url = "redis://localhost:6379/0"
celery_app.conf.result_backend = "redis://localhost:6379/0"

# Acceptation uniquement des contenus JSON
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"

# Optionnel : timezone pour logs/cohérence
celery_app.conf.timezone = "UTC"
