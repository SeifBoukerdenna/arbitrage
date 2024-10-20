# models.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class Bet:
    name: str
    odds: float
    confidence: float  # Probability that the bet will pass (0-100)

@dataclass
class Combination:
    bets: List[Bet]
    combined_odds: float = field(init=False)

    def __post_init__(self):
        self.combined_odds = 1.0
        for bet in self.bets:
            self.combined_odds *= bet.odds

@dataclass
class BettingStrategy:
    total_budget: float
    strategy_type: str  # "Accumulator", "Parlay", "System"
    folds: int  # Number of legs per combination
    combinations: List[Combination] = field(default_factory=list)
    stake_allocation: List[float] = field(default_factory=list)
