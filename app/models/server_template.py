from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base

class ServerTemplate(Base):
    __tablename__ = "server_templates"

    # Champs simples
    id = Column(Integer, primary_key=True)
    status = Column(String(20), default="pending")          # pending / running / success / failed / partial
    started_at     = Column(DateTime(timezone=True))
    finished_at    = Column(DateTime(timezone=True))

    # Foreign Keys métier
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    

    # Relations utilisateur
    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="servers_templates_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="servers_templates_updated"
    )

    # Relations métier
    server = relationship(
        "Server",
        foreign_keys=[server_id],
        back_populates="server_templates"
    )

    template = relationship(
        "Template",
        foreign_keys=[template_id],
        back_populates="template_servers"
    )

    server_configurations = relationship(
        "ServerConfiguration",
        back_populates="server_template"
    )
