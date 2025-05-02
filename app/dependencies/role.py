from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import RoleService

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)
