from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.execution_group import ExecutionGroupShort
    from app.schemas.user import UserShort


class ExecutionShort(BaseModel):
    id: int
    title: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class ExecutionBase(BaseModel):
    title: Optional[str] = Field(None, description="Titre de l’exécution (optionnel)")
    status: Optional[str] = Field(default="pending", description="Statut global de l’exécution")
    started_at: Optional[datetime] = Field(None, description="Date de début d’exécution")
    finished_at: Optional[datetime] = Field(None, description="Date de fin d’exécution")


class ExecutionCreate(ExecutionBase):
    pass


class ExecutionUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    


class ExecutionInDB(ExecutionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ExecutionPublic(BaseModel):
    id: int
    title: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user: Optional["UserShort"] = None
    updated_by_user: Optional["UserShort"] = None

    execution_groups: list["ExecutionGroupShort"] = []

    class Config:
        from_attributes = True
