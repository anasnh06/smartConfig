from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import UserCreate, UserUpdate, UserInDB
from app.dependencies import get_current_user
from app.services import *
from app.services import user as user_service
from app.db import get_db

router = APIRouter()



@router.post("/", response_model=UserInDB, status_code=201)
def create_user(user_create: UserCreate, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    # Ensure `user.email` is accessed correctly
    if get_user_by_email(db, user_create.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if get_user_by_username(db, user_create.username):
        raise HTTPException(status_code=400, detail="Username déjà utilisé")
    user_create = user_create.model_copy(update={"created_by": current_user.id})
    return user_service.create_user(db, user_create)

@router.get("/", response_model=list[UserInDB])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    return get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user

@router.patch("/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    user_update = user_update.model_copy(update={"updated_by": current_user.id})
    user_update = user_service.update_user(db, user_id, user_update)
    if not user_update:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user_update

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    if not user_service.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return 
