from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.db import Base
from .associations import server_role

class Role(Base):
    __tablename__ = "roles"

    # Champs simples
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # ForeignKeys (hors User) → aucun ici

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="roles_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="roles_updated"
    )

    # Relations métier
    servers = relationship(
        "Server",
        secondary=server_role,
        back_populates="roles"
    )

    templates = relationship(
        "Template",
        back_populates="role",
        cascade="all, delete-orphan"
    )
