from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# 🔹 Short (relation minimale)
class RoleShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# 🔸 Base commun
class RoleBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom du rôle (ex: 'WebServer')")
    description: Optional[str] = Field(None, description="Description optionnelle du rôle")


# 🟢 Create
class RoleCreate(RoleBase):
    pass


# ✏️ Update
class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Nom du rôle")
    description: Optional[str] = Field(None, description="Description du rôle")


# 🛠 InDB
class RoleInDB(RoleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# ⏳ Imports retardés pour éviter les circular imports
from app.schemas.server import ServerShort
from app.schemas.template import TemplateShort


# 🌐 Public (version complète)
class RolePublic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    servers: List[ServerShort] = []
    templates: List[TemplateShort] = []

    class Config:
        from_attributes = True
