from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List

from app.schemas import (
    TemplateConfigurationCreate,
    TemplateConfigurationUpdate,
    TemplateConfigurationPublic,
    TemplateConfigurationInDB,
    BulkAttachToTemplate,
)
from app.dependencies import get_template_configuration_service, get_current_user
from app.services import TemplateConfigurationService
from app.models import User

router = APIRouter()


@router.post("/", response_model=TemplateConfigurationPublic, status_code=status.HTTP_201_CREATED)
def attach_configuration_to_template(
    attach_in: TemplateConfigurationCreate,
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    📎 Attache une configuration à un template avec un ordre d'exécution.
    """
    assoc = service.create(attach_in, created_by_id=current_user.id)
    return service.get_by_id(assoc.id, include_related=True)


@router.get("/", response_model=List[TemplateConfigurationPublic], status_code=status.HTTP_200_OK)
def list_template_configurations(
    skip: int = 0,
    limit: int = 100,
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des associations Template <-> Configuration.
    """
    return service.list_all(skip=skip, limit=limit)


@router.get("/{attachment_id}", response_model=TemplateConfigurationPublic, status_code=status.HTTP_200_OK)
def get_template_configuration(
    attachment_id: int,
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère une association Template <-> Configuration.
    """
    association = service.get_by_id(attachment_id, include_related=True)
    if not association:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lien introuvable.")
    return association


@router.patch("/{attachment_id}", response_model=TemplateConfigurationPublic, status_code=status.HTTP_200_OK)
def update_template_configuration(
    attachment_id: int,
    update_data: TemplateConfigurationUpdate,
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Modifie un attachement (ordre, contexte, etc.).
    """
    updated = service.update(attachment_id, update_data, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lien introuvable.")
    return service.get_by_id(updated.id, include_related=True)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template_configuration(
    attachment_id: int,
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime une liaison Template <-> Configuration.
    """
    if not service.delete(attachment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lien introuvable.")
    return

@router.post("/bulk-attach", response_model=List[TemplateConfigurationPublic], status_code=status.HTTP_201_CREATED)
def bulk_attach_configurations(
    payload: BulkAttachToTemplate = Body(...),
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    📎 Attache plusieurs configurations à un template (sans écrasement).
    """
    return service.attach_many(
        template_id=payload.template_id,
        items=payload.configurations,
        created_by_id=current_user.id
    )

@router.put("/replace", response_model=List[TemplateConfigurationPublic], status_code=status.HTTP_200_OK)
def replace_template_configurations(
    payload: BulkAttachToTemplate = Body(...),
    service: TemplateConfigurationService = Depends(get_template_configuration_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔁 Remplace toutes les configurations d’un template par une nouvelle liste.
    """
    return service.replace_all_for_template(
        template_id=payload.template_id,
        items=payload.configurations,
        user_id=current_user.id
    )
