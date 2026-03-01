# Planning Poker Backend - MIT License - (c) 2026 Vinicius do Canto
import re
import os
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

import asyncio
import logging

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _is_numeric(v: str) -> bool:
    try:
        float(v.replace('½', '0.5'))
        return True
    except ValueError:
        return False


# --- Constants / Limits ---
CLEANUP_INTERVAL  = 30 * 60   # Check every 30 minutes
INACTIVE_TIMEOUT  = 2 * 60 * 60  # 2 hours of inactivity
REDIS_TTL         = INACTIVE_TIMEOUT  # Redis key TTL mirrors the GC timeout
MAX_ROOM_ID_LEN   = 40
MAX_USERNAME_LEN  = 30
MAX_VOTE_LEN      = 8      # longest valid card is "XXL" + slack
MAX_USERS_PER_ROOM = 20
VALID_NAME_RE     = re.compile(r'^[a-zA-ZÀ-ÿ0-9\s\-\.]{1,30}$', re.UNICODE)
VALID_ROOM_RE     = re.compile(r'^[A-Za-z0-9\-_]{1,40}$')
DECK_TYPES: Dict[str, List[str]] = {
    'fibonacci': ['0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕'],
    'powers2':   ['0', '1', '2', '4', '8', '16', '32', '64', '?', '☕'],
    'tshirt':    ['XS', 'S', 'M', 'L', 'XL', 'XXL', '?', '☕'],
}
ALLOWED_VOTES = set(v for deck in DECK_TYPES.values() for v in deck)  # union of all cards
RATE_LIMIT_MSGS   = 10      # max messages per window
RATE_LIMIT_WINDOW = 1.0     # window size in seconds

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

APP_VERSION = "0.17.0"


class UserState(BaseModel):
    vote: Optional[str] = None
    voted: bool = False


class RoundRecord(BaseModel):
    round: int
    votes: Dict[str, str]       # username -> vote string
    average: Optional[float] = None


class RoomState(BaseModel):
    users: Dict[str, UserState] = {}
    revealed: bool = False
    host: Optional[str] = None
    last_activity: float = 0.0
    deck_type: str = 'fibonacci'
    round_number: int = 0
    history: List[RoundRecord] = []
    timer_end: Optional[float] = None
    timer_duration: int = 60

    def model_dump_json_safe(self) -> dict:
        """Returns a plain dict safe for JSON serialisation."""
        return self.model_dump()


class WsMessage(BaseModel):
    action: str
    value: Optional[str] = None

    @field_validator('action')
    @classmethod
    def action_must_be_known(cls, v: str) -> str:
        if v not in ('vote', 'reveal', 'reset', 'set_deck', 'start_timer', 'cancel_timer'):
            raise ValueError(f'Unknown action: {v}')
        return v



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

    async def get(self, room_id: str) -> Optional[RoomState]:
        if self._use_redis and self._redis:
            raw = await self._redis.get(f"room:{room_id}")
            return RoomState.model_validate_json(raw) if raw else None
        raw_dict = self._memory.get(room_id)
        return RoomState.model_validate(raw_dict) if raw_dict else None

    async def set(self, room_id: str, state: RoomState) -> None:
        if self._use_redis and self._redis:
            await self._redis.set(
                f"room:{room_id}",
                state.model_dump_json(),
                ex=REDIS_TTL
            )
        else:
            self._memory[room_id] = state.model_dump()

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
        self.rate_limits: Dict[int, Dict[str, object]] = {}  # keyed by id(ws)
        self.timer_tasks: Dict[str, asyncio.Task] = {}  # room_id -> active reveal task

    async def connect(self, websocket: WebSocket, room_id: str, user_name: str, deck_type: str = 'fibonacci') -> bool:
        if not validate_room_id(room_id) or not validate_username(user_name):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Invalid room_id or user_name.")
            return False

        state = await store.get(room_id)

        # Prevent duplicate usernames in the same room
        if state and user_name in state.users:
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
            # Brand new room — use the deck_type requested by the creator
            state = RoomState(
                users={},
                revealed=False,
                host=user_name,
                last_activity=time.time(),
                deck_type=deck_type,
            )

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        state.users[user_name] = UserState(vote=None, voted=False)
        state.last_activity = time.time()
        await store.set(room_id, state)

        self.active_connections[room_id].append(websocket)
        await self.broadcast_event(room_id, 'user_joined', user_name, exclude=websocket)
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
            state.users.pop(user_name, None)

            # Promote next user to host if host left
            if state.host == user_name:
                remaining = list(state.users.keys())
                state.host = remaining[0] if remaining else None

            if state.users:
                await store.set(room_id, state)
            else:
                # Last person left — delete the room
                await store.delete(room_id)
                self.active_connections.pop(room_id, None)

        if websocket in self.rate_limits:
            del self.rate_limits[websocket]

    async def broadcast_event(self, room_id: str, event: str, user: str, exclude: Optional[WebSocket] = None, deck_type: Optional[str] = None) -> None:
        """Send event_notify to all connections in room (optionally excluding one WS)."""
        payload: Dict[str, object] = {"type": "event_notify", "event": event, "user": user}
        if deck_type is not None:
            payload['deck_type'] = deck_type
        for conn in self.active_connections.get(room_id, []):
            if conn is exclude:
                continue
            try:
                await conn.send_json(payload)
            except Exception:
                pass

    async def broadcast_state(self, room_id: str) -> None:
        if room_id not in self.active_connections:
            return
        state = await store.get(room_id)
        if not state:
            return

        state_to_send: Dict[str, object] = {
            'users': {},
            'revealed': state.revealed,
            'host': state.host,
            'deck_type': state.deck_type,
            'round_number': state.round_number,
            'history': [r.model_dump() for r in state.history],
            'timer_end': state.timer_end,
            'timer_duration': state.timer_duration,
        }
        for user, data in state.users.items():
            if state.revealed:
                state_to_send['users'][user] = data.model_dump()  # type: ignore[index]
            else:
                state_to_send['users'][user] = {'voted': data.voted}  # type: ignore[index]

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

    async def process_vote(self, room_id: str, user_name: str, vote_value: str) -> None:
        if vote_value not in ALLOWED_VOTES:
            return
        state = await store.get(room_id)
        if state and user_name in state.users:
            if state.revealed:
                return
            state.users[user_name].vote = vote_value
            state.users[user_name].voted = True
            state.last_activity = time.time()
            await store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def reveal_votes(self, room_id: str) -> None:
        # Cancel any pending auto-reveal timer
        if room_id in self.timer_tasks:
            self.timer_tasks[room_id].cancel()
            del self.timer_tasks[room_id]

        state = await store.get(room_id)
        if state:
            state.revealed = True
            state.timer_end = None   # clear timer on reveal
            state.last_activity = time.time()
            await store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def reset_votes(self, room_id: str) -> None:
        # Cancel any pending auto-reveal timer
        if room_id in self.timer_tasks:
            self.timer_tasks[room_id].cancel()
            del self.timer_tasks[room_id]

        state = await store.get(room_id)
        if state:
            # Record finished round in history (only if votes were revealed)
            if state.revealed:
                votes = {u: d.vote for u, d in state.users.items() if d.voted and d.vote}
                nums = [float(v) for v in votes.values() if v not in ('?', '☕') and _is_numeric(v)]
                avg = round(sum(nums) / len(nums), 1) if nums else None
                state.round_number += 1
                record = RoundRecord(round=state.round_number, votes=votes, average=avg)
                state.history = (state.history + [record])[-20:]   # keep last 20
            state.revealed = False
            state.timer_end = None   # clear timer on reset
            state.last_activity = time.time()
            for user in state.users.values():
                user.vote = None
                user.voted = False
            await store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def set_deck_type(self, room_id: str, deck: str) -> None:
        if deck not in DECK_TYPES:
            return
        # Cancel timer
        if room_id in self.timer_tasks:
            self.timer_tasks[room_id].cancel()
            del self.timer_tasks[room_id]

        state = await store.get(room_id)
        if state:
            state.deck_type = deck
            state.revealed = False
            state.timer_end = None
            state.last_activity = time.time()
            for user in state.users.values():
                user.vote = None
                user.voted = False
            await store.set(room_id, state)
            host_name = state.host or ''
            await self.broadcast_event(room_id, 'deck_changed', host_name, deck_type=deck)
            await self.broadcast_state(room_id)

    async def start_timer(self, room_id: str, duration: int) -> None:
        """Start a countdown timer. duration is clamped to 10-300 seconds."""
        duration = max(10, min(300, duration))
        
        # Cancel existing task if any
        if room_id in self.timer_tasks:
            self.timer_tasks[room_id].cancel()
            
        state = await store.get(room_id)
        if state and not state.revealed:
            state.timer_end = time.time() + duration
            state.timer_duration = duration
            state.last_activity = time.time()
            await store.set(room_id, state)
            
            # Schedule auto-reveal
            self.timer_tasks[room_id] = asyncio.create_task(self._auto_reveal_after(room_id, duration))
            
            await self.broadcast_state(room_id)

    async def _auto_reveal_after(self, room_id: str, delay: int) -> None:
        """Helper task to reveal votes after a delay."""
        try:
            await asyncio.sleep(delay)
            # Check if still voting and timer is the same (handled by task management)
            await self.reveal_votes(room_id)
            logger.info(f"⏰ Auto-revealed room {room_id} after {delay}s")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ Error in auto-reveal task for {room_id}: {e}")
        finally:
            self.timer_tasks.pop(room_id, None)

    async def cancel_timer(self, room_id: str) -> None:
        if room_id in self.timer_tasks:
            self.timer_tasks[room_id].cancel()
            del self.timer_tasks[room_id]
            
        state = await store.get(room_id)
        if state:
            state.timer_end = None
            state.last_activity = time.time()
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
        return state.host if state else None


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/{room_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_name: str, deck: str = 'fibonacci'):
    accepted = await manager.connect(websocket, room_id, user_name, deck_type=deck if deck in DECK_TYPES else 'fibonacci')
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

            elif action == 'set_deck':
                if await manager.get_host(room_id) == user_name:
                    deck = str(data.get('value', ''))[:16]
                    await manager.set_deck_type(room_id, deck)

            elif action == 'start_timer':
                if await manager.get_host(room_id) == user_name:
                    try:
                        duration = int(str(data.get('value', '60')))
                    except (ValueError, TypeError):
                        duration = 60
                    await manager.start_timer(room_id, duration)

            elif action == 'cancel_timer':
                if await manager.get_host(room_id) == user_name:
                    await manager.cancel_timer(room_id)

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, room_id, user_name)
        await manager.broadcast_state(room_id)


@app.get("/")
def read_root():
    return {"message": "Planning Poker API"}
