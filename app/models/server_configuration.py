from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base

class ServerConfiguration(Base):
    __tablename__ = "server_configurations"

    # Champs simples
    id = Column(Integer, primary_key=True)
    status = Column(String(50), nullable=False, default="pending")
    return_code = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(50), nullable=True)  # 'manual' | 'template'

    # Foreign Keys métier
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id", ondelete="CASCADE"), nullable=False)
    execution_id = Column(Integer, ForeignKey("executions.id", ondelete="SET NULL"), nullable=True)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="servers_configurations_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="servers_configurations_updated"
    )

    # Relations métier
    server = relationship(
        "Server",
        foreign_keys=[server_id],
        back_populates="server_configurations"
    )

    configuration = relationship(
        "Configuration",
        foreign_keys=[configuration_id],
        back_populates="configuration_servers"
    )

    # future
    # execution = relationship(
    #     "Execution",
    #     foreign_keys=[execution_id],
    #     back_populates="server_configurations"
    # )
