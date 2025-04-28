from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.db import Base

class Environment(Base):
    __tablename__ = "environments"

    # Champs simples
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # ForeignKeys (aucune autre que User ici)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="environments_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="environments_updated"
    )

    # Relations métier
    servers = relationship(
        "Server",
        back_populates="environment",
        cascade="all, delete-orphan"
    )
