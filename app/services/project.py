from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: int, include_related: bool = False) -> Optional[Project]:
        query = self.db.query(Project)
        if include_related:
            query = query.options(joinedload(Project.servers),
                                  joinedload(Project.created_by_user),
                                  joinedload(Project.updated_by_user),
            )
        return query.filter(Project.id == project_id).first()

    def get_by_name(self, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.db.query(Project).offset(skip).limit(limit).all()

    def create(self, project_in: ProjectCreate, created_by_id: Optional[int] = None) -> Project:
        project = Project(
            name=project_in.name,
            description=project_in.description,
            created_by=created_by_id
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id: int, project_in: ProjectUpdate, updated_by_id: int) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None

        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        project = self.get_by_id(project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True
