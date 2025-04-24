from sqlalchemy import Table, Column, ForeignKey, Integer
from app.db import Base

# Server <-> Role
server_role = Table(
    "server_role",
    Base.metadata,
    Column("server_id", ForeignKey("servers.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Server <-> Configuration
server_configuration = Table(
    "server_configuration",
    Base.metadata,
    Column("server_id", ForeignKey("servers.id", ondelete="CASCADE"), primary_key=True),
    Column("configuration_id", ForeignKey("configurations.id", ondelete="CASCADE"), primary_key=True),
)

# Server <-> Template
server_template = Table(
    "server_template",
    Base.metadata,
    Column("server_id", ForeignKey("servers.id", ondelete="CASCADE"), primary_key=True),
    Column("template_id", ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
)


# Configuration <-> OperatingSystem (Many-to-Many)
configuration_operating_system = Table(
    "configuration_operating_system",
    Base.metadata,
    Column("configuration_id", ForeignKey("configurations.id", ondelete="CASCADE"), primary_key=True),
    Column("operating_system_id", ForeignKey("operating_systems.id", ondelete="CASCADE"), primary_key=True),
)

# Configuration <-> Template (Many-to-Many)
template_configuration = Table(
    "template_configuration",
    Base.metadata,
    Column("template_id", ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
    Column("configuration_id", ForeignKey("configurations.id", ondelete="CASCADE"), primary_key=True),
)

# Template <-> Configuration (Many-to-Many)
template_operating_system = Table(
    "template_operating_system",
    Base.metadata,
    Column("template_id", ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
    Column("operating_system_id", ForeignKey("operating_systems.id", ondelete="CASCADE"), primary_key=True),
)


