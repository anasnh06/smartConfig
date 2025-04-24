from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base

class Environment(Base):
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 🔁 Relations utilisateur (audit trail)
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="environments_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="environments_updated")

    # 🔗 Relation one-to-many avec Server
    servers = relationship("Server", back_populates="environment", cascade="all, delete-orphan")
