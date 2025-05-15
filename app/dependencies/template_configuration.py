from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import TemplateConfigurationService

def get_template_configuration_service(db: Session = Depends(get_db)) -> TemplateConfigurationService:
    return TemplateConfigurationService(db)
