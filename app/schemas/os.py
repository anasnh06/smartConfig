from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field




# 🔹 Short (pour relations)
class OperatingSystemShort(BaseModel):
    id: int
    name: str
    version: Optional[str] = None

    class Config:
        from_attributes = True


# 🔸 Base
class OperatingSystemBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom du système d'exploitation")
    version: Optional[str] = Field(None, max_length=50, description="Version du système")


# 🟢 Create
class OperatingSystemCreate(OperatingSystemBase):
    pass


# ✏️ Update
class OperatingSystemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)


# 🛠 InDB
class OperatingSystemInDB(OperatingSystemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True



from app.schemas.server import ServerShort
from app.schemas.configuration import ConfigurationShort
from app.schemas.template import TemplateShort
# 🌐 Public (retour complet)
class OperatingSystemPublic(BaseModel):
    id: int
    name: str
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    servers: List[ServerShort] = []
    configurations: List[ConfigurationShort] = []
    templates: List[TemplateShort] = []

    class Config:
        from_attributes = True
