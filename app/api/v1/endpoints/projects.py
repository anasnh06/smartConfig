from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectPublic,
    ProjectInDB,
)
from app.dependencies import get_project_service, get_current_user
from app.services import ProjectService
from app.models import User

router = APIRouter()


@router.post("/", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un projet si le nom est unique.
    """
    if project_service.get_by_name(project_in.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nom du projet déjà utilisé.")
    
    project = project_service.create(project_in, created_by_id=current_user.id)
    return project_service.get_by_id(project.id, include_related=True)


@router.get("/", response_model=List[ProjectPublic], status_code=status.HTTP_200_OK)
def list_projects(
    skip: int = 0,
    limit: int = 100,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des projets.
    """
    return project_service.list_all(skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectPublic, status_code=status.HTTP_200_OK)
def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère un projet par ID avec les relations.
    """
    project = project_service.get_by_id(project_id, include_related=True)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable.")
    return project


@router.patch("/{project_id}", response_model=ProjectPublic, status_code=status.HTTP_200_OK)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour un projet existant.
    """

    if project_service.get_by_name(project_update.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nom du projet déjà utilisé.")
    updated = project_service.update(project_id, project_update, updated_by_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable.")
    return project_service.get_by_id(updated.id, include_related=True)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un projet.
    """
    if not project_service.delete(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable.")
    return
