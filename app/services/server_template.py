from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import ServerTemplate
from app.schemas import ServerTemplateCreate, ServerTemplateUpdate


class ServerTemplateService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, st_id: int, include_related: bool = False) -> Optional[ServerTemplate]:
        query = self.db.query(ServerTemplate)
        if include_related:
            query = query.options(
                joinedload(ServerTemplate.server),
                joinedload(ServerTemplate.template),
                joinedload(ServerTemplate.server_configurations)
            )
        return query.filter(ServerTemplate.id == st_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ServerTemplate]:
        return self.db.query(ServerTemplate).offset(skip).limit(limit).all()

    def create(self, st_in: ServerTemplateCreate, created_by_id: Optional[int] = None) -> ServerTemplate:
        st = ServerTemplate(
            server_id=st_in.server_id,
            template_id=st_in.template_id,
            context=st_in.context,
            created_by=created_by_id
        )
        self.db.add(st)
        self.db.commit()
        self.db.refresh(st)
        return st

    def update(self, st_id: int, st_in: ServerTemplateUpdate, updated_by_id: Optional[int] = None) -> Optional[ServerTemplate]:
        st = self.get_by_id(st_id)
        if not st:
            return None

        update_data = st_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(st, field, value)

        st.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(st)
        return st

    def delete(self, st_id: int) -> bool:
        st = self.get_by_id(st_id)
        if not st:
            return False
        self.db.delete(st)
        self.db.commit()
        return True
