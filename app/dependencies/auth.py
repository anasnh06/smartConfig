from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import settings
from app.db import get_db
from app.models import User
from app.services import AuthService, UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ✅ Injecter le AuthService
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# ✅ Obtenir l’utilisateur actuel via le token JWT
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré. Veuillez vous reconnecter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    user = UserService(db).get_by_username(username)
    if not user:
        raise credentials_exception

    AuthService(db).ensure_user_is_active(user)
    return user

# ✅ Vérifie que l’utilisateur est actif
def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    AuthService(None).ensure_user_is_active(current_user)
    return current_user
