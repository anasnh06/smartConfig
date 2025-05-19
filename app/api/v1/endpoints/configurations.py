from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationPublic,
    ConfigurationInDB,
)
from app.dependencies import get_configuration_service, get_current_user
from app.services import ConfigurationService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ConfigurationPublic, status_code=status.HTTP_201_CREATED)
def create_configuration(
    configuration_in: ConfigurationCreate,
    configuration_service: ConfigurationService = Depends(get_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée une configuration avec association des OS cibles.
    """
    configuration = configuration_service.create(configuration_in, created_by_id=current_user.id)
    return configuration_service.get_by_id(configuration.id, include_related=True)


@router.get("/", response_model=List[ConfigurationInDB], status_code=status.HTTP_200_OK)
def list_configurations(
    skip: int = 0,
    limit: int = 100,
    configuration_service: ConfigurationService = Depends(get_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des configurations.
    """
    return configuration_service.list_all(skip=skip, limit=limit)


@router.get("/{configuration_id}", response_model=ConfigurationPublic, status_code=status.HTTP_200_OK)
def get_configuration(
    configuration_id: int,
    configuration_service: ConfigurationService = Depends(get_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère une configuration par son ID avec les relations.
    """
    configuration = configuration_service.get_by_id(configuration_id, include_related=True)
    if not configuration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration introuvable.")
    return configuration


@router.patch("/{configuration_id}", response_model=ConfigurationPublic, status_code=status.HTTP_200_OK)
def update_configuration(
    configuration_id: int,
    configuration_update: ConfigurationUpdate,
    configuration_service: ConfigurationService = Depends(get_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour une configuration (y compris les OS liés).
    """
    updated = configuration_service.update(configuration_id, configuration_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration introuvable.")
    return configuration_service.get_by_id(updated.id, include_related=True)


@router.delete("/{configuration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_configuration(
    configuration_id: int,
    configuration_service: ConfigurationService = Depends(get_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime une configuration.
    """
    if not configuration_service.delete(configuration_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration introuvable.")
    return
