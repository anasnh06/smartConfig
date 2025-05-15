from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import TemplateService

def get_template_service(db: Session = Depends(get_db)) -> TemplateService:
    return TemplateService(db)
