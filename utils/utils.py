# utils/utils.py

import itertools
import math
from typing import List
from models.models import Bet, Combination, BettingStrategy

def kelly_criterion(odds: float, probability: float, fraction: float = 1.0) -> float:
    """
    Calculate the Kelly fraction with optional scaling.

    :param odds: Decimal odds of the bet.
    :param probability: Probability of the bet winning (0-1).
    :param fraction: Fraction of the full Kelly Criterion (default is 1.0 for full Kelly).
    :return: Kelly fraction (0-1).
    """
    b = odds - 1
    p = probability
    q = 1 - p
    if b <= 0 or p <= 0 or p >= 1:
        return 0.0
    kelly = (b * p - q) / b
    return max(fraction * kelly, 0.0)

def generate_combinations(bets: List[Bet], folds: int, strategy_type: str) -> List[Combination]:
    """
    Generate bet combinations based on the strategy type.

    :param bets: List of available bets.
    :param folds: Number of legs per combination.
    :param strategy_type: Type of betting strategy.
    :return: List of Combination objects.
    """
    combinations = []
    if strategy_type in ["Accumulator", "Parlay"]:
        combinations = [Combination(list(combo)) for combo in itertools.combinations(bets, folds)]
    elif strategy_type == "System":
        for r in range(folds, len(bets) + 1):
            combinations.extend([Combination(list(combo)) for combo in itertools.combinations(bets, r)])
    return combinations

def allocate_stakes(strategy: BettingStrategy, fraction: float = 0.5, margin: float = 0.05):
    """
    Allocate stakes to each combination based on the Kelly Criterion.

    :param strategy: BettingStrategy object.
    :param fraction: Fractional Kelly (default is 0.5 for half Kelly).
    :param margin: Margin to adjust the odds (default is 5% reduction).
    """
    stakes = []
    total_budget = strategy.total_budget

    for combo in strategy.combinations:
        # Calculate combined probability assuming independence
        combined_prob = math.prod([bet.confidence / 100 for bet in combo.bets])

        # Adjust odds for margin
        adjusted_odds = combo.combined_odds * (1 - margin)

        # Kelly Criterion based on combined probability
        kelly_frac = kelly_criterion(adjusted_odds, combined_prob, fraction)
        stake = kelly_frac * total_budget
        stakes.append(stake)

    # Normalize stakes if they exceed the total budget
    total_stake = sum(stakes)
    if total_stake > total_budget:
        normalization_factor = total_budget / total_stake
        stakes = [stake * normalization_factor for stake in stakes]

    strategy.stake_allocation = stakes
