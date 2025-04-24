from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from .user import User
from .role import Role
from .configuration import Configuration
from .os import OperatingSystem
from .associations import template_configuration, template_operating_system

class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign Keys
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id"), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="templates")

    configurations: Mapped[list["Configuration"]] = relationship(
        "Configuration",
        secondary=template_configuration,
        back_populates="templates"
    )

    operating_systems: Mapped[list["OperatingSystem"]] = relationship(
        "OperatingSystem",
        secondary=template_operating_system,
        back_populates="templates"
    )

    created_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    updated_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by])
