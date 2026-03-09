import os
import json
import logging
import redis.asyncio as redis
from typing import Optional, List
from .models import RoomState
from .constants import REDIS_TTL

logger = logging.getLogger(__name__)

class RedisRoomStore:
    def __init__(self):
        self.url = os.getenv("REDIS_URL")
        self.redis = None
        self.in_memory = {}  # fallback if redis is down or not configured
        
    async def init_redis(self):
        if self.url:
            try:
                self.redis = redis.from_url(self.url, decode_responses=False)
                await self.redis.ping()
                logger.info("Connected to Async Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Falling back to in-memory.")
                self.redis = None
        else:
            logger.info("REDIS_URL not set. Using in-memory store.")

    async def get(self, room_id: str) -> Optional[RoomState]:
        if self.redis:
            try:
                data = await self.redis.get(f"room:{room_id}")
                if data:
                    return RoomState.model_validate_json(data)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        return self.in_memory.get(room_id)

    async def set(self, room_id: str, state: RoomState):
        if self.redis:
            try:
                await self.redis.setex(
                    f"room:{room_id}",
                    REDIS_TTL,
                    state.model_dump_json()
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        self.in_memory[room_id] = state

    async def delete(self, room_id: str):
        if self.redis:
            try:
                await self.redis.delete(f"room:{room_id}")
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if room_id in self.in_memory:
            del self.in_memory[room_id]

    async def list_rooms(self) -> List[str]:
        if self.redis:
            try:
                keys = await self.redis.keys("room:*")
                return [k.decode('utf-8').split(":", 1)[1] for k in keys]
            except Exception as e:
                logger.error(f"Redis keys error: {e}")
        
        return list(self.in_memory.keys())

# Global instance
room_store = RedisRoomStore()
