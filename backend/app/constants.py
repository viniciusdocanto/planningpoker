import re
from typing import Dict, List

# --- App Version ---
APP_VERSION = "0.19.0"  # Incrementing version for componentization milestone

# --- Cleanup & TTL ---
CLEANUP_INTERVAL = 30 * 60      # Check every 30 minutes
INACTIVE_TIMEOUT = 2 * 60 * 60  # 2 hours of inactivity
REDIS_TTL = INACTIVE_TIMEOUT    # Redis key TTL mirrors the GC timeout

# --- Room & User Limits ---
MAX_ROOM_ID_LEN = 40
MAX_USERNAME_LEN = 30
MAX_VOTE_LEN = 8                # longest valid card is "XXL" + slack
MAX_USERS_PER_ROOM = 20

# --- Validation Regex ---
VALID_NAME_RE = re.compile(r'^[a-zA-ZÀ-ÿ0-9\s\-\.]{1,30}$', re.UNICODE)
VALID_ROOM_RE = re.compile(r'^[A-Za-z0-9\-_]{1,40}$')

# --- Game Logic ---
DECK_TYPES: Dict[str, List[str]] = {
    'fibonacci': ['0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕'],
    'powers2':   ['0', '1', '2', '4', '8', '16', '32', '64', '?', '☕'],
    'tshirt':    ['XS', 'S', 'M', 'L', 'XL', 'XXL', '?', '☕'],
}
ALLOWED_VOTES = set(v for deck in DECK_TYPES.values() for v in deck)

# --- Rate Limiting ---
RATE_LIMIT_MSGS = 10            # max messages per window
RATE_LIMIT_WINDOW = 1.0         # window size in seconds
