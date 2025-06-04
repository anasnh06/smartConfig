from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.os import OperatingSystemShort
    from app.schemas.role import RoleShort
    from app.schemas.template_configuration import TemplateConfigurationShort
    from app.schemas.server_template import ServerTemplateShortForTemplate
    from app.schemas.user import UserShort


class TemplateShort(BaseModel):
    id: int
    name: str

    role: Optional["RoleShort"] = None
    operating_systems: List["OperatingSystemShort"] = []

    class Config:
        from_attributes = True


class TemplateBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom du template")
    description: Optional[str] = Field(None, description="Description optionnelle")


class TemplateCreate(TemplateBase):
    role_id: Optional[int] = Field(None, description="ID du rôle associé")
    operating_system_ids: List[int] = Field(default_factory=list, description="Liste des OS compatibles")


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    role_id: Optional[int] = Field(None, description="Modifier le rôle")
    operating_system_ids: Optional[List[int]] = Field(default=None, description="Nouvelle liste des OS compatibles")


class TemplateInDB(TemplateBase):
    id: int
    role_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class TemplatePublic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    role: Optional["RoleShort"] = None
    operating_systems: List["OperatingSystemShort"] = []
    template_configurations: List["TemplateConfigurationShort"] = []
    template_servers: List["ServerTemplateShortForTemplate"] = []

    class Config:
        from_attributes = True
