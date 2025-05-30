from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import settings
from app.db import get_db
from app.models import User
from app.services import AuthService, UserService

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ✅ Injecter le AuthService
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# ✅ Obtenir l’utilisateur actuel via le token JWT
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié.")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token invalide")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = UserService(db).get_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé.")

    AuthService(db).ensure_user_is_active(user)
    return user

# ✅ Vérifie que l’utilisateur est actif
def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    AuthService(None).ensure_user_is_active(current_user)
    return current_user
