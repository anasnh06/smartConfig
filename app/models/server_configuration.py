from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base

class ServerConfiguration(Base):
    __tablename__ = "server_configurations"

    id = Column(Integer, primary_key=True)

    # Statut d'exécution
    status = Column(String(20), default="pending")          # pending / running / success / failed
    return_code = Column(Integer)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    log_path = Column(String(255), nullable=True)                                 # stdout/stderr concaténés ou JSON compacté
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    source = Column(String(20))     # manual / template / custom

    # Liens métier
    server_id            = Column(ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    execution_group_id   = Column(ForeignKey("execution_groups.id", ondelete="CASCADE"), nullable=False)
    configuration_id     = Column(ForeignKey("configurations.id", ondelete="SET NULL"))
    server_template_id   = Column(ForeignKey("server_templates.id", ondelete="SET NULL"))
    custom_command       = Column(String, nullable=True)         # si commande libre

    

    # Relations principales
    server          = relationship("Server", back_populates="server_configurations", foreign_keys=[server_id])
    execution_group = relationship("ExecutionGroup", back_populates="server_configurations", foreign_keys=[execution_group_id])
    configuration   = relationship("Configuration", back_populates="configuration_servers", foreign_keys=[configuration_id])
    server_template = relationship("ServerTemplate", back_populates="server_configurations", foreign_keys=[server_template_id])

    # Audit utilisateur
    created_by = Column(ForeignKey("users.id"), nullable=True)
    updated_by = Column(ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="servers_configurations_created")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="servers_configurations_updated")
