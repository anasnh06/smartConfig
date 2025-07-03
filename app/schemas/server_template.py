from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.template import TemplateShort
    from app.schemas.server import ServerShort
    from app.schemas.user import UserShort
    from app.schemas.server_configuration import ServerConfigurationShortForExecution


class ServerTemplateShort(BaseModel):
    id: int
    status: Optional[str] = None
    server: "ServerShort"
    template: "TemplateShort"

    class Config:
        from_attributes = True


class ServerTemplateShortForTemplate(BaseModel):
    id: int
    status: Optional[str] = None
    server: "ServerShort"

    class Config:
        from_attributes = True


class ServerTemplateBase(BaseModel):
    status: Optional[str] = Field(None, description="Statut du template sur le serveur")


class ServerTemplateCreate(ServerTemplateBase):
    server_id: int
    template_id: int
    


class ServerTemplateUpdate(BaseModel):
    status: Optional[str] = None
    server_id: Optional[int] = None
    template_id: Optional[int] = None


class ServerTemplateInDB(ServerTemplateBase):
    id: int
    server_id: int
    template_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ServerTemplatePublic(BaseModel):
    id: int
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    server: "ServerShort"
    template: "TemplateShort"
    server_configurations: list["ServerConfigurationShortForExecution"] = []

    class Config:
        from_attributes = True
