from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import OperatingSystemService


def get_operating_system_service(db: Session = Depends(get_db)) -> OperatingSystemService:
    return OperatingSystemService(db)
