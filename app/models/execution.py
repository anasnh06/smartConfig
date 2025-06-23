from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base


class Execution(Base):
    __tablename__ = "executions"

    # Champs simples
    id          = Column(Integer, primary_key=True)
    title       = Column(String(120), nullable=True)
    status      = Column(String(20), default="draft")            # draft / running / success / failed / partial
    started_at  = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))

    # Audit utilisateur
    created_by = Column(ForeignKey("users.id"), nullable=True)
    updated_by = Column(ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="executions_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="executions_updated")

    replayed_from_id = Column(Integer, ForeignKey("executions.id"), nullable=True)
    replayed_from = relationship("Execution", remote_side=[id])


    # Relations
    execution_groups = relationship(
        "ExecutionGroup",
        back_populates="execution",
        cascade="all, delete-orphan"
    )