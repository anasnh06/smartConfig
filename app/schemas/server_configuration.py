from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.server import ServerShort
    from app.schemas.configuration import ConfigurationShort
    from app.schemas.server_template import ServerTemplateShort
    from app.schemas.execution_group import ExecutionGroupShort 
    from app.schemas.user import UserShort


class ServerConfigurationShort(BaseModel):
    id: int
    status: Optional[str] = None
    return_code: Optional[int] = None
    configuration: Optional["ConfigurationShort"] = None

    class Config:
        from_attributes = True


class ServerConfigurationShortForConfiguration(BaseModel):
    id: int
    status: Optional[str] = None
    return_code: Optional[int] = None
    server: "ServerShort"

    class Config:
        from_attributes = True


class ServerConfigurationBase(BaseModel):
    status: Optional[str] = Field(default="pending", description="Statut d’exécution (pending, running, success, failed)")
    return_code: Optional[int] = Field(None, description="Code de retour de la commande")
    output: Optional[str] = Field(None, description="Sortie de la commande exécutée (stdout/stderr)")
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    source: Optional[str] = Field(None, description="Origine de la configuration (manual/template/custom)")
    custom_command: Optional[str] = Field(None, description="Commande personnalisée (si source=custom)")


class ServerConfigurationCreate(ServerConfigurationBase):
    server_id: int
    execution_group_id: int
    configuration_id: Optional[int] = None
    server_template_id: Optional[int] = None


class ServerConfigurationUpdate(BaseModel):
    status: Optional[str] = None
    return_code: Optional[int] = None
    output: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    source: Optional[str] = None
    custom_command: Optional[str] = None


class ServerConfigurationInDB(ServerConfigurationBase):
    id: int
    server_id: int
    execution_group_id: int
    configuration_id: Optional[int] = None
    server_template_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ServerConfigurationPublic(BaseModel):
    id: int
    status: Optional[str] = None
    return_code: Optional[int] = None
    output: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    source: Optional[str] = None
    custom_command: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    server: "ServerShort"
    execution_group: "ExecutionGroupShort"
    configuration: Optional["ConfigurationShort"] = None
    server_template: Optional["ServerTemplateShort"] = None

    class Config:
        from_attributes = True
