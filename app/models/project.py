from typing import Optional
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # One-to-many avec Server
    servers = relationship("Server", back_populates="project", cascade="all, delete-orphan")

    # Relations vers User
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="projects_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="projects_updated")
