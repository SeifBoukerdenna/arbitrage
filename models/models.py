# models/models.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class Bet:
    """Represents a single bet."""
    name: str
    odds: float
    confidence: float  # Probability (0-100)

@dataclass
class Combination:
    """Represents a combination of bets."""
    bets: List[Bet]
    combined_odds: float = field(init=False)

    def __post_init__(self):
        self.combined_odds = 1.0
        for bet in self.bets:
            self.combined_odds *= bet.odds

@dataclass
class BettingStrategy:
    """Encapsulates the betting strategy details."""
    total_budget: float
    strategy_type: str  # "Accumulator", "Parlay", "System"
    folds: int  # Number of legs per combination
    combinations: List[Combination] = field(default_factory=list)
    stake_allocation: List[float] = field(default_factory=list)
