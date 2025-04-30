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
    started_at     = Column(DateTime(timezone=True))
    finished_at    = Column(DateTime(timezone=True))

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