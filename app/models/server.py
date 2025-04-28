import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base
from .associations import server_role

class Server(Base):
    __tablename__ = "servers"

    # Champs simples
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

    # Foreign Keys métier
    operating_system_id = Column(Integer, ForeignKey("operating_systems.id"), nullable=False)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relations utilisateur
    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="servers_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="servers_updated"
    )

    # Relations métier avec foreign_keys explicites
    operating_system = relationship(
        "OperatingSystem",
        foreign_keys=[operating_system_id],
        back_populates="servers"
    )

    environment = relationship(
        "Environment",
        foreign_keys=[environment_id],
        back_populates="servers"
    )

    project = relationship(
        "Project",
        foreign_keys=[project_id],
        back_populates="servers"
    )

    roles = relationship(
        "Role",
        secondary=server_role,
        back_populates="servers"
    )

    
    server_configurations= relationship(
        "ServerConfiguration",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    server_templates = relationship(
        "ServerTemplate",
        back_populates="server",
        cascade="all, delete-orphan"
    )
