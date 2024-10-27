import numpy as np
from scipy.optimize import minimize
from models.betting_strategy import BettingStrategy

def allocate_stakes(strategy: BettingStrategy):
    """Allocate stakes using Mean-Variance Optimization."""
    returns = np.array([combo.ev_per_dollar for combo in strategy.combinations])
    probabilities = np.array([combo.combined_prob for combo in strategy.combinations])

    # Calculate covariance matrix (assuming independence)
    covariance_matrix = np.diag(probabilities * (1 - probabilities))

    # Objective function: minimize negative expected return adjusted for risk
    def objective(weights):
        portfolio_return = np.dot(weights, returns)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        # Risk aversion parameter
        risk_aversion = {
            "Conservative": 5.0,
            "Moderate": 2.5,
            "Aggressive": 1.0
        }.get(strategy.risk_preference, 2.5)
        return -portfolio_return + risk_aversion * portfolio_variance

    # Constraints: weights sum to 1, weights >= 0
    constraints = [{'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}]
    bounds = [(0, 1) for _ in strategy.combinations]
    initial_guess = np.array([1.0 / len(strategy.combinations)] * len(strategy.combinations))

    result = minimize(objective, initial_guess, bounds=bounds, constraints=constraints)

    if not result.success:
        raise ValueError("Optimization failed: " + result.message)

    weights = result.x
    strategy.stake_allocation = weights * strategy.total_budget
