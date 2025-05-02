from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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


class OperatingSystemPublic(OperatingSystemInDB):
    pass