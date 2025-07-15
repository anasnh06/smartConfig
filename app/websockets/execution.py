from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import manager

router = APIRouter()

@router.websocket("/executions/{execution_id}")
async def websocket_execution(websocket: WebSocket, execution_id: int):
    """
    📱 WebSocket endpoint permettant aux clients de s'abonner à une exécution pour recevoir les mises à jour en temps réel.
    Reçoit les événements envoyés via manager.broadcast_json(execution_id, {...})
    """
    await manager.connect(execution_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # utile pour garder la connexion vivante
    except WebSocketDisconnect:
        await manager.disconnect(execution_id, websocket)
