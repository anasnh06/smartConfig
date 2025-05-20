from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import ExecutionGroup
from app.schemas import ExecutionGroupCreate, ExecutionGroupUpdate


class ExecutionGroupService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, eg_id: int, include_related: bool = False) -> Optional[ExecutionGroup]:
        query = self.db.query(ExecutionGroup)
        if include_related:
            query = query.options(
                joinedload(ExecutionGroup.execution),
                joinedload(ExecutionGroup.server_configurations),
                joinedload(ExecutionGroup.created_by_user),
                joinedload(ExecutionGroup.updated_by_user),
            )
        return query.filter(ExecutionGroup.id == eg_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ExecutionGroup]:
        return self.db.query(ExecutionGroup).offset(skip).limit(limit).all()

    def create(self, eg_in: ExecutionGroupCreate, created_by_id: Optional[int] = None) -> ExecutionGroup:
        eg = ExecutionGroup(
            name=eg_in.name,
            status=eg_in.status,
            execution_id=eg_in.execution_id,
            created_by=created_by_id
        )
        self.db.add(eg)
        self.db.commit()
        self.db.refresh(eg)
        return eg

    def update(self, eg_id: int, eg_in: ExecutionGroupUpdate, updated_by_id: Optional[int] = None) -> Optional[ExecutionGroup]:
        eg = self.get_by_id(eg_id)
        if not eg:
            return None

        update_data = eg_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(eg, field, value)

        eg.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(eg)
        return eg

    def delete(self, eg_id: int) -> bool:
        eg = self.get_by_id(eg_id)
        if not eg:
            return False
        self.db.delete(eg)
        self.db.commit()
        return True
