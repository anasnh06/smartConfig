from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.server import ServerShort
    from app.schemas.configuration import ConfigurationShort
    from app.schemas.template import TemplateShort
    from app.schemas.user import UserShort


class OperatingSystemShort(BaseModel):
    id: int
    name: str
    version: Optional[str] = None

    class Config:
        from_attributes = True


class OperatingSystemBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom du système d'exploitation")
    version: Optional[str] = Field(None, max_length=50, description="Version du système")


class OperatingSystemCreate(OperatingSystemBase):
    pass


class OperatingSystemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)


class OperatingSystemInDB(OperatingSystemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class OperatingSystemPublic(BaseModel):
    id: int
    name: str
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    servers: List["ServerShort"] = []
    configurations: List["ConfigurationShort"] = []
    templates: List["TemplateShort"] = []

    class Config:
        from_attributes = True
