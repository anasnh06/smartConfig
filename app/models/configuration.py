from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db import Base
from .associations import configuration_operating_system

class Configuration(Base):
    __tablename__ = "configurations"

    # Champs classiques
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    command = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    # ForeignKeys (hors utilisateur) → aucun ici

    # Meta utilisateur
    created_by = Column(ForeignKey("users.id"), nullable=True)
    updated_by = Column(ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="configurations_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="configurations_updated"
    )

    # Relations
    operating_systems = relationship(
        "OperatingSystem",
        secondary=configuration_operating_system,
        back_populates="configurations"
    )

    configuration_templates = relationship(
        "TemplateConfiguration",
        back_populates="configuration",
        cascade="all, delete-orphan"
    )

    configuration_servers = relationship(
        "ServerConfiguration",
        back_populates="configuration",
        cascade="all, delete-orphan"
    )

