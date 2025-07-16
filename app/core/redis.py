import redis.asyncio as aioredis
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


# Vérifie que settings.redis_url contient bien l'URL de Redis
redis_client = aioredis.from_url(
    settings.redis_url,
    decode_responses=True,  # ✅ string au lieu de bytes
)

def get_redis_client():
    """
    Fournit le client Redis global (asyncio).
    À utiliser dans services, websockets, etc.
    """
    return redis_client

async def publish_ws_event(execution_id: int, message: dict):
    """
    📡 Publie un message JSON dans Redis (canal `execution:{id}`) pour les WebSockets.
    Utilisé dans `ExecutionRunnerService` pour notifier le frontend via Redis Pub/Sub.
    """
    try:
        channel = f"execution:{execution_id}"
        payload = json.dumps(message)
        await redis_client.publish(channel, payload)
        logger.info(f"📨 Redis → Published on {channel}: {payload}")
    except Exception as e:
        logger.error(f"❌ Redis publish failed for execution {execution_id}: {e}")
