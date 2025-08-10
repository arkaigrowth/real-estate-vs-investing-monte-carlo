"""Home value GBM simulation."""

import numpy as np

def simulate_home_values(initial_price, mu, sigma, n_months, n_paths, rng):
    """Simulate home values using monthly GBM.
    
    Returns: (n_paths, n_months+1) array with initial value at t=0.
    """
    dt = 1/12
    paths = np.zeros((n_paths, n_months + 1))
    paths[:, 0] = initial_price
    
    # Monthly returns
    z = rng.standard_normal((n_paths, n_months))
    returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)
    
    # Compound returns
    for t in range(n_months):
        paths[:, t + 1] = paths[:, t] * returns[:, t]
    
    return paths