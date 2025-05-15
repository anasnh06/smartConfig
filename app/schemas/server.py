from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field, IPvAnyAddress

if TYPE_CHECKING:
    from app.schemas.project import ProjectShort
    from app.schemas.os import OperatingSystemShort
    from app.schemas.environment import EnvironmentShort
    from app.schemas.role import RoleShort
    from app.schemas.server_template import ServerTemplateShort
    from app.schemas.server_configuration import ServerConfigurationShort
    from app.schemas.user import UserShort


class ServerShort(BaseModel):
    id: int
    name: str
    ip_address: IPvAnyAddress

    class Config:
        from_attributes = True


class ServerBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom unique du serveur")
    ip_address: IPvAnyAddress = Field(..., description="Adresse IP du serveur")
    ssh_port: int = Field(default=22, ge=1, le=65535, description="Port SSH")
    ssh_user: str = Field(..., max_length=100, description="Nom d’utilisateur SSH")
    ssh_private_key_path: str = Field(default="~/.ssh/id_rsa", max_length=255, description="Chemin vers la clé SSH")


class ServerCreate(ServerBase):
    operating_system_id: int = Field(..., description="ID du système d’exploitation")
    environment_id: int = Field(..., description="ID de l’environnement")
    project_id: int = Field(..., description="ID du projet")
    role_ids: List[int] = Field(default_factory=list, description="Liste des IDs des rôles associés")


class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[IPvAnyAddress] = None
    ssh_port: Optional[int] = Field(None, ge=1, le=65535)
    ssh_user: Optional[str] = Field(None, max_length=100)
    ssh_private_key_path: Optional[str] = Field(None, max_length=255)
    operating_system_id: Optional[int] = None
    environment_id: Optional[int] = None
    project_id: Optional[int] = None
    role_ids: Optional[List[int]] = Field(default=None, description="Nouvelle liste des rôles associés")


class ServerInDB(ServerBase):
    id: int
    operating_system_id: int
    environment_id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ServerPublic(BaseModel):
    id: int
    name: str
    ip_address: IPvAnyAddress
    ssh_port: int
    ssh_user: str
    ssh_private_key_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    operating_system: "OperatingSystemShort"
    environment: "EnvironmentShort"
    project: "ProjectShort"
    roles: List["RoleShort"] = []
    server_templates: List["ServerTemplateShort"] = []
    server_configurations: List["ServerConfigurationShort"] = []

    class Config:
        from_attributes = True
