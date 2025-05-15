from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ServerTemplateService

def get_server_template_service(db: Session = Depends(get_db)) -> ServerTemplateService:
    return ServerTemplateService(db)
