from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ServerService


def get_server_service(db: Session = Depends(get_db)) -> ServerService:
    return ServerService(db)
