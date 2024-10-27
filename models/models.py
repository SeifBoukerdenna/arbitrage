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
            self.combined_prob *= bet.confidence  # Already between 0 and 1
        self.ev_per_dollar = self.combined_prob * self.combined_odds - 1.0


@dataclass
class BettingStrategy:
    """Encapsulates the betting strategy details."""
    total_budget: float
    strategy_type: str  # "Accumulator", "Parlay", "System"
    folds: int  # Number of legs per combination (None for System)
    risk_preference: str  # "Conservative", "Moderate", "Aggressive"
    combinations: List[Combination] = field(default_factory=list)
    stake_allocation: List[float] = field(default_factory=list)

    def filter_and_sort_combinations(self):
        """Filter and sort combinations based on risk preference."""
        # Define risk thresholds
        risk_thresholds = {
            "Conservative": {"min_ev": 0.05, "max_combined_odds": 5},
            "Moderate": {"min_ev": 0.0, "max_combined_odds": 15},
            "Aggressive": {"min_ev": -0.05, "max_combined_odds": None},
        }

        thresholds = risk_thresholds.get(self.risk_preference, risk_thresholds["Moderate"])

        # Filter combinations based on expected value and combined odds
        filtered_combinations = [
            combo for combo in self.combinations
            if combo.ev_per_dollar >= thresholds["min_ev"] and
            (thresholds["max_combined_odds"] is None or combo.combined_odds <= thresholds["max_combined_odds"])
        ]

        # Sort combinations
        filtered_combinations.sort(key=lambda combo: combo.ev_per_dollar, reverse=True)

        # Limit the number of combinations
        K = 500
        self.combinations = filtered_combinations[:K]
