import logging
import asyncio
from sqlalchemy.exc import SQLAlchemyError

from app.tasks.celery_app import celery_app
from app.services.execution_runner import ExecutionRunnerService
from app.db import get_db

logger = logging.getLogger(__name__)


@celery_app.task(
    name="run_execution_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def run_execution_task(self, execution_id: int):
    """
    Tâche Celery pour lancer une exécution complète via ExecutionRunnerService.
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        logger.info(f"[CELERY] ▶️ Lancement exécution ID={execution_id}")
        runner = ExecutionRunnerService(db)
        asyncio.run(runner.launch_execution(execution_id))
        logger.info(f"[CELERY] ✅ Terminé exécution ID={execution_id}")
    except SQLAlchemyError as db_error:
        logger.error(f"[CELERY] ❌ Erreur SQL exécution ID={execution_id} : {db_error}")
        raise
    except Exception as e:
        logger.error(f"[CELERY] ❌ Erreur inattendue exécution ID={execution_id} : {e}")
        raise
    finally:
        db.close()


@celery_app.task(
    name="run_group_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def run_group_task(self, group_id: int):
    """
    Tâche Celery pour lancer un groupe d'exécution unique via ExecutionRunnerService.
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        logger.info(f"[CELERY] ▶️ Lancement groupe ID={group_id}")
        runner = ExecutionRunnerService(db)
        asyncio.run(runner.launch_group(group_id))
        logger.info(f"[CELERY] ✅ Terminé groupe ID={group_id}")
    except SQLAlchemyError as db_error:
        logger.error(f"[CELERY] ❌ Erreur SQL groupe ID={group_id} : {db_error}")
        raise
    except Exception as e:
        logger.error(f"[CELERY] ❌ Erreur inattendue groupe ID={group_id} : {e}")
        raise
    finally:
        db.close()
