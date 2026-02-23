# core/cache.py

import redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)

async def get_cached_embedding(text_hash: str):
    try:
        data = redis_client.get(f"embedding:{text_hash}")
        if data:
            return json.loads(data)
    except Exception:
        # Redis down → fail gracefully
        return None

    return None


async def set_cached_embedding(text_hash: str, embedding):
    try:
        redis_client.set(
            f"embedding:{text_hash}",
            json.dumps(embedding),
            ex=86400
        )
    except Exception:
        # Redis down → silently ignore
        pass