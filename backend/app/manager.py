import json
import logging
import asyncio
import time
from fastapi import WebSocket
from typing import Dict, List, Set, Optional

from .models import RoomState, UserState, RoundRecord
from .store import room_store
from .constants import (
    MAX_USERS_PER_ROOM, VALID_NAME_RE, VALID_ROOM_RE, 
    DECK_TYPES, ALLOWED_VOTES
)
from .utils import get_average

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # active_connections[room_id] = set of WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.timers: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, room_id: str, username: str, deck: str = 'fibonacci'):
        # Basic validation
        if not VALID_ROOM_RE.match(room_id):
            await websocket.close(code=4001, reason="Invalid Room ID")
            return False
        if not VALID_NAME_RE.match(username):
            await websocket.close(code=4002, reason="Invalid Username")
            return False

        await websocket.accept()
        
        state = room_store.get(room_id)
        if not state:
            state = RoomState(last_activity=time.time(), host=username, deck_type=deck)
        
        # Check if user already exists (reconnection or duplicate name)
        if username in state.users:
            # We allow it, but in a real app we might want more check
            pass
        elif len(state.users) >= MAX_USERS_PER_ROOM:
            await websocket.send_text(json.dumps({"type": "error", "message": "Room is full"}))
            await websocket.close()
            return False

        if username not in state.users:
            state.users[username] = UserState()
        
        # If room has no host, this user becomes the host
        if not state.host or state.host not in state.users:
            state.host = username

        state.last_activity = time.time()
        room_store.set(room_id, state)

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        
        return True

    def disconnect(self, websocket: WebSocket, room_id: str, username: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        state = room_store.get(room_id)
        if state:
            if username in state.users:
                del state.users[username]
            
            if not state.users:
                room_store.delete(room_id)
                if room_id in self.timers:
                    self.timers[room_id].cancel()
                    del self.timers[room_id]
            else:
                # If host left, assign new host
                if state.host == username:
                    state.host = next(iter(state.users.keys()))
                state.last_activity = time.time()
                room_store.set(room_id, state)

    async def broadcast_state(self, room_id: str):
        state = room_store.get(room_id)
        if not state or room_id not in self.active_connections:
            return

        # Prepare state for broadcast (hide votes if not revealed)
        data = state.model_dump()
        if not state.revealed:
            for user in data['users'].values():
                if user['vote'] is not None:
                    user['vote'] = '✓' # obfuscate
        
        message = json.dumps({"type": "state_update", "data": data})
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_text(message)
            except Exception:
                pass

    async def process_vote(self, room_id: str, username: str, vote: Optional[str]):
        state = room_store.get(room_id)
        if not state or state.revealed:
            return

        if vote is not None and vote not in ALLOWED_VOTES:
            return

        if username in state.users:
            state.users[username].vote = vote
            state.users[username].voted = (vote is not None)
            state.last_activity = time.time()
            room_store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def reveal_votes(self, room_id: str):
        state = room_store.get(room_id)
        if not state or state.revealed:
            return
        
        state.revealed = True
        state.last_activity = time.time()
        
        # Cancel timer if active
        if room_id in self.timers:
            self.timers[room_id].cancel()
            del self.timers[room_id]
            state.timer_end = None

        room_store.set(room_id, state)
        await self.broadcast_state(room_id)

    async def reset_votes(self, room_id: str):
        state = room_store.get(room_id)
        if not state:
            return

        # Record history before resetting if it was revealed
        if state.revealed:
            votes = {u: s.vote for u, s in state.users.items() if s.vote}
            if votes:
                avg = get_average(votes)
                record = RoundRecord(round=state.round_number, votes=votes, average=avg)
                state.history.insert(0, record)
                if len(state.history) > 50: # Limit history
                    state.history = state.history[:50]

        state.revealed = False
        state.round_number += 1
        for user in state.users.values():
            user.vote = None
            user.voted = False
        
        state.timer_end = None
        state.last_activity = time.time()
        room_store.set(room_id, state)
        await self.broadcast_state(room_id)

    async def set_deck(self, room_id: str, deck_type: str):
        if deck_type not in DECK_TYPES:
            return
        state = room_store.get(room_id)
        if state:
            state.deck_type = deck_type
            state.last_activity = time.time()
            room_store.set(room_id, state)
            await self.broadcast_state(room_id)

    async def start_timer(self, room_id: str, duration: int):
        # Clamp duration 5s - 10min
        duration = max(5, min(duration, 600))
        
        state = room_store.get(room_id)
        if not state: return

        state.timer_duration = duration
        state.timer_end = time.time() + duration
        state.last_activity = time.time()
        room_store.set(room_id, state)

        # Cancel existing timer task
        if room_id in self.timers:
            self.timers[room_id].cancel()

        # Schedule auto-reveal
        async def _timer_task():
            await asyncio.sleep(duration)
            await self.reveal_votes(room_id)
            if room_id in self.timers:
                del self.timers[room_id]

        self.timers[room_id] = asyncio.create_task(_timer_task())
        await self.broadcast_state(room_id)

    async def cancel_timer(self, room_id: str):
        state = room_store.get(room_id)
        if not state: return
        
        state.timer_end = None
        room_store.set(room_id, state)
        
        if room_id in self.timers:
            self.timers[room_id].cancel()
            del self.timers[room_id]
        
        await self.broadcast_state(room_id)

# Global instance
manager = ConnectionManager()
