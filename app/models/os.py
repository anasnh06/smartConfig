from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.db import Base
from .associations import configuration_operating_system, template_operating_system

class OperatingSystem(Base):
    __tablename__ = "operating_systems"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # e.g., Ubuntu
    version = Column(String(50), nullable=True)  # e.g., 20.04

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 🔁 Relations utilisateur (optionnelles si tu veux tracer)
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="operating_systems_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="operating_systems_updated")

    # 🔁 Relation One-to-Many avec Server
    servers = relationship("Server", back_populates="operating_system", cascade="all, delete-orphan")

    # 🔁 Relation Many-to-Many avec Configuration
    configurations = relationship(
        "Configuration",
        secondary=configuration_operating_system,
        back_populates="operating_systems",
    )

    # 🔁 Relation Many-to-Many avec Template
    templates = relationship(
        "Template",
        secondary=template_operating_system,
        back_populates="operating_systems",
    )
