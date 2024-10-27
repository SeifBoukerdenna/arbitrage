import itertools
from typing import List
from models.bet import Bet
from models.combination import Combination

def generate_combinations(bets: List[Bet], strategy_type: str, risk_preference: str, folds: int = None, max_combination_size: int = None) -> List[Combination]:
    """Generate bet combinations based on the strategy type."""
    combinations = []
    if strategy_type == "System":
        max_size = folds or max_combination_size or len(bets)
        min_size = {
            "Conservative": 1,
            "Moderate": 2,
            "Aggressive": 3
        }.get(risk_preference, 2)
        for r in range(min_size, max_size + 1):
            combinations.extend([Combination(list(combo)) for combo in itertools.combinations(bets, r)])
    else:
        combinations = [Combination(bets)]
    return combinations
