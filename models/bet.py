from dataclasses import dataclass


@dataclass
class Bet:
    """Represents a single bet."""
    name: str
    odds: float
    confidence: float  # Probability (0-100)
