from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas import UserCreate, UserPublic
from app.dependencies import get_user_service, get_auth_service, get_current_user
from app.models import User
from app.services import UserService, AuthService
from app.core import settings

router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    ✅ Enregistre un nouvel utilisateur.
    """
    if user_service.get_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")
    if user_service.get_by_username(user.username):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé.")
    return user_service.create(user, created_by_id=None)


@router.post("/login", response_model=UserPublic, status_code=status.HTTP_200_OK)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    🔐 Authentifie un utilisateur et retourne un cookie sécurisé contenant un token JWT.
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides.")

    auth_service.ensure_user_is_active(user)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = auth_service.generate_token(user, expires_delta=access_token_expires)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # ✅ Mets True en production (HTTPS obligatoire)
        samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )

    return UserPublic.from_orm(user)


@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    🔎 Récupère l'utilisateur actuellement authentifié.
    """
    return current_user


@router.get("/check-token", status_code=status.HTTP_200_OK)
def check_token(current_user: User = Depends(get_current_user)):
    """
    ✅ Vérifie que le token est valide (debug frontend).
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }

@router.post("/logout", status_code=status.HTTP_200_OK, response_class=JSONResponse)
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Déconnecté avec succès"}
