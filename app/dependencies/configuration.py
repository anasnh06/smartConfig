from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ConfigurationService


def get_configuration_service(db: Session = Depends(get_db)) -> ConfigurationService:
    """
    🧩 Fournit une instance de ConfigurationService injectée avec la session DB.
    """
    return ConfigurationService(db)
