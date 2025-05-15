from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ExecutionService

def get_execution_service(db: Session = Depends(get_db)) -> ExecutionService:
    return ExecutionService(db)
