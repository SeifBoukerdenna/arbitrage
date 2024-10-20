# utils.py

import itertools
import math
from typing import List
from models import Bet, Combination, BettingStrategy

def kelly_criterion(odds: float, probability: float) -> float:
    """
    Calculate the Kelly fraction.

    :param odds: Decimal odds of the bet.
    :param probability: Probability of the bet winning (0-1).
    :return: Kelly fraction (0-1).
    """
    b = odds - 1
    p = probability
    q = 1 - p
    if b == 0:
        return 0
    kelly = (b * p - q) / b
    return max(kelly, 0)

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
        # All possible combinations of the specified number of folds
        for combo in itertools.combinations(bets, folds):
            combinations.append(Combination(list(combo)))
    elif strategy_type == "System":
        # For system bets, generate combinations from all subsets of bets >= folds
        for r in range(folds, len(bets)+1):
            for combo in itertools.combinations(bets, r):
                combinations.append(Combination(list(combo)))
    return combinations

def allocate_stakes(strategy: BettingStrategy):
    """
    Allocate stakes to each combination based on the Kelly Criterion.

    :param strategy: BettingStrategy object.
    """
    stakes = []
    for combo in strategy.combinations:
        # Calculate combined probability assuming independence
        combined_prob = math.prod([bet.confidence / 100 for bet in combo.bets])
        # Kelly Criterion based on combined probability
        kelly_frac = kelly_criterion(combo.combined_odds, combined_prob)
        stake = kelly_frac * strategy.total_budget
        stakes.append(stake)
    strategy.stake_allocation = stakes
