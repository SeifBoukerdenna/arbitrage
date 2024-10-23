def kelly_criterion(odds: float, probability: float, fraction: float = 1.0) -> float:
    """Calculate the Kelly fraction with optional scaling."""
    b = odds - 1
    p = probability
    q = 1 - p
    if b <= 0 or p <= 0 or p >= 1:
        return 0.0
    kelly = (b * p - q) / b
    return max(fraction * kelly, 0.0)
