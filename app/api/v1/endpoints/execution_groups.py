from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ExecutionGroupCreate,
    ExecutionGroupUpdate,
    ExecutionGroupPublic,
)
from app.dependencies import get_current_user, get_execution_group_service
from app.services import ExecutionGroupService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ExecutionGroupPublic, status_code=status.HTTP_201_CREATED)
def create_execution_group(
    execution_group_in: ExecutionGroupCreate,
    service: ExecutionGroupService = Depends(get_execution_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un groupe d'exécution.
    """
    return service.create(execution_group_in, created_by_id=current_user.id)


@router.get("/", response_model=List[ExecutionGroupPublic], status_code=status.HTTP_200_OK)
def list_execution_groups(
    skip: int = 0,
    limit: int = 100,
    service: ExecutionGroupService = Depends(get_execution_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des groupes d'exécution.
    """
    return service.list_all(skip=skip, limit=limit)


@router.get("/{execution_group_id}", response_model=ExecutionGroupPublic, status_code=status.HTTP_200_OK)
def get_execution_group(
    execution_group_id: int,
    service: ExecutionGroupService = Depends(get_execution_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Détail d’un groupe d’exécution (avec les server_configurations associées).
    """
    group = service.get_by_id(execution_group_id, include_related=True)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    return group


@router.patch("/{execution_group_id}", response_model=ExecutionGroupPublic, status_code=status.HTTP_200_OK)
def update_execution_group(
    execution_group_id: int,
    update_data: ExecutionGroupUpdate,
    service: ExecutionGroupService = Depends(get_execution_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour un groupe d'exécution.
    """
    updated = service.update(execution_group_id, update_data, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    return updated


@router.delete("/{execution_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution_group(
    execution_group_id: int,
    service: ExecutionGroupService = Depends(get_execution_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un groupe d'exécution.
    """
    if not service.delete(execution_group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    return
