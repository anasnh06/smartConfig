from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field



# 🔹 Short schema (pour relations dans d'autres entités)
class ProjectShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# 🔸 Base commun
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom du projet")
    description: Optional[str] = Field(None, description="Description optionnelle du projet")


# 🟢 Création
class ProjectCreate(ProjectBase):
    pass


# ✏️ Mise à jour
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Nom du projet")
    description: Optional[str] = Field(None, description="Description du projet")


# 🛠 InDB (avec audit)
class ProjectInDB(ProjectBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True




from app.schemas.server import ServerShort
# 🌐 Public (exposé côté API)
class ProjectPublic(BaseModel):
    id: int
    name: str = Field(..., max_length=100, description="Nom du projet")
    description: Optional[str] = Field(None, description="Description optionnelle du projet")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    servers: List[ServerShort] = []

    class Config:
        from_attributes = True
