import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.associations import server_role, server_template, server_configuration


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    ip_address = Column(String(100), nullable=False)
    ssh_port = Column(Integer, default=22)
    ssh_user = Column(String(100), nullable=False)
    ssh_private_key_path = Column(
        String(255),
        default=os.path.expanduser("~/.ssh/id_rsa"),
        nullable=False
    )

    # Foreign keys (meta)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign keys (main)
    operating_system_id = Column(Integer, ForeignKey("operating_systems.id"), nullable=False)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Relationships (back_populates est utilisé pour les accès bidirectionnels)
    operating_system = relationship("OperatingSystem", back_populates="servers")
    environment = relationship("Environment", back_populates="servers")
    project = relationship("Project", back_populates="servers")

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="servers_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="servers_updated")

    roles = relationship("Role", secondary=server_role, back_populates="servers")
    templates = relationship("Template", secondary=server_template, back_populates="servers")
    configurations = relationship("Configuration", secondary=server_configuration, back_populates="servers")
