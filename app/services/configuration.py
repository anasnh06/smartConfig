from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import Configuration
from app.schemas import ConfigurationCreate, ConfigurationUpdate


class ConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, configuration_id: int, include_related: bool = False) -> Optional[Configuration]:
        """
        🔎 Récupère une configuration par son ID, avec ou sans relations.
        """
        query = self.db.query(Configuration)
        if include_related:
            query = query.options(
                joinedload(Configuration.operating_systems),
                joinedload(Configuration.configuration_servers),
                joinedload(Configuration.configuration_templates),
                joinedload(Configuration.created_by_user),
                joinedload(Configuration.updated_by_user)
            )
        return query.filter(Configuration.id == configuration_id).first()

    def get_by_name(self, name: str) -> Optional[Configuration]:
        """
        🔎 Récupère une configuration par son nom.
        """
        return self.db.query(Configuration).filter(Configuration.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Configuration]:
        """
        📄 Liste paginée de toutes les configurations.
        """
        return self.db.query(Configuration).offset(skip).limit(limit).all()

    def create(self, configuration_in: ConfigurationCreate, created_by_id: Optional[int] = None) -> Configuration:
        """
        ✅ Crée une nouvelle configuration.
        """
        configuration = Configuration(
            name=configuration_in.name,
            command=configuration_in.command,
            description=configuration_in.description,
            created_by=created_by_id
        )
        self.db.add(configuration)

        # Ajout des OS compatibles (many-to-many simple)
        if configuration_in.operating_system_ids:
            configuration.operating_systems = self.db.query(
                Configuration.operating_systems.property.mapper.class_
            ).filter(
                Configuration.operating_systems.property.secondary.c.operating_system_id.in_(
                    configuration_in.operating_system_ids
                )
            ).all()

        self.db.commit()
        self.db.refresh(configuration)
        return configuration

    def update(self, configuration_id: int, configuration_in: ConfigurationUpdate, updated_by_id: Optional[int] = None) -> Optional[Configuration]:
        """
        ✏️ Met à jour une configuration existante.
        """
        configuration = self.get_by_id(configuration_id)
        if not configuration:
            return None

        update_data = configuration_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "operating_system_ids":
                os_list = self.db.query(
                    Configuration.operating_systems.property.mapper.class_
                ).filter(
                    Configuration.operating_systems.property.secondary.c.operating_system_id.in_(value)
                ).all()
                configuration.operating_systems = os_list
            else:
                setattr(configuration, field, value)

        configuration.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(configuration)
        return configuration

    def delete(self, configuration_id: int) -> bool:
        """
        🗑 Supprime une configuration par son ID.
        """
        configuration = self.get_by_id(configuration_id)
        if not configuration:
            return False
        self.db.delete(configuration)
        self.db.commit()
        return True
