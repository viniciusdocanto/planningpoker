import re
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

app = FastAPI()

# --- CORS: allow only the frontend origin in production ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Constants / Limits ---
MAX_ROOM_ID_LEN   = 40
MAX_USERNAME_LEN  = 30
MAX_VOTE_LEN      = 4      # longest valid card is "☕" (4 bytes)
MAX_USERS_PER_ROOM = 20
VALID_NAME_RE     = re.compile(r'^[\w\s\-\.]{1,30}$', re.UNICODE)
VALID_ROOM_RE     = re.compile(r'^[A-Za-z0-9\-_]{1,40}$')
ALLOWED_VOTES     = {'0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕'}


def validate_room_id(room_id: str) -> bool:
    return bool(VALID_ROOM_RE.match(room_id))


def validate_username(name: str) -> bool:
    return bool(VALID_NAME_RE.match(name))


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.room_states: Dict[str, Dict[str, any]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_name: str) -> bool:
        """
        Returns True if connection was accepted, False if rejected.
        """
        # --- Input validation ---
        if not validate_room_id(room_id) or not validate_username(user_name):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Invalid room_id or user_name.")
            return False

        # --- Prevent duplicate usernames in the same room ---
        if room_id in self.room_states and user_name in self.room_states[room_id]['users']:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Username already taken in this room.")
            return False

        # --- Room capacity limit ---
        if room_id in self.active_connections and \
           len(self.active_connections[room_id]) >= MAX_USERS_PER_ROOM:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
                                  reason="Room is full.")
            return False

        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_states[room_id] = {'users': {}, 'revealed': False, 'host': user_name}

        self.active_connections[room_id].append(websocket)
        self.room_states[room_id]['users'][user_name] = {'vote': None, 'voted': False}
        await self.broadcast_state(room_id)
        return True

    def disconnect(self, websocket: WebSocket, room_id: str, user_name: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            if user_name in self.room_states.get(room_id, {}).get('users', {}):
                del self.room_states[room_id]['users'][user_name]

            # Promote next user to host if host left
            if self.room_states.get(room_id, {}).get('host') == user_name:
                remaining = list(self.room_states[room_id]['users'].keys())
                self.room_states[room_id]['host'] = remaining[0] if remaining else None

            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.room_states:
                    del self.room_states[room_id]

    async def broadcast_state(self, room_id: str):
        if room_id not in self.active_connections:
            return
        state = self.room_states[room_id]
        state_to_send = {'users': {}, 'revealed': state['revealed'], 'host': state['host']}
        for user, data in state['users'].items():
            if state['revealed']:
                state_to_send['users'][user] = data
            else:
                state_to_send['users'][user] = {'voted': data['voted']}

        dead_connections = []
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_json({"type": "state_update", "data": state_to_send})
            except Exception:
                dead_connections.append(connection)

        # Remove any connections that failed silently
        for conn in dead_connections:
            if conn in self.active_connections.get(room_id, []):
                self.active_connections[room_id].remove(conn)

    async def process_vote(self, room_id: str, user_name: str, vote_value: str):
        # --- Validate vote value against allowed set ---
        if vote_value not in ALLOWED_VOTES:
            return
        if room_id in self.room_states and user_name in self.room_states[room_id]['users']:
            # Don't allow changing vote after reveal
            if self.room_states[room_id].get('revealed'):
                return
            self.room_states[room_id]['users'][user_name]['vote'] = vote_value
            self.room_states[room_id]['users'][user_name]['voted'] = True
            await self.broadcast_state(room_id)

    async def reveal_votes(self, room_id: str):
        if room_id in self.room_states:
            self.room_states[room_id]['revealed'] = True
            await self.broadcast_state(room_id)

    async def reset_votes(self, room_id: str):
        if room_id in self.room_states:
            self.room_states[room_id]['revealed'] = False
            for user in self.room_states[room_id]['users']:
                self.room_states[room_id]['users'][user]['vote'] = None
                self.room_states[room_id]['users'][user]['voted'] = False
            await self.broadcast_state(room_id)


manager = ConnectionManager()


@app.websocket("/ws/{room_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_name: str):
    accepted = await manager.connect(websocket, room_id, user_name)
    if not accepted:
        return

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except Exception:
                # Invalid JSON or connection error — close gracefully
                break

            action = data.get('action', '')

            if action == 'vote':
                value = str(data.get('value', ''))[:MAX_VOTE_LEN]
                await manager.process_vote(room_id, user_name, value)

            elif action == 'reveal':
                if manager.room_states.get(room_id, {}).get('host') == user_name:
                    await manager.reveal_votes(room_id)

            elif action == 'reset':
                if manager.room_states.get(room_id, {}).get('host') == user_name:
                    await manager.reset_votes(room_id)
            # Unknown actions are silently ignored

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, room_id, user_name)
        await manager.broadcast_state(room_id)


@app.get("/")
def read_root():
    return {"message": "Planning Poker API"}
