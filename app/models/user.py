from typing import Optional, List
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ✅ Relations SELF (auto-références)
    creator = relationship("User", remote_side=[id], foreign_keys=[created_by])
    updater = relationship("User", remote_side=[id], foreign_keys=[updated_by])

    # ✅ Relations inverses avec toutes les entités qui ont "created_by" / "updated_by"
    servers_created = relationship("Server", back_populates="created_by_user", foreign_keys="Server.created_by")
    servers_updated = relationship("Server", back_populates="updated_by_user", foreign_keys="Server.updated_by")

    projects_created = relationship("Project", back_populates="created_by_user", foreign_keys="Project.created_by")
    projects_updated = relationship("Project", back_populates="updated_by_user", foreign_keys="Project.updated_by")

    configurations_created = relationship("Configuration", back_populates="created_by_user", foreign_keys="Configuration.created_by")
    configurations_updated = relationship("Configuration", back_populates="updated_by_user", foreign_keys="Configuration.updated_by")

    environments_created = relationship("Environment", back_populates="created_by_user", foreign_keys="Environment.created_by")
    environments_updated = relationship("Environment", back_populates="updated_by_user", foreign_keys="Environment.updated_by")

    roles_created = relationship("Role", back_populates="created_by_user", foreign_keys="Role.created_by")
    roles_updated = relationship("Role", back_populates="updated_by_user", foreign_keys="Role.updated_by")

    operating_systems_created = relationship("OperatingSystem", back_populates="created_by_user", foreign_keys="OperatingSystem.created_by")
    operating_systems_updated = relationship("OperatingSystem", back_populates="updated_by_user", foreign_keys="OperatingSystem.updated_by")

    templates_created = relationship("Template", back_populates="created_by_user", foreign_keys="Template.created_by")
    templates_updated = relationship("Template", back_populates="updated_by_user", foreign_keys="Template.updated_by")
