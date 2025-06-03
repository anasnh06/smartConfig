from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ServerCreate,
    ServerUpdate,
    ServerPublic,
    ServerInDB,
    ServerShort,  # added
)
from app.dependencies import get_server_service, get_current_user
from app.services import ServerService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ServerPublic, status_code=status.HTTP_201_CREATED)
def create_server(
    server_in: ServerCreate,
    server_service: ServerService = Depends(get_server_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un serveur avec ses rôles et infos système.
    """
    if server_service.get_by_name(server_in.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nom du serveur déjà utilisé.")
    
    server = server_service.create(server_in, created_by_id=current_user.id)
    return server_service.get_by_id(server.id, include_related=True)


@router.get("/", response_model=List[ServerPublic], status_code=status.HTTP_200_OK)
def list_servers(
    skip: int = 0,
    limit: int = 100,
    server_service: ServerService = Depends(get_server_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des serveurs.
    """
    return server_service.list_all(skip=skip, limit=limit)


@router.get("/short", response_model=List[ServerShort], status_code=status.HTTP_200_OK)
def list_servers_short(
    server_service: ServerService = Depends(get_server_service),
    current_user: User = Depends(get_current_user),
):
    """
    📋 Liste simplifiée des serveurs (id + nom, pour dropdowns).
    """
    return server_service.list_short()


@router.get("/{server_id}", response_model=ServerPublic, status_code=status.HTTP_200_OK)
def get_server(
    server_id: int,
    server_service: ServerService = Depends(get_server_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Détail complet du serveur (configurations, templates, rôles, etc.).
    """
    server = server_service.get_by_id(server_id, include_related=True)
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serveur introuvable.")
    return server


@router.patch("/{server_id}", response_model=ServerPublic, status_code=status.HTTP_200_OK)
def update_server(
    server_id: int,
    server_update: ServerUpdate,
    server_service: ServerService = Depends(get_server_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour les infos et rôles du serveur.
    """
    if server_service.get_by_name(server_update.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nom du serveur déjà utilisé.")
    updated = server_service.update(server_id, server_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serveur introuvable.")
    return server_service.get_by_id(updated.id, include_related=True)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_server(
    server_id: int,
    server_service: ServerService = Depends(get_server_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un serveur.
    """
    if not server_service.delete(server_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serveur introuvable.")
    return
