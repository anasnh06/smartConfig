from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field




# 🔹 Short schema (pour relations simplifiées)
class EnvironmentShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# 🔸 Base commun
class EnvironmentBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom de l'environnement (ex: production, staging)")


# 🟢 Création
class EnvironmentCreate(EnvironmentBase):
    pass


# ✏️ Mise à jour
class EnvironmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Nom de l'environnement")


# 🛠 InDB (interne, avec champs d’audit)
class EnvironmentInDB(EnvironmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

from app.schemas.server import ServerShort

# 🌐 Public (ce qu’on expose côté API)
class EnvironmentPublic(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    servers: List[ServerShort] = []

    class Config:
        from_attributes = True
