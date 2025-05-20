from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.server import ServerShort
    from app.schemas.user import UserShort


class EnvironmentShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class EnvironmentBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom de l'environnement (ex: production, staging)")


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Nom de l'environnement")


class EnvironmentInDB(EnvironmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class EnvironmentPublic(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    servers: List["ServerShort"] = []

    class Config:
        from_attributes = True
