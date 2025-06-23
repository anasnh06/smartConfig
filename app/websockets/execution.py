from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets.manager import manager

router = APIRouter()

@router.websocket("/execution/{execution_id}")
async def websocket_execution(websocket: WebSocket, execution_id: int):
    """
    📱 WebSocket endpoint permettant aux clients de s'abonner à une exécution pour recevoir les mises à jour en temps réel.
    
    Reçoit les événements envoyés via `manager.broadcast_json(execution_id, {...})`.
    """
    await manager.connect(execution_id, websocket)
    try:
        while True:
            # Si le client envoie un message (utile pour les ping ou actions futures)
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(execution_id, websocket)
