import pytest
import asyncio
from app.utils import get_average
from app.store import RedisRoomStore
from app.models import RoomState

def test_get_average():
    # Regular voting
    votes = {'UserA': '5', 'UserB': '8', 'UserC': '5'}
    assert get_average(votes) == 6.0
    
    # Ignoring special characters
    votes = {'UserA': '5', 'UserB': '?', 'UserC': '☕'}
    assert get_average(votes) == 5.0

    # Float parsing
    votes = {'UserA': '0.5', 'UserB': '1', 'UserC': '1.5'}
    assert get_average(votes) == 1.0

    # No valid votes
    votes = {'UserA': '?', 'UserB': '☕'}
    assert get_average(votes) is None

@pytest.mark.asyncio
async def test_store_in_memory():
    store = RedisRoomStore()
    
    # Store should be empty and fallback to memory since we didn't init redis
    assert store.redis is None
    
    state = RoomState(host="Alice", deck_type="fibonacci")
    
    # Test SET
    await store.set("room123", state)
    
    # Test GET
    retrieved = await store.get("room123")
    assert retrieved is not None
    assert retrieved.host == "Alice"
    
    # Test LIST
    rooms = await store.list_rooms()
    assert "room123" in rooms
    
    # Test DELETE
    await store.delete("room123")
    assert await store.get("room123") is None
