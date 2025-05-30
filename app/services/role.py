from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import Role, User
from app.schemas import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, role_id: int, include_related: bool = False) -> Optional[Role]:
        query = self.db.query(Role)
        if include_related:
            query = query.options(
                joinedload(Role.servers),
                joinedload(Role.templates),
                joinedload(Role.created_by_user),
                joinedload(Role.updated_by_user)
            )
        return query.filter(Role.id == role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100, include_related: bool = False) -> List[Role]:
        query = self.db.query(Role)
        if include_related:
            query = query.options(
                joinedload(Role.servers),
                joinedload(Role.templates),
                joinedload(Role.created_by_user),
                joinedload(Role.updated_by_user),
            )
        return query.offset(skip).limit(limit).all()


    def create(self, role_in: RoleCreate, created_by_id: Optional[int] = None) -> Role:
        role = Role(
            name=role_in.name,
            description=role_in.description,
            created_by=created_by_id
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role_id: int, role_in: RoleUpdate, updated_by_id: Optional[int]) -> Optional[Role]:
        role = self.get_by_id(role_id)
        if not role:
            return None

        update_data = role_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)

        role.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role_id: int) -> bool:
        role = self.get_by_id(role_id)
        if not role:
            return False
        self.db.delete(role)
        self.db.commit()
        return True
