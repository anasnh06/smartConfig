import asyncio
import json
import logging
from redis.asyncio import Redis
from app.core.redis import get_redis_client
from app.websockets.manager import manager

logger = logging.getLogger(__name__)

async def _run_redis_listener(pubsub):
    async for message in pubsub.listen():
        if message is None:
            continue

        if message.get("type") not in {"message", "pmessage"}:
            continue

        try:
            data = json.loads(message["data"])
            channel = message.get("channel") or message.get("pattern")
            if isinstance(channel, bytes):
                channel = channel.decode()

            if ":" in channel:
                execution_id = int(channel.split(":")[1])
                await manager.broadcast_json(execution_id, data)
                logger.info(f"📤 Redis → WS : execution_id={execution_id}, data={data}")
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement message Redis → WS : {e}")

async def subscribe_to_redis():
    redis: Redis = get_redis_client()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("execution:*")
    logger.info("📡 Abonnement Redis prêt : execution:*")

    # Lancer l'écoute dans une tâche dédiée (non bloquante)
    asyncio.create_task(_run_redis_listener(pubsub))
