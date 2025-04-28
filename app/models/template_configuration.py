from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base

class TemplateConfiguration(Base):
    __tablename__ = "template_configurations"

    # Champs simples
    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)

    # Foreign Keys métier
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id", ondelete="CASCADE"), nullable=False)

    # Meta utilisateur
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relations utilisateur
    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="templates_configurations_created"
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="templates_configurations_updated"
    )

    # Relations métier
    template = relationship(
        "Template",
        foreign_keys=[template_id],
        back_populates="template_configurations"
    )

    configuration = relationship(
        "Configuration",
        foreign_keys=[configuration_id],
        back_populates="configuration_templates"
    )
