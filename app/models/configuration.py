from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from .associations import configuration_operating_system, template_configuration, server_configuration

class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer,primary_key=True)
    name = Column(String(100), nullable=False)
    command = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    # Meta
    created_by = Column(ForeignKey("users.id"), nullable=True)
    updated_by = Column(ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="configurations_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="configurations_updated")

    # Relations Many-to-Many
    operating_systems = relationship(
        "OperatingSystem",
        secondary=configuration_operating_system,
        back_populates="configurations"
    )

    templates = relationship(
        "Template",
        secondary=template_configuration,
        back_populates="configurations"
    )

    servers = relationship(
        "Server",
        secondary=server_configuration,
        back_populates="configurations"
    )
