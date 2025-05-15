from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import OperatingSystem
from app.schemas import OperatingSystemCreate, OperatingSystemUpdate


class OperatingSystemService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, os_id: int, include_related: bool = False) -> Optional[OperatingSystem]:
        query = self.db.query(OperatingSystem)
        if include_related:
            query = query.options(
                joinedload(OperatingSystem.servers),
                joinedload(OperatingSystem.configurations),
                joinedload(OperatingSystem.templates),
                joinedload(OperatingSystem.created_by_user),
                joinedload(OperatingSystem.updated_by_user),
            )
        return query.filter(OperatingSystem.id == os_id).first()
    
    def get_by_name(self, name: str) -> Optional[OperatingSystem]:
        return self.db.query(OperatingSystem).filter(OperatingSystem.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[OperatingSystem]:
        return self.db.query(OperatingSystem).offset(skip).limit(limit).all()

    def create(self, os_in: OperatingSystemCreate, created_by_id: Optional[int] = None) -> OperatingSystem:
        os = OperatingSystem(
            name=os_in.name,
            version=os_in.version,
            created_by=created_by_id
        )
        self.db.add(os)
        self.db.commit()
        self.db.refresh(os)
        return os

    def update(self, os_id: int, os_in: OperatingSystemUpdate, updated_by_id: Optional[int] = None) -> Optional[OperatingSystem]:
        os = self.get_by_id(os_id)
        if not os:
            return None

        update_data = os_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(os, field, value)

        os.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(os)
        return os

    def delete(self, os_id: int) -> bool:
        os = self.get_by_id(os_id)
        if not os:
            return False
        self.db.delete(os)
        self.db.commit()
        return True
