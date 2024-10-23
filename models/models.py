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
    combined_prob: float = field(init=False)
    ev_per_dollar: float = field(init=False)
    adjusted_odds: float = field(init=False)
    kelly_fraction: float = field(init=False)

    def __post_init__(self):
        self.combined_odds = 1.0
        self.combined_prob = 1.0
        for bet in self.bets:
            self.combined_odds *= bet.odds
            self.combined_prob *= bet.confidence / 100.0
        self.ev_per_dollar = self.combined_prob * self.combined_odds - 1.0


@dataclass
class BettingStrategy:
    """Encapsulates the betting strategy details."""
    total_budget: float
    strategy_type: str  # "Accumulator", "Parlay", "System"
    folds: int  # Number of legs per combination (None for System)
    combinations: List[Combination] = field(default_factory=list)
    stake_allocation: List[float] = field(default_factory=list)
