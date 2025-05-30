from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ExecutionCreate,
    ExecutionUpdate,
    ExecutionPublic,
    ExecutionInDB,
)
from app.dependencies import get_current_user, get_execution_service
from app.services import ExecutionService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ExecutionPublic, status_code=status.HTTP_201_CREATED)
def create_execution(
    execution_in: ExecutionCreate,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée une exécution globale (peut contenir plusieurs groupes et serveurs).
    """
    execution = service.create(execution_in, created_by_id=current_user.id)
    return service.get_by_id(execution.id, include_related=True)


@router.get("/", response_model=List[ExecutionPublic], status_code=status.HTTP_200_OK)
def list_executions(
    skip: int = 0,
    limit: int = 100,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des exécutions globales.
    """
    return service.list_all(skip=skip, limit=limit)


@router.get("/{execution_id}", response_model=ExecutionPublic, status_code=status.HTTP_200_OK)
def get_execution(
    execution_id: int,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère le détail d’une exécution globale avec ses groupes.
    """
    execution = service.get_by_id(execution_id, include_related=True)
    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exécution introuvable.")
    return execution


@router.patch("/{execution_id}", response_model=ExecutionPublic, status_code=status.HTTP_200_OK)
def update_execution(
    execution_id: int,
    update_data: ExecutionUpdate,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour une exécution globale.
    """
    updated = service.update(execution_id, update_data, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exécution introuvable.")
    return service.get_by_id(updated.id, include_related=True)


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(
    execution_id: int,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime une exécution globale.
    """
    if not service.delete(execution_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exécution introuvable.")
    return
