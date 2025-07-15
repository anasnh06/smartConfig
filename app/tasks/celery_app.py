from celery import Celery
from app.core import settings

# Création de l'application Celery avec un nom unique
celery_app = Celery("smartconfig_execution")

# Configuration de base (le broker Redis doit être lancé sur ce port/local)
celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url

# Acceptation uniquement des contenus JSON
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"

# Optionnel : timezone pour logs/cohérence
celery_app.conf.timezone = "UTC"


