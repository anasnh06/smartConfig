from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.execution_runner import ExecutionRunnerService

def get_execution_runner_service(db: Session = Depends(get_db)) -> ExecutionRunnerService:
    return ExecutionRunnerService(db)
