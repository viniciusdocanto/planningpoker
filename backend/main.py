# Planning Poker Backend - MIT License - (c) 2026 Vinicius do Canto
import re
import os
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional

import asyncio
import logging

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants / Limits ---
CLEANUP_INTERVAL  = 30 * 60   # Check every 30 minutes
INACTIVE_TIMEOUT  = 2 * 60 * 60  # 2 hours of inactivity
REDIS_TTL         = INACTIVE_TIMEOUT  # Redis key TTL mirrors the GC timeout
MAX_ROOM_ID_LEN   = 40
MAX_USERNAME_LEN  = 30
MAX_VOTE_LEN      = 4      # longest valid card is "☕" (4 bytes)
MAX_USERS_PER_ROOM = 20
VALID_NAME_RE     = re.compile(r'^[a-zA-ZÀ-ÿ0-9\s\-\.]{1,30}$', re.UNICODE)
VALID_ROOM_RE     = re.compile(r'^[A-Za-z0-9\-_]{1,40}$')
ALLOWED_VOTES     = {'0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕'}
RATE_LIMIT_MSGS   = 10      # max messages per window
RATE_LIMIT_WINDOW = 1.0     # window size in seconds

app = FastAPI()


# ---------------------------------------------------------------------------
# Redis Room Store
# ---------------------------------------------------------------------------

class RedisRoomStore:
    """
    Persists room state to Redis.
    Falls back transparently to an in-memory dict when REDIS_URL is not set,
    keeping the app fully functional in development and simple deployments.
    """

    def __init__(self):
        self._redis = None
        self._memory: Dict[str, dict] = {}  # fallback
        self._use_redis = False

    async def init(self):
        redis_url = os.getenv("REDIS_URL", "")
        if not redis_url:
            logger.warning("⚠️  REDIS_URL not set — using in-memory store (state lost on restart).")
            return

        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(redis_url, decode_responses=True)
            await self._redis.ping()
            self._use_redis = True
            logger.info("✅ Redis connected — room state will persist across restarts.")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}. Falling back to in-memory store.")
            self._redis = None

    async def get(self, room_id: str) -> Optional[dict]:
        if self._use_redis and self._redis:
            raw = await self._redis.get(f"room:{room_id}")
            return json.loads(raw) if raw else None
        return self._memory.get(room_id)

    async def set(self, room_id: str, state: dict):
        if self._use_redis and self._redis:
            await self._redis.set(
                f"room:{room_id}",
                json.dumps(state),
                ex=REDIS_TTL
            )
        else:
            self._memory[room_id] = state

    async def delete(self, room_id: str):
        if self._use_redis and self._redis:
            await self._redis.delete(f"room:{room_id}")
        else:
            self._memory.pop(room_id, None)

    async def all_room_ids(self) -> List[str]:
        """Returns all active room IDs (used by the GC for in-memory fallback)."""
        if self._use_redis and self._redis:
            keys = await self._redis.keys("room:*")
            return [k.removeprefix("room:") for k in keys]
        return list(self._memory.keys())


store = RedisRoomStore()


# ---------------------------------------------------------------------------
# Startup / Cleanup
# ---------------------------------------------------------------------------

async def cleanup_inactive_rooms():
    """
    Background task that removes rooms inactive for 2+ hours.
    When Redis is used, the TTL handles expiration automatically, so this
    task only needs to act on the in-memory fallback.
    """
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)

        if store._use_redis:
            # Redis TTL takes care of expiring keys — we only need to close
            # any live WebSocket connections that belong to expired rooms.
            active_rooms = set(manager.active_connections.keys())
            for room_id in list(active_rooms):
                state = await store.get(room_id)
                if state is None:
                    logger.info(f"🧹 GC: Room {room_id} expired in Redis, closing connections.")
                    await _close_room_connections(room_id)
            return

        # --- In-memory fallback GC ---
        now = time.time()
        rooms_to_delete = []
        for room_id in await store.all_room_ids():
            state = await store.get(room_id)
            if state and now - state.get('last_activity', 0) > INACTIVE_TIMEOUT:
                rooms_to_delete.append(room_id)

        for room_id in rooms_to_delete:
            logger.info(f"🧹 GC: Removing inactive room {room_id}")
            await _close_room_connections(room_id)
            await store.delete(room_id)


async def _close_room_connections(room_id: str):
    """Forcefully closes all WebSocket connections in a room."""
    connections = manager.active_connections.get(room_id, [])
    for ws in list(connections):
        try:
            await ws.close(code=status.WS_1001_GOING_AWAY, reason="Room expired due to inactivity.")
        except Exception:
            pass
    manager.active_connections.pop(room_id, None)


@app.on_event("startup")
async def startup_event():
    await store.init()
    asyncio.create_task(cleanup_inactive_rooms())
    logger.info("📡 Planning Poker API started.")


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

if not allowed_origins:
    logger.warning("⚠️ ALLOWED_ORIGINS is empty. The API will be inaccessible from browsers (CORS block).")
elif "*" in allowed_origins:
    logger.critical("🚨 SECURITY RISK: ALLOWED_ORIGINS contains '*'. This is extremely insecure for production!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_room_id(room_id: str) -> bool:
    return bool(VALID_ROOM_RE.match(room_id))


def validate_username(name: str) -> bool:
    return bool(VALID_NAME_RE.match(name))


# ---------------------------------------------------------------------------
# Connection Manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        # WebSocket objects cannot be serialised — they always stay in-process
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.rate_limits: Dict[WebSocket, Dict[str, any]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_name: str) -> bool:
        if not validate_room_id(room_id) or not validate_username(user_name):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Invalid room_id or user_name.")
            return False

        state = await store.get(room_id)

        # Prevent duplicate usernames in the same room
        if state and user_name in state.get('users', {}):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Username already taken in this room.")
            return False

        # Room capacity limit
        if room_id in self.active_connections and \
           len(self.active_connections[room_id]) >= MAX_USERS_PER_ROOM:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Room is full.")
            return False

        await websocket.accept()

        if state is None:
            # Brand new room
            state = {
                'users': {},
                'revealed': False,
                'host': user_name,
                'last_activity': time.time(),
            }
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        state['users'][user_name] = {'vote': None, 'voted': False}
        state['last_activity'] = time.time()
        await store.set(room_id, state)

        self.active_connections[room_id].append(websocket)
        await self.broadcast_state(room_id)
        return True

    async def disconnect(self, websocket: WebSocket, room_id: str, user_name: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket) \
                if hasattr(self.active_connections[room_id], 'discard') \
                else self.active_connections[room_id].remove(websocket) \
                if websocket in self.active_connections[room_id] else None

        state = await store.get(room_id)
        if state:
            state['users'].pop(user_name, None)

            # Promote next user to host if host left
            if state.get('host') == user_name:
                remaining = list(state['users'].keys())
                state['host'] = remaining[0] if remaining else None

            if state['users']:
                await store.set(room_id, state)
            else:
                # Last person left — delete the room
                await store.delete(room_id)
                self.active_connections.pop(room_id, None)

        if websocket in self.rate_limits:
            del self.rate_limits[websocket]

    async def broadcast_state(self, room_id: str):
        if room_id not in self.active_connections:
            return
        state = await store.get(room_id)
        if not state:
            return

        state_to_send = {'users': {}, 'revealed': state['revealed'], 'host': state['host']}
        for user, data in state['users'].items():
            if state['revealed']:
                state_to_send['users'][user] = data
            else:
                state_to_send['users'][user] = {'voted': data['voted']}

        dead_connections = []
        for connection in self.active_connections.get(room_id, []):
            try:
                await connection.send_json({"type": "state_update", "data": state_to_send})
            except Exception:
                dead_connections.append(connection)

        for conn in dead_connections:
            conns = self.active_connections.get(room_id, [])
            if conn in conns:
                conns.remove(conn)

    async def process_vote(self, room_id: str, user_name: str, vote_value: str):
        if vote_value not in ALLOWED_VOTES:
            return
        state = await store.get(room_id)
        if state and user_name in state.get('users', {}):
            if state.get('revealed'):
                return
            state['users'][user_name]['vote'] = vote_value
            state['users'][user_name]['voted'] = True
            state['last_activity'] = time.time()
            await store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def reveal_votes(self, room_id: str):
        state = await store.get(room_id)
        if state:
            state['revealed'] = True
            state['last_activity'] = time.time()
            await store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def reset_votes(self, room_id: str):
        state = await store.get(room_id)
        if state:
            state['revealed'] = False
            state['last_activity'] = time.time()
            for user in state['users']:
                state['users'][user]['vote'] = None
                state['users'][user]['voted'] = False
            await store.set(room_id, state)
            await self.broadcast_state(room_id)

    def is_rate_limited(self, websocket: WebSocket) -> bool:
        now = time.time()
        if websocket not in self.rate_limits:
            self.rate_limits[websocket] = {'count': 1, 'start_time': now}
            return False

        data = self.rate_limits[websocket]
        if now - data['start_time'] < RATE_LIMIT_WINDOW:
            if data['count'] >= RATE_LIMIT_MSGS:
                return True
            data['count'] += 1
        else:
            data['count'] = 1
            data['start_time'] = now
        return False

    async def get_host(self, room_id: str) -> Optional[str]:
        state = await store.get(room_id)
        return state.get('host') if state else None


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/{room_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_name: str):
    accepted = await manager.connect(websocket, room_id, user_name)
    if not accepted:
        return

    try:
        while True:
            try:
                data = await websocket.receive_json()
                if manager.is_rate_limited(websocket):
                    continue
            except Exception:
                break

            action = data.get('action', '')

            if action == 'vote':
                value = str(data.get('value', ''))[:MAX_VOTE_LEN]
                await manager.process_vote(room_id, user_name, value)

            elif action == 'reveal':
                if await manager.get_host(room_id) == user_name:
                    await manager.reveal_votes(room_id)

            elif action == 'reset':
                if await manager.get_host(room_id) == user_name:
                    await manager.reset_votes(room_id)

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, room_id, user_name)
        await manager.broadcast_state(room_id)


@app.get("/")
def read_root():
    return {"message": "Planning Poker API"}
