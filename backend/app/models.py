from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

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
