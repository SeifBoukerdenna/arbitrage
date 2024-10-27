from dataclasses import dataclass, field
from typing import List
from .bet import Bet


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
            self.combined_prob *= bet.confidence  # Confidence is now between 0 and 1
        self.ev_per_dollar = self.combined_prob * self.combined_odds - 1.0
