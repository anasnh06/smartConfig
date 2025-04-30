from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import UserCreate, UserInDB
from app.dependencies import get_user_service, get_auth_service, get_current_user
from app.models import User

router = APIRouter()

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    user_service = Depends(get_user_service)
):
    if user_service.get_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if user_service.get_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username déjà utilisé")
    return user_service.create(user, created_by_id=None)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    auth_service.ensure_user_is_active(user)
    token = auth_service.generate_token(user)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
