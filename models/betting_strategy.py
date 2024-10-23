from dataclasses import dataclass, field
from typing import List
from .combination import Combination


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

    def get_unique_bets(self):
        unique_bets = {}
        for combo in self.combinations:
            for bet in combo.bets:
                unique_bets[bet.name] = bet
        return unique_bets.values()
