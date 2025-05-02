from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    EnvironmentCreate,
    EnvironmentUpdate,
    EnvironmentInDB,
    EnvironmentPublic,
)
from app.dependencies import get_current_user, get_environment_service
from app.models import User
from app.services import EnvironmentService

router = APIRouter()


@router.post("/", response_model=EnvironmentPublic, status_code=status.HTTP_201_CREATED)
def create_environment(
    environment_in: EnvironmentCreate,
    environment_service: EnvironmentService = Depends(get_environment_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un nouvel environnement si le nom est unique.
    """
    if environment_service.get_by_name(environment_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom d’environnement déjà utilisé."
        )
    return environment_service.create(environment_in, created_by_id=current_user.id)


@router.get("/", response_model=List[EnvironmentPublic], status_code=status.HTTP_200_OK)
def list_environments(
    skip: int = 0,
    limit: int = 100,
    environment_service: EnvironmentService = Depends(get_environment_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée de tous les environnements.
    """
    return environment_service.list_all(skip=skip, limit=limit)


@router.get("/{environment_id}", response_model=EnvironmentPublic, status_code=status.HTTP_200_OK)
def get_environment(
    environment_id: int,
    environment_service: EnvironmentService = Depends(get_environment_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère un environnement spécifique par son ID.
    """
    environment = environment_service.get_by_id(environment_id)
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environnement introuvable."
        )
    return environment


@router.patch("/{environment_id}", response_model=EnvironmentPublic, status_code=status.HTTP_200_OK)
def update_environment(
    environment_id: int,
    environment_update: EnvironmentUpdate,
    environment_service: EnvironmentService = Depends(get_environment_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour un environnement existant.
    """
    updated = environment_service.update(environment_id, environment_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environnement introuvable."
        )
    return updated


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    environment_id: int,
    environment_service: EnvironmentService = Depends(get_environment_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un environnement par son ID.
    """
    if not environment_service.delete(environment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environnement introuvable."
        )
    return
