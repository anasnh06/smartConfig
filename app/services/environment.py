from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import Environment
from app.schemas import EnvironmentCreate, EnvironmentUpdate


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, environment_id: int, include_related: bool = False) -> Optional[Environment]:
        query = self.db.query(Environment)
        if include_related:
            query = query.options(
                joinedload(Environment.servers),
                joinedload(Environment.created_by_user),
                joinedload(Environment.updated_by_user)
            )
        return query.filter(Environment.id == environment_id).first()

    def get_by_name(self, name: str) -> Optional[Environment]:
        return self.db.query(Environment).filter(Environment.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Environment]:
        return self.db.query(Environment).offset(skip).limit(limit).all()

    def create(self, environment_in: EnvironmentCreate, created_by_id: Optional[int] = None) -> Environment:
        environment = Environment(
            name=environment_in.name,
            created_by=created_by_id
        )
        self.db.add(environment)
        self.db.commit()
        self.db.refresh(environment)
        return environment

    def update(self, environment_id: int, environment_in: EnvironmentUpdate, updated_by_id: int) -> Optional[Environment]:
        environment = self.get_by_id(environment_id)
        if not environment:
            return None

        update_data = environment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(environment, field, value)

        environment.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(environment)
        return environment

    def delete(self, environment_id: int) -> bool:
        environment = self.get_by_id(environment_id)
        if not environment:
            return False
        self.db.delete(environment)
        self.db.commit()
        return True
