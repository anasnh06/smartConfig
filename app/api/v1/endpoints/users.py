from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserCreate, UserUpdate, UserInDB
from app.dependencies import get_user_service, get_current_user
from app.models import User

router = APIRouter()

@router.post("/", response_model=UserInDB, status_code=201)
def create_user(
    user_create: UserCreate,
    user_service = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    if user_service.get_by_email(user_create.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if user_service.get_by_username(user_create.username):
        raise HTTPException(status_code=400, detail="Username déjà utilisé")
    return user_service.create(user_create, created_by_id=current_user.id)

@router.get("/", response_model=list[UserInDB])
def read_users(
    skip: int = 0,
    limit: int = 10,
    user_service = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return user_service.list_all(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserInDB)
def read_user(
    user_id: int,
    user_service = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user

@router.patch("/{user_id}", response_model=UserInDB)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    
    updated_user = user_service.update(user_id, user_update, updated_by_id=current_user.id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return updated_user

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    user_service = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    if not user_service.delete(user_id):
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return
