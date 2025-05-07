from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.template import TemplateShort

class ServerTemplateShort(BaseModel):
    id: int
    status: Optional[str] = None
    context: Optional[str] = None
    template: "TemplateShort"

    class Config:
        from_attributes = True

from app.schemas.server import ServerShort  # lazy import

class ServerTemplateShortForTemplate(BaseModel):
    id: int
    status: Optional[str] = None
    context: Optional[str] = None
    server: ServerShort

    class Config:
        from_attributes = True

class ServerTemplateBase(BaseModel):
    status: Optional[str] = Field(None, description="Statut du template sur le serveur")
    context: Optional[str] = Field(None, description="Contexte spécifique à ce lien serveur-template")

class ServerTemplateCreate(ServerTemplateBase):
    server_id: int
    template_id: int

class ServerTemplateUpdate(BaseModel):
    status: Optional[str] = None
    context: Optional[str] = None

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
# ⏳ Lazy imports déjà utilisés
class ServerTemplatePublic(BaseModel):
    id: int
    status: Optional[str] = None
    context: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    server: ServerShort
    template: "TemplateShort"

    class Config:
        from_attributes = True

