from typing import Dict, Set
from fastapi import WebSocket
from asyncio import Lock
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Gère toutes les connexions WebSocket groupées par execution_id.
    Permet de diffuser en temps réel tous les événements liés à une exécution (groupes, serveurs, statut global...).
    """

    def __init__(self):
        # Dictionnaire des connexions actives par execution_id
        self.connections: Dict[int, Set[WebSocket]] = {}
        self.lock = Lock()

    async def connect(self, execution_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            if execution_id not in self.connections:
                self.connections[execution_id] = set()
            self.connections[execution_id].add(websocket)
        logger.info(f"🔌 WebSocket connecté : execution_id={execution_id} (total={len(self.connections[execution_id])})")

    async def disconnect(self, execution_id: int, websocket: WebSocket):
        async with self.lock:
            if execution_id in self.connections:
                self.connections[execution_id].discard(websocket)
                if not self.connections[execution_id]:
                    del self.connections[execution_id]
        logger.info(f"❌ WebSocket déconnecté : execution_id={execution_id}")

    async def broadcast_json(self, execution_id: int, message: dict):
        """
        Envoie un message JSON à tous les clients connectés à une execution_id donnée.
        """
        async with self.lock:
            clients = self.connections.get(execution_id, set()).copy()

        if not clients:
            logger.debug(f"⚠️ Aucun client connecté pour execution_id={execution_id}, message ignoré : {message}")
            return

        disconnected = set()
        for ws in clients:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"⚠️ WebSocket envoi échoué → suppression : {e}")
                disconnected.add(ws)

        # Nettoyage
        async with self.lock:
            for ws in disconnected:
                self.connections[execution_id].discard(ws)

# Instance globale à importer
manager = WebSocketManager()
