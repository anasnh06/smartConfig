import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Charger les variables d’environnement
from dotenv import load_dotenv

from app.db import Base, engine
load_dotenv()

# Inclure le chemin racine du projet pour les imports absolus
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modèles pour qu'Alembic détecte Base.metadata
# Remplacer l'import global par un import différé pour éviter les problèmes de circularité
def include_models():
    import app.models
# Alembic config
config = context.config

# Configurer le logging si un fichier est défini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Cibler le metadata pour la génération des migrations
target_metadata = Base.metadata

# Récupérer l'URL de la base depuis .env
DATABASE_URL = os.getenv("DATABASE_URL")

def run_migrations_offline() -> None:
    """Exécute les migrations en mode 'offline' (sans DB connectée)."""
    include_models()  # Charger les modèles avant de configurer Alembic
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Exécute les migrations en mode 'online' (avec DB connectée)."""
    include_models()  # Charger les modèles avant de configurer Alembic
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

# Déterminer si l'on est en mode offline ou online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
