from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import ServerCreate, ServerUpdate, ServerPublic
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
        raise HTTPException(status_code=400, detail="Nom du serveur déjà utilisé.")
    return server_service.create(server_in, created_by_id=current_user.id)


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
        raise HTTPException(status_code=404, detail="Serveur introuvable.")
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
    updated = server_service.update(server_id, server_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Serveur introuvable.")
    return updated


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
        raise HTTPException(status_code=404, detail="Serveur introuvable.")
    return
