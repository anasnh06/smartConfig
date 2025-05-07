from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ExecutionGroupShort(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        from_attributes = True


class ExecutionGroupBase(BaseModel):
    name: Optional[str] = Field(None, description="Nom ou étiquette du groupe d’exécution")


class ExecutionGroupCreate(ExecutionGroupBase):
    execution_id: int


class ExecutionGroupUpdate(BaseModel):
    name: Optional[str] = None


class ExecutionGroupInDB(ExecutionGroupBase):
    id: int
    execution_id: int
    status: Optional[str] = None
    playbook_path: Optional[str] = None
    inventory_path: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


from app.schemas.execution import ExecutionShort
from app.schemas.server_configuration import ServerConfigurationShort

class ExecutionGroupPublic(BaseModel):
    id: int
    name: Optional[str] = None
    status: Optional[str] = None
    playbook_path: Optional[str] = None
    inventory_path: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    execution: ExecutionShort
    server_configurations: list[ServerConfigurationShort] = []

    class Config:
        from_attributes = True
