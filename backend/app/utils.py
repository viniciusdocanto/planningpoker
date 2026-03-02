from typing import Optional

def is_numeric(v: str) -> bool:
    """Checks if a string represents a numeric value, handling '½'."""
    try:
        float(v.replace('½', '0.5'))
        return True
    except ValueError:
        return False

def get_average(votes: dict) -> Optional[float]:
    """Calculates the average of numeric votes."""
    numeric_votes = []
    for v in votes.values():
        clean_v = v.replace('½', '0.5')
        try:
            numeric_votes.append(float(clean_v))
        except ValueError:
            continue
    
    if not numeric_votes:
        return None
    return sum(numeric_votes) / len(numeric_votes)
