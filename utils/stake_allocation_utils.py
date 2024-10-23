from models.betting_strategy import BettingStrategy
from .kelly_criterion import kelly_criterion


def allocate_stakes(strategy: BettingStrategy, margin: float = 0.05):
    """Allocate stakes to each combination based on the Kelly Criterion and risk preference."""
    total_budget = strategy.total_budget

    # Adjust Kelly fraction based on risk preference
    risk_fraction = {
        "Conservative": 0.25,
        "Moderate": 0.5,
        "Aggressive": 1.0
    }.get(strategy.risk_preference, 0.5)

    total_kelly_fraction = 0.0

    for combo in strategy.combinations:
        adjusted_odds = combo.combined_odds * (1 - margin)
        combo.adjusted_odds = adjusted_odds
        combo.kelly_fraction = kelly_criterion(adjusted_odds, combo.combined_prob, fraction=risk_fraction)
        total_kelly_fraction += combo.kelly_fraction

    if total_kelly_fraction == 0:
        stakes = [0.0 for _ in strategy.combinations]
    else:
        stakes = [(combo.kelly_fraction / total_kelly_fraction) * total_budget for combo in strategy.combinations]

    strategy.stake_allocation = stakes
