from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import EnvironmentService


def get_environment_service(db: Session = Depends(get_db)) -> EnvironmentService:
    return EnvironmentService(db)
