from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ExecutionGroupService

def get_execution_group_service(db: Session = Depends(get_db)) -> ExecutionGroupService:
    return ExecutionGroupService(db)
