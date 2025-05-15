from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import UserCreate, UserUpdate, UserPublic, UserInDB
from app.dependencies import get_user_service, get_current_user
from app.models import User
from app.services import UserService

router = APIRouter()


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Crée un nouvel utilisateur si l'email et le username sont uniques.
    """
    if user_service.get_by_email(user_create.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")
    if user_service.get_by_username(user_create.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username déjà utilisé")
    user = user_service.create(user_create, created_by_id=current_user.id)
    return user_service.get_by_id(user.id, include_related=True)    


@router.get("/", response_model=List[UserInDB], status_code=status.HTTP_200_OK)
def list_users(
    skip: int = 0,
    limit: int = 10,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    📄 Liste paginée des utilisateurs.
    """
    return user_service.list_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère un utilisateur par son ID.
    """
    user = user_service.get_by_id(user_id, include_related=True)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    return user


@router.patch("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    ✏️ Met à jour les informations d'un utilisateur.
    """
    updated_user = user_service.update(user_id, user_update, updated_by_id=current_user.id)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    
    # ✅ Ajout : retourne l’objet avec les relations chargées
    return user_service.get_by_id(updated_user.id, include_related=True)



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    🗑 Supprime un utilisateur.
    """
    if not user_service.delete(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    return
