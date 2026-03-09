import logging
import asyncio
import time
import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware

from .constants import (
    APP_VERSION, CLEANUP_INTERVAL, INACTIVE_TIMEOUT, 
    ALLOWED_VOTES, RATE_LIMIT_MSGS, RATE_LIMIT_WINDOW
)
from .models import WsMessage
from .store import room_store
from .manager import manager

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Planning Poker API", version=APP_VERSION)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Start background tasks
    await room_store.init_redis()
    asyncio.create_task(cleanup_inactive_rooms())
    asyncio.create_task(manager.ping_loop())

async def cleanup_inactive_rooms():
    """Background task to remove rooms that have been inactive for too long."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        now = time.time()
        rooms = await room_store.list_rooms()
        
        for room_id in rooms:
            state = await room_store.get(room_id)
            if state and (now - state.last_activity > INACTIVE_TIMEOUT):
                logger.info(f"Cleaning up inactive room: {room_id}")
                # If room is active in connection manager, disconnect everyone
                if room_id in manager.active_connections:
                    # Closing sockets will trigger disconnect logic
                    for ws in list(manager.active_connections[room_id]):
                        try:
                            await ws.close()
                        except:
                            pass
                await room_store.delete(room_id)

@app.get("/")
async def root():
    return {"status": "ok", "version": APP_VERSION}

@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str, deck: str = 'fibonacci'):
    # Rate limiting
    msg_window = []
    
    connected = await manager.connect(websocket, room_id, username, deck)
    if not connected:
        return

    try:
        # Initial state broadcast
        await manager.broadcast_state(room_id)

        while True:
            data = await websocket.receive_text()
            
            # Simple Rate Limiting
            now = time.time()
            msg_window = [t for t in msg_window if now - t < RATE_LIMIT_WINDOW]
            if len(msg_window) >= RATE_LIMIT_MSGS:
                await websocket.send_text(json.dumps({"type": "error", "message": "Rate limit exceeded"}))
                continue
            msg_window.append(now)

            try:
                msg_data = json.loads(data)
                msg = WsMessage.model_validate(msg_data)
                
                if msg.action == 'vote':
                    await manager.process_vote(room_id, username, msg.value)
                elif msg.action == 'reveal':
                    await manager.reveal_votes(room_id)
                elif msg.action == 'reset':
                    await manager.reset_votes(room_id)
                elif msg.action == 'set_deck' and msg.value:
                    await manager.set_deck(room_id, msg.value)
                elif msg.action == 'start_timer':
                    duration = int(msg.value) if msg.value else 60
                    await manager.start_timer(room_id, duration)
                elif msg.action == 'cancel_timer':
                    await manager.cancel_timer(room_id)
                elif msg.action == 'pong':
                    await manager.handle_pong(websocket)
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid message format"}))

    except WebSocketDisconnect:
        await manager.disconnect(websocket, room_id, username)
        await manager.broadcast_state(room_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, room_id, username)
        await manager.broadcast_state(room_id)
