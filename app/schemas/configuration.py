from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.os import OperatingSystemShort
    from app.schemas.server_configuration import ServerConfigurationShortForConfiguration
    from app.schemas.template_configuration import TemplateConfigurationShortForConfiguration
    from app.schemas.user import UserShort


class ConfigurationShort(BaseModel):
    id: int
    name: str
    operating_systems: List["OperatingSystemShort"] = []

    class Config:
        from_attributes = True


class ConfigurationBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom unique de la configuration")
    command: str = Field(..., description="Commande shell à exécuter via Ansible")
    description: Optional[str] = Field(None, description="Description facultative")


class ConfigurationCreate(ConfigurationBase):
    operating_system_ids: List[int] = Field(
        default_factory=list,
        description="Liste des IDs des systèmes d’exploitation compatibles"
    )


class ConfigurationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    command: Optional[str] = None
    description: Optional[str] = None
    operating_system_ids: Optional[List[int]] = Field(
        default=None,
        description="Nouvelle liste des OS compatibles (remplace l’ancienne)"
    )


class ConfigurationInDB(ConfigurationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True  


class ConfigurationPublic(BaseModel):
    id: int
    name: str
    command: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    operating_systems: List["OperatingSystemShort"] = []
    configuration_servers: List["ServerConfigurationShortForConfiguration"] = []
    configuration_templates: List["TemplateConfigurationShortForConfiguration"] = []

    class Config:
        from_attributes = True
