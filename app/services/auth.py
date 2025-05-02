from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.core import settings, create_access_token, verify_password, get_password_hash
from app.services.user import UserService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_service.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def generate_token(self, user: User) -> str:
        data = {"sub": user.username}
        expires = timedelta(minutes=settings.access_token_expire_minutes)
        return create_access_token(data, expires_delta=expires)

    def ensure_user_is_active(self, user: User):
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Utilisateur inactif. Veuillez contacter l'administrateur."
            )

    def change_password(self, user: User, new_password: str) -> User:
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user