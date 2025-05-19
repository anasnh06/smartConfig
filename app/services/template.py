from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import Template, Role, OperatingSystem
from app.schemas import TemplateCreate, TemplateUpdate


class TemplateService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, template_id: int, include_related: bool = False) -> Optional[Template]:
        query = self.db.query(Template)
        if include_related:
            query = query.options(
                joinedload(Template.role),
                joinedload(Template.operating_systems),
                joinedload(Template.template_configurations),
                joinedload(Template.template_servers),
                joinedload(Template.created_by_user),
                joinedload(Template.updated_by_user),
            )
        return query.filter(Template.id == template_id).first()

    def get_by_name(self, name: str) -> Optional[Template]:
        return self.db.query(Template).filter(Template.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Template]:
        return self.db.query(Template).offset(skip).limit(limit).all()

    def create(self, template_in: TemplateCreate, created_by_id: Optional[int] = None) -> Template:
        template = Template(
            name=template_in.name,
            description=template_in.description,
            role_id=template_in.role_id,
            created_by=created_by_id
        )

        # OS compatibles (many-to-many)
        if template_in.operating_system_ids:
            template.operating_systems = self.db.query(OperatingSystem).filter(
                OperatingSystem.id.in_(template_in.operating_system_ids)
            ).all()

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template_id: int, template_in: TemplateUpdate, updated_by_id: Optional[int] = None) -> Optional[Template]:
        template = self.get_by_id(template_id)
        if not template:
            return None

        update_data = template_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "operating_system_ids":
                template.operating_systems = self.db.query(OperatingSystem).filter(
                    OperatingSystem.id.in_(value)
                ).all()
            else:
                setattr(template, field, value)

        template.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template_id: int) -> bool:
        template = self.get_by_id(template_id)
        if not template:
            return False
        self.db.delete(template)
        self.db.commit()
        return True
