from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ServerConfigurationService

def get_server_configuration_service(db: Session = Depends(get_db)) -> ServerConfigurationService:
    return ServerConfigurationService(db)
