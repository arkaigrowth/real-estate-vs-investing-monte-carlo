"""Statistical utilities for percentiles and probability calculations."""

import numpy as np

def compute_percentiles(paths, percentiles=[10, 50, 90]):
    """Compute percentiles across paths (axis=0).
    
    Args:
        paths: (n_paths, n_months+1) array
        percentiles: List of percentiles to compute
    
    Returns:
        Dict mapping percentile to (n_months+1) array
    """
    return {p: np.percentile(paths, p, axis=0) for p in percentiles}

def probability_a_beats_b(a_paths, b_paths):
    """Compute P(A > B) at terminal time.
    
    Args:
        a_paths: (n_paths, n_months+1) array
        b_paths: (n_paths, n_months+1) array
    
    Returns:
        Float probability between 0 and 1
    """
    return np.mean(a_paths[:, -1] > b_paths[:, -1])

def max_drawdown(paths):
    """Compute maximum drawdown for each path.
    
    Args:
        paths: (n_paths, n_months+1) array
    
    Returns:
        (n_paths,) array of max drawdowns
    """
    drawdowns = np.zeros(paths.shape[0])
    for i in range(paths.shape[0]):
        cummax = np.maximum.accumulate(paths[i])
        dd = (paths[i] - cummax) / cummax
        drawdowns[i] = np.min(dd)
    return drawdowns