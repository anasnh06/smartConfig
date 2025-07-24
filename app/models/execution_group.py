from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base

class ExecutionGroup(Base):
    __tablename__ = "execution_groups"

    id             = Column(Integer, primary_key=True)
    execution_id   = Column(ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    name           = Column(String(100))
    status         = Column(String(20), default="pending")       # pending / running / success / failed
    playbook_path  = Column(String(255), nullable=True)          # rempli au launch
    inventory_path = Column(String(255), nullable=True)
    log_path = Column(String(255), nullable=True)   # tous pour ansible en utilisant paths 
    started_at     = Column(DateTime(timezone=True))
    finished_at    = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(ForeignKey("users.id"), nullable=True)
    updated_by = Column(ForeignKey("users.id"), nullable=True)

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="execution_groups_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="execution_groups_updated")


    execution = relationship(
        "Execution",
        foreign_keys=[execution_id],
        back_populates="execution_groups"
    )

    server_configurations = relationship(
        "ServerConfiguration",
        back_populates="execution_group",
        cascade="all, delete-orphan"
    )