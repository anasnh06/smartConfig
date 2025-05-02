from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import RoleCreate, RoleUpdate, RolePublic
from app.dependencies import get_role_service, get_current_user
from app.models import User
from app.services import RoleService

router = APIRouter()


@router.post("/", response_model=RolePublic, status_code=status.HTTP_201_CREATED)
def create_role(
    role_create: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un nouveau rôle si le nom est unique.
    """
    existing = role_service.get_by_name(role_create.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom du rôle déjà utilisé."
        )
    return role_service.create(role_create, created_by_id=current_user.id)


@router.get("/", response_model=List[RolePublic], status_code=status.HTTP_200_OK)
def list_roles(
    skip: int = 0,
    limit: int = 100,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des rôles existants.
    """
    return role_service.list_all(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RolePublic, status_code=status.HTTP_200_OK)
def get_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère un rôle par son ID.
    """
    role = role_service.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle introuvable."
        )
    return role


@router.patch("/{role_id}", response_model=RolePublic, status_code=status.HTTP_200_OK)
def update_role(
    role_id: int,
    role_update: RoleUpdate,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour un rôle existant.
    """
    updated = role_service.update(role_id, role_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle introuvable."
        )
    return updated


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un rôle par son ID.
    """
    deleted = role_service.delete(role_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle introuvable."
        )
    return
