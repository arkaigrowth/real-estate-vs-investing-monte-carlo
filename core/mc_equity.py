"""Equity GBM simulation with variable contributions and fee drag."""

import numpy as np

def simulate_equity_portfolio(initial_value, contributions, mu, sigma, fee, n_months, n_paths, rng):
    """Simulate equity portfolio with monthly GBM and variable contributions.
    
    Args:
        initial_value: Starting portfolio value
        contributions: (n_paths, n_months) array of monthly contributions
        mu: Annual return
        sigma: Annual volatility
        fee: Annual expense ratio
        n_months: Number of months
        n_paths: Number of paths
        rng: Random number generator
    
    Returns:
        (n_paths, n_months+1) array with initial value at t=0
    """
    dt = 1/12
    paths = np.zeros((n_paths, n_months + 1))
    paths[:, 0] = initial_value
    
    # Adjust for fees
    mu_adj = mu - fee
    
    # Monthly returns
    z = rng.standard_normal((n_paths, n_months))
    returns = np.exp((mu_adj - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)
    
    # Apply returns and contributions
    for t in range(n_months):
        # Growth from returns
        paths[:, t + 1] = paths[:, t] * returns[:, t]
        # Add contributions
        paths[:, t + 1] += contributions[:, t]
    
    return paths