from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ServerConfigurationCreate,
    ServerConfigurationUpdate,
    ServerConfigurationPublic,
)
from app.dependencies import get_server_configuration_service, get_current_user
from app.services import ServerConfigurationService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ServerConfigurationPublic, status_code=status.HTTP_201_CREATED)
def create_server_configuration(
    server_config_in: ServerConfigurationCreate,
    service: ServerConfigurationService = Depends(get_server_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée une exécution serveur/configuration (libre, via template ou directe).
    """
    return service.create(server_config_in, created_by_id=current_user.id)


@router.get("/", response_model=List[ServerConfigurationPublic], status_code=status.HTTP_200_OK)
def list_server_configurations(
    skip: int = 0,
    limit: int = 100,
    service: ServerConfigurationService = Depends(get_server_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des exécutions serveur/configuration.
    """
    return service.list_all(skip=skip, limit=limit)


@router.get("/{server_config_id}", response_model=ServerConfigurationPublic, status_code=status.HTTP_200_OK)
def get_server_configuration(
    server_config_id: int,
    service: ServerConfigurationService = Depends(get_server_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Détail d'une exécution serveur/configuration.
    """
    config = service.get_by_id(server_config_id, include_related=True)
    if not config:
        raise HTTPException(status_code=404, detail="Exécution introuvable.")
    return config


@router.patch("/{server_config_id}", response_model=ServerConfigurationPublic, status_code=status.HTTP_200_OK)
def update_server_configuration(
    server_config_id: int,
    update_data: ServerConfigurationUpdate,
    service: ServerConfigurationService = Depends(get_server_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour une exécution (status, retour, output...).
    """
    updated = service.update(server_config_id, update_data, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Exécution introuvable.")
    return updated


@router.delete("/{server_config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_server_configuration(
    server_config_id: int,
    service: ServerConfigurationService = Depends(get_server_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime une exécution serveur/configuration.
    """
    if not service.delete(server_config_id):
        raise HTTPException(status_code=404, detail="Exécution introuvable.")
    return
