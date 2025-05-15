from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.server import ServerShort
    from app.schemas.template import TemplateShort
    from app.schemas.user import UserShort


class RoleShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom du rôle (ex: 'WebServer')")
    description: Optional[str] = Field(None, description="Description optionnelle du rôle")


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Nom du rôle")
    description: Optional[str] = Field(None, description="Description du rôle")


class RoleInDB(RoleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class RolePublic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    servers: List["ServerShort"] = []
    templates: List["TemplateShort"] = []
