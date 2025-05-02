from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.db import Base
from .associations import configuration_operating_system, template_operating_system

class OperatingSystem(Base):
    __tablename__ = "operating_systems"

    # Champs simples
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # e.g., Ubuntu
    version = Column(String(50), nullable=True)  # e.g., 20.04

    # ForeignKeys (aucune autre que User ici)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="operating_systems_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="operating_systems_updated"
    )

    # Relations métier
    servers = relationship(
        "Server",
        back_populates="operating_system",
        cascade="all, delete-orphan"
    )

    configurations = relationship(
        "Configuration",
        secondary=configuration_operating_system,
        back_populates="operating_systems"
    )

    templates = relationship(
        "Template",
        secondary=template_operating_system,
        back_populates="operating_systems"
    )
