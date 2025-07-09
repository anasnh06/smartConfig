from fastapi import APIRouter, Depends, status, HTTPException
from app.services.execution_runner import ExecutionRunnerService
from app.dependencies.execution_runner import get_execution_runner_service
from app.dependencies import get_current_user
from app.models import User
from fastapi.responses import JSONResponse

router = APIRouter()



@router.post("/launch/full", status_code=status.HTTP_201_CREATED)
async def launch_full_execution(
    data: dict,  # contient title et groups_data
    service: ExecutionRunnerService = Depends(get_execution_runner_service),
    current_user: User = Depends(get_current_user),
):
    title = data.get("title")
    groups_data = data.get("groups", [])

    if not groups_data:
        raise HTTPException(status_code=400, detail="Au moins un groupe requis")

    # Validation : chaque groupe doit avoir au moins 1 serveur et 1 élément
    for idx, group in enumerate(groups_data):
        if not group.get("servers"):
            raise HTTPException(status_code=400, detail=f"Groupe {idx+1} sans serveurs")
        if not group.get("elements"):
            raise HTTPException(status_code=400, detail=f"Groupe {idx+1} sans éléments")

    # ⚙️ Appel du service complet
    execution = await service.create_and_launch_execution(
        title=title,
        groups_data=groups_data,
        created_by=current_user.id,
    )

    # ✅ Retour propre
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": execution.id,
            "title": execution.title,
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
        },
    )




# ✅ Lancer une exécution via Celery
@router.post("/launch/celery/{execution_id}", status_code=status.HTTP_202_ACCEPTED)
def launch_execution_celery(
    execution_id: int,
    service: ExecutionRunnerService = Depends(get_execution_runner_service),
    current_user: User = Depends(get_current_user),
):
    from app.tasks.execution import run_execution_task
    run_execution_task.delay(execution_id)
    return {"message": f"Exécution {execution_id} lancée (Celery)."}





# ✅ Lancer un groupe via Celery
@router.post("/launch/group/celery/{group_id}", status_code=status.HTTP_202_ACCEPTED)
def launch_group_celery(
    group_id: int,
    service: ExecutionRunnerService = Depends(get_execution_runner_service),
    current_user: User = Depends(get_current_user),
):
    from app.tasks.execution import run_group_task
    run_group_task.delay(group_id)
    return {"message": f"Groupe {group_id} lancé (Celery)."}





# ✅ Obtenir le statut agrégé d'une exécution (optionnel)
@router.get("/execution/status/{execution_id}", status_code=status.HTTP_200_OK)
def get_execution_status(
    execution_id: int,
    service: ExecutionRunnerService = Depends(get_execution_runner_service),
    current_user: User = Depends(get_current_user),
):
    execution = service.db.query(service.Execution).filter_by(id=execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Exécution introuvable")
    return {
        "id": execution.id,
        "status": execution.status,
        "started_at": execution.started_at,
        "finished_at": execution.finished_at
    }


@router.get("/group/status/{group_id}", status_code=200)
def get_group_status(
    group_id: int,
    service: ExecutionRunnerService = Depends(get_execution_runner_service),
    current_user: User = Depends(get_current_user),
):
    group = service.db.query(service.ExecutionGroup).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")
    return {
        "id": group.id,
        "status": group.status,
        "started_at": group.started_at,
        "finished_at": group.finished_at
    }


# ✅ Lancer un groupe (asynchrone, pas via Celery)
# @router.post("/launch/group/async/{group_id}", status_code=status.HTTP_202_ACCEPTED)
# async def launch_group_async(
#     group_id: int,
#     service: ExecutionRunnerService = Depends(get_execution_runner_service),
#     current_user: User = Depends(get_current_user),
# ):
#     await service.launch_group(group_id)
#     return {"message": f"Groupe {group_id} lancé (async)."}



# ✅ Lancer une exécution (asynchrone, pas via Celery)
# @router.post("/launch/async/{execution_id}", status_code=status.HTTP_202_ACCEPTED)
# async def launch_execution_async(
#     execution_id: int,
#     service: ExecutionRunnerService = Depends(get_execution_runner_service),
#     current_user: User = Depends(get_current_user),
# ):
#     await service.launch_execution(execution_id)
#     return {"message": f"Exécution {execution_id} lancée (async)."}



# ✅ Replay : exécution complète
# @router.post("/replay/execution/{execution_id}", status_code=status.HTTP_201_CREATED)
# def replay_execution(
#     execution_id: int,
#     service: ExecutionRunnerService = Depends(get_execution_runner_service),
#     current_user: User = Depends(get_current_user),
# ):
#     execution = service.replay_execution(execution_id, created_by=current_user.id)
#     from app.tasks.execution import launch_execution_task
#     launch_execution_task.delay(execution.id)
#     return execution


# ✅ Replay : un groupe
# @router.post("/replay/group/{group_id}", status_code=status.HTTP_201_CREATED)
# def replay_group(
#     group_id: int,
#     service: ExecutionRunnerService = Depends(get_execution_runner_service),
#     current_user: User = Depends(get_current_user),
# ):
#     execution = service.replay_group(group_id, created_by=current_user.id)
#     from app.tasks.execution import launch_execution_task
#     launch_execution_task.delay(execution.id)
#     return execution


# ✅ Replay : un ServerTemplate
# @router.post("/replay/server_template/{st_id}", status_code=status.HTTP_201_CREATED)
# def replay_server_template(
#     st_id: int,
#     service: ExecutionRunnerService = Depends(get_execution_runner_service),
#     current_user: User = Depends(get_current_user),
# ):
#     execution = service.replay_server_template(st_id, created_by=current_user.id)
#     from app.tasks.execution import launch_execution_task
#     launch_execution_task.delay(execution.id)
#     return execution


# ✅ Replay : un ServerConfiguration
# @router.post("/replay/server_configuration/{sc_id}", status_code=status.HTTP_201_CREATED)
# def replay_server_configuration(
#     sc_id: int,
#     service: ExecutionRunnerService = Depends(get_execution_runner_service),
#     current_user: User = Depends(get_current_user),
# ):
#     execution = service.replay_server_configuration(sc_id, created_by=current_user.id)
#     from app.tasks.execution import launch_execution_task
#     launch_execution_task.delay(execution.id)
#     return execution