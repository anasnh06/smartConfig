from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import ServerConfiguration
from app.schemas import ServerConfigurationCreate, ServerConfigurationUpdate


class ServerConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sc_id: int, include_related: bool = False) -> Optional[ServerConfiguration]:
        query = self.db.query(ServerConfiguration)
        if include_related:
            query = query.options(
                joinedload(ServerConfiguration.server),
                joinedload(ServerConfiguration.configuration),
                joinedload(ServerConfiguration.server_template),
                joinedload(ServerConfiguration.execution_group),
                joinedload(ServerConfiguration.created_by_user),
                joinedload(ServerConfiguration.updated_by_user),
            )
        return query.filter(ServerConfiguration.id == sc_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ServerConfiguration]:
        """
        📄 Liste paginée de toutes les liaisons serveur-configuration avec relations chargées.
        """
        return (
            self.db.query(ServerConfiguration)
            .options(
                joinedload(ServerConfiguration.server),
                joinedload(ServerConfiguration.configuration),
                joinedload(ServerConfiguration.server_template),
                joinedload(ServerConfiguration.execution_group),
                joinedload(ServerConfiguration.created_by_user),
                joinedload(ServerConfiguration.updated_by_user),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, sc_in: ServerConfigurationCreate, created_by_id: Optional[int] = None) -> ServerConfiguration:
        sc = ServerConfiguration(
            server_id=sc_in.server_id,
            execution_group_id=sc_in.execution_group_id,
            configuration_id=sc_in.configuration_id,
            server_template_id=sc_in.server_template_id,
            custom_command=sc_in.custom_command,
            source=sc_in.source,
            status=sc_in.status or "pending",
            return_code=sc_in.return_code,
            output=sc_in.output,
            started_at=sc_in.started_at,
            finished_at=sc_in.finished_at,
            created_by=created_by_id
        )
        self.db.add(sc)
        self.db.commit()
        self.db.refresh(sc)
        return sc

    def update(self, sc_id: int, sc_in: ServerConfigurationUpdate, updated_by_id: Optional[int] = None) -> Optional[ServerConfiguration]:
        sc = self.get_by_id(sc_id)
        if not sc:
            return None

        update_data = sc_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sc, field, value)

        sc.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(sc)
        return sc

    def delete(self, sc_id: int) -> bool:
        sc = self.get_by_id(sc_id)
        if not sc:
            return False
        self.db.delete(sc)
        self.db.commit()
        return True
