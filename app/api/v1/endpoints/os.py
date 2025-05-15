from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import OperatingSystemCreate, OperatingSystemUpdate, OperatingSystemPublic, OperatingSystemInDB
from app.dependencies import get_operating_system_service, get_current_user
from app.services import OperatingSystemService
from app.models import User

router = APIRouter()


@router.post("/", response_model=OperatingSystemPublic, status_code=status.HTTP_201_CREATED)
def create_os(
    os_in: OperatingSystemCreate,
    os_service: OperatingSystemService = Depends(get_operating_system_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un système d'exploitation.
    """
    return os_service.create(os_in, created_by_id=current_user.id)


@router.get("/", response_model=List[OperatingSystemInDB], status_code=status.HTTP_200_OK)
def list_os(
    skip: int = 0,
    limit: int = 100,
    os_service: OperatingSystemService = Depends(get_operating_system_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des systèmes d'exploitation.
    """
    return os_service.list_all(skip=skip, limit=limit)


@router.get("/{os_id}", response_model=OperatingSystemPublic, status_code=status.HTTP_200_OK)
def get_os(
    os_id: int,
    os_service: OperatingSystemService = Depends(get_operating_system_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère un système d'exploitation par ID.
    """
    os = os_service.get_by_id(os_id, include_related=True)
    if not os:
        raise HTTPException(status_code=404, detail="Système d'exploitation introuvable.")
    return os


@router.patch("/{os_id}", response_model=OperatingSystemPublic, status_code=status.HTTP_200_OK)
def update_os(
    os_id: int,
    os_in: OperatingSystemUpdate,
    os_service: OperatingSystemService = Depends(get_operating_system_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour un système d'exploitation.
    """
    updated = os_service.update(os_id, os_in, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Système d'exploitation introuvable.")
    return updated


@router.delete("/{os_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_os(
    os_id: int,
    os_service: OperatingSystemService = Depends(get_operating_system_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un système d'exploitation.
    """
    if not os_service.delete(os_id):
        raise HTTPException(status_code=404, detail="Système d'exploitation introuvable.")
    return
