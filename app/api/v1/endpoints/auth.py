from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


from app.schemas import UserCreate, UserInDB
from app.services import *
from app.db import get_db
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Enregistre un nouvel utilisateur.
    Vérifie si l'utilisateur etl'email sont déjà utilisés avant de créer l'utilisateur.
    """
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé. Veuillez en choisir un autre.",
        )
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username déjà utilisé. Veuillez en choisir un autre.",
        )
    return create_user(db, user)

@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et génère un token JWT.
    Vérifie les identifiants et l'état actif de l'utilisateur.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides. Veuillez vérifier votre username et mot de passe.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte inactif. Veuillez contacter l'administrateur.",
        )
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB, status_code=status.HTTP_200_OK)
def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    """
    return current_user



