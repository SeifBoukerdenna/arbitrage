import itertools
from typing import List
from models.bet import Bet
from models.combination import Combination


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
