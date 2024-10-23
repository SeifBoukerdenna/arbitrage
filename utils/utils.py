import itertools
from typing import List
from models.models import Bet, Combination, BettingStrategy


def kelly_criterion(odds: float, probability: float, fraction: float = 1.0) -> float:
    """Calculate the Kelly fraction with optional scaling."""
    b = odds - 1
    p = probability
    q = 1 - p
    if b <= 0 or p <= 0 or p >= 1:
        return 0.0
    kelly = (b * p - q) / b
    return max(fraction * kelly, 0.0)


def generate_combinations(bets: List[Bet], strategy_type: str, max_combination_size: int = None) -> List[Combination]:
    """Generate bet combinations based on the strategy type."""
    combinations = []
    if strategy_type == "System":
        max_size = max_combination_size or len(bets)
        for r in range(1, max_size + 1):
            combinations.extend([Combination(list(combo)) for combo in itertools.combinations(bets, r)])
    else:
        combinations = [Combination(bets)]
    return combinations


def allocate_stakes(strategy: BettingStrategy, fraction: float = 0.5, margin: float = 0.05):
    """Allocate stakes to each combination based on the Kelly Criterion."""
    total_budget = strategy.total_budget
    total_kelly_fraction = 0.0

    for combo in strategy.combinations:
        adjusted_odds = combo.combined_odds * (1 - margin)
        combo.adjusted_odds = adjusted_odds
        combo.kelly_fraction = kelly_criterion(adjusted_odds, combo.combined_prob, fraction)
        total_kelly_fraction += combo.kelly_fraction

    if total_kelly_fraction == 0:
        stakes = [0.0 for _ in strategy.combinations]
    else:
        stakes = [(combo.kelly_fraction / total_kelly_fraction) * total_budget for combo in strategy.combinations]

    strategy.stake_allocation = stakes
