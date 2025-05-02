from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 🎯 Base commun pour réutilisation
class EnvironmentBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nom de l'environnement (ex: production, staging)")

# ✅ Pour création
class EnvironmentCreate(EnvironmentBase):
    pass

# 🔁 Pour mise à jour (champs optionnels)
class EnvironmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)

# 📦 Format utilisé en base
class EnvironmentInDB(EnvironmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True  # 🔄 Permet la conversion depuis un ORM SQLAlchemy

class EnvironmentPublic(EnvironmentInDB):
    pass