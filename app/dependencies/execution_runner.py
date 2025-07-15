from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.execution_runner import ExecutionRunnerService

from app.core.redis import get_redis_client  # ajoute ceci

def get_execution_runner_service(db: Session = Depends(get_db)) -> ExecutionRunnerService:
    service = ExecutionRunnerService(db)
    service.redis = get_redis_client()  # injecte ici le client Redis déjà connecté
    return service