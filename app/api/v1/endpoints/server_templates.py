from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ServerTemplateCreate,
    ServerTemplateUpdate,
    ServerTemplatePublic,
    ServerTemplateInDB,
)
from app.dependencies import get_server_template_service, get_current_user
from app.services import ServerTemplateService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ServerTemplatePublic, status_code=status.HTTP_201_CREATED)
def attach_template_to_server(
    attach_in: ServerTemplateCreate,
    service: ServerTemplateService = Depends(get_server_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    📎 Attache un template à un serveur (optionnellement avec contexte).
    """
    assoc = service.create(attach_in, created_by_id=current_user.id)
    return service.get_by_id(assoc.id, include_related=True)


@router.get("/", response_model=List[ServerTemplatePublic], status_code=status.HTTP_200_OK)
def list_server_templates(
    skip: int = 0,
    limit: int = 100,
    service: ServerTemplateService = Depends(get_server_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des associations Server <-> Template.
    """
    return service.list_all(skip=skip, limit=limit)


@router.get("/{attachment_id}", response_model=ServerTemplatePublic, status_code=status.HTTP_200_OK)
def get_server_template(
    attachment_id: int,
    service: ServerTemplateService = Depends(get_server_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère une liaison serveur/template.
    """
    assoc = service.get_by_id(attachment_id, include_related=True)
    if not assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liaison introuvable.")
    return assoc


@router.patch("/{attachment_id}", response_model=ServerTemplatePublic, status_code=status.HTTP_200_OK)
def update_server_template(
    attachment_id: int,
    update_data: ServerTemplateUpdate,
    service: ServerTemplateService = Depends(get_server_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Modifie un attachement serveur/template (ex: contexte).
    """
    updated = service.update(attachment_id, update_data, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liaison introuvable.")
    return service.get_by_id(updated.id, include_related=True)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_server_template(
    attachment_id: int,
    service: ServerTemplateService = Depends(get_server_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime une liaison serveur/template.
    """
    if not service.delete(attachment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liaison introuvable.")
    return
