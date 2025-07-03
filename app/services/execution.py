from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import Execution
from app.schemas import ExecutionCreate, ExecutionUpdate


class ExecutionService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, execution_id: int, include_related: bool = False) -> Optional[Execution]:
        query = self.db.query(Execution)
        if include_related:
            query = query.options(
                joinedload(Execution.execution_groups),
                joinedload(Execution.created_by_user),
                joinedload(Execution.updated_by_user),
            )
        return query.filter(Execution.id == execution_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Execution]:
        """
        📄 Liste paginée de toutes les exécutions, avec relations chargées.
        """
        return (
            self.db.query(Execution)
            .options(
                joinedload(Execution.execution_groups),
                joinedload(Execution.created_by_user),
                joinedload(Execution.updated_by_user),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_short(self) -> List[Execution]:
        """
        📋 Liste brute de toutes les exécutions (sans relations).
        """
        return self.db.query(Execution).all()

    def create(self, execution_in: ExecutionCreate, created_by_id: Optional[int] = None) -> Execution:
        execution = Execution(
            title=execution_in.title,
            status=execution_in.status,
            created_by=created_by_id
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def update(self, execution_id: int, execution_in: ExecutionUpdate, updated_by_id: Optional[int] = None) -> Optional[Execution]:
        execution = self.get_by_id(execution_id)
        if not execution:
            return None

        update_data = execution_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(execution, field, value)

        execution.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def delete(self, execution_id: int) -> bool:
        execution = self.get_by_id(execution_id)
        if not execution:
            return False
        self.db.delete(execution)
        self.db.commit()
        return True
