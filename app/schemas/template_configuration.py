from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.configuration import ConfigurationShort

class TemplateConfigurationShort(BaseModel):
    id: int
    order: Optional[int] = None
    comment: Optional[str] = None
    configuration: ConfigurationShort

    class Config:
        from_attributes = True

from app.schemas.template import TemplateShort

class TemplateConfigurationShortForConfiguration(BaseModel):
    id: int
    order: Optional[int] = None
    comment: Optional[str] = None
    template: TemplateShort

    class Config:
        from_attributes = True

class TemplateConfigurationBase(BaseModel):
    order: Optional[int] = Field(None, description="Ordre d’exécution")
    comment: Optional[str] = Field(None, description="Commentaire optionnel")


class TemplateConfigurationCreate(TemplateConfigurationBase):
    template_id: int
    configuration_id: int

class TemplateConfigurationUpdate(BaseModel):
    order: Optional[int] = None
    comment: Optional[str] = None


class TemplateConfigurationInDB(TemplateConfigurationBase):
    id: int
    template_id: int
    configuration_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

# ⏳ Lazy imports déjà faits ci-dessus
class TemplateConfigurationPublic(BaseModel):
    id: int
    order: Optional[int] = None
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    template: TemplateShort
    configuration: ConfigurationShort

    class Config:
        from_attributes = True

