from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import UserCreate, UserPublic
from app.dependencies import get_user_service, get_auth_service, get_current_user
from app.models import User
from app.services import UserService, AuthService

router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    ✅ Enregistre un nouvel utilisateur.
    - Vérifie l'unicité de l'email et du username.
    - Retourne l'utilisateur créé sans le mot de passe.
    """
    if user_service.get_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé. Veuillez en choisir un autre."
        )
    if user_service.get_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom d'utilisateur déjà pris. Veuillez en choisir un autre."
        )
    return user_service.create(user, created_by_id=None)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    🔐 Authentifie un utilisateur et génère un token JWT.
    - Vérifie les identifiants
    - Vérifie l'état actif
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides. Vérifiez votre nom d'utilisateur ou mot de passe.",
        )

    auth_service.ensure_user_is_active(user)

    token = auth_service.generate_token(user)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
def read_users_me(
    current_user: User = Depends(get_current_user),
):
    """
    🔎 Récupère les infos de l'utilisateur actuellement connecté.
    """
    return current_user

@router.get("/check-token", status_code=status.HTTP_200_OK)
def check_token(current_user: User = Depends(get_current_user)):
    """
    🔐 Vérifie que le token JWT est valide et retourne un résumé utilisateur.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active
    }


