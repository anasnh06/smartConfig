from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import TemplateCreate, TemplateUpdate, TemplatePublic
from app.dependencies import get_template_service, get_current_user
from app.services import TemplateService
from app.models import User

router = APIRouter()


@router.post("/", response_model=TemplatePublic, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: TemplateCreate,
    template_service: TemplateService = Depends(get_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un template avec OS compatibles et rôle associé.
    """
    return template_service.create(template_in, created_by_id=current_user.id)


@router.get("/", response_model=List[TemplatePublic], status_code=status.HTTP_200_OK)
def list_templates(
    skip: int = 0,
    limit: int = 100,
    template_service: TemplateService = Depends(get_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des templates.
    """
    return template_service.list_all(skip=skip, limit=limit)    


@router.get("/{template_id}", response_model=TemplatePublic, status_code=status.HTTP_200_OK)
def get_template(
    template_id: int,
    template_service: TemplateService = Depends(get_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Détail d’un template avec ses configurations et serveurs attachés.
    """
    template = template_service.get_by_id(template_id, include_related=True)
    if not template:
        raise HTTPException(status_code=404, detail="Template introuvable.")
    return template


@router.patch("/{template_id}", response_model=TemplatePublic, status_code=status.HTTP_200_OK)
def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    template_service: TemplateService = Depends(get_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour un template (rôle ou OS).
    """
    updated = template_service.update(template_id, template_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Template introuvable.")
    return updated


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    template_service: TemplateService = Depends(get_template_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un template.
    """
    if not template_service.delete(template_id):
        raise HTTPException(status_code=404, detail="Template introuvable.")
    return
