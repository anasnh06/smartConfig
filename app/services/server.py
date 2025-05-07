from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Server
from app.schemas import ServerCreate, ServerUpdate


class ServerService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, server_id: int) -> Optional[Server]:
        return self.db.query(Server).filter(Server.id == server_id).first()

    def get_by_name(self, name: str) -> Optional[Server]:
        return self.db.query(Server).filter(Server.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Server]:
        return self.db.query(Server).offset(skip).limit(limit).all()

    def create(self, server_in: ServerCreate, created_by_id: Optional[int] = None) -> Server:
        server = Server(
            name=server_in.name,
            ip_address=str(server_in.ip_address),
            ssh_port=server_in.ssh_port,
            ssh_user=server_in.ssh_user,
            ssh_private_key_path=server_in.ssh_private_key_path,
            operating_system_id=server_in.operating_system_id,
            environment_id=server_in.environment_id,
            project_id=server_in.project_id,
            created_by=created_by_id
        )
        self.db.add(server)
        self.db.commit()
        self.db.refresh(server)
        return server

    def update(self, server_id: int, server_in: ServerUpdate, updated_by_id: int) -> Optional[Server]:
        server = self.get_by_id(server_id)
        if not server:
            return None

        update_data = server_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "ip_address":
                value = str(value)
            setattr(server, field, value)

        server.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(server)
        return server

    def delete(self, server_id: int) -> bool:
        server = self.get_by_id(server_id)
        if not server:
            return False
        self.db.delete(server)
        self.db.commit()
        return True
