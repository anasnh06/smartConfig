from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.core import settings
from app.models import User
from app.services import get_user_by_username, verify_password

# ✅ Authentifier un utilisateur
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# ✅ Générer un token JWT
def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=settings.access_token_expire_minutes),
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

# ✅ Vérifier si un utilisateur est actif
def ensure_user_is_active(user: User):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur inactif. Veuillez contacter l'administrateur.",
        )
