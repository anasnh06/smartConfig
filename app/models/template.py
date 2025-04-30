from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Integer, func
from sqlalchemy.orm import relationship

from app.db import Base
from .associations import template_operating_system

class Template(Base):
    __tablename__ = "templates"

    # Champs simples
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Foreign Keys
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="templates_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="templates_updated"
    )

    # Relations métier
    role = relationship(
        "Role",
        foreign_keys=[role_id],
        back_populates="templates"
    )
    operating_systems = relationship(
        "OperatingSystem",
        secondary=template_operating_system,
        back_populates="templates"
    )

    
    template_configurations= relationship(
        "TemplateConfiguration",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateConfiguration.order"
    )

    
    template_servers = relationship(
        "ServerTemplate",
        back_populates="template",
        cascade="all, delete-orphan"
    )