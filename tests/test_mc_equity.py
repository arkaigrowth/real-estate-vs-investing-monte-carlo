"""Tests for equity portfolio simulation."""

import numpy as np
import pytest
from core.mc_equity import simulate_equity_portfolio

def test_zero_returns_with_contributions():
    """Test that with mu=sigma=0, portfolio equals sum of contributions."""
    n_paths = 100
    n_months = 12
    initial = 10000
    rng = np.random.RandomState(42)
    
    # Constant contributions
    contributions = np.full((n_paths, n_months), 1000)
    
    paths = simulate_equity_portfolio(
        initial, contributions, 
        mu=0, sigma=0, fee=0,
        n_months=n_months, n_paths=n_paths, rng=rng
    )
    
    # Should be initial + sum of contributions
    expected_final = initial + n_months * 1000
    assert np.allclose(paths[:, -1], expected_final, rtol=1e-10)

def test_variable_contributions():
    """Test that variable contributions are properly added."""
    n_paths = 10
    n_months = 6
    initial = 5000
    rng = np.random.RandomState(42)
    
    # Variable contributions
    contributions = np.arange(n_months).reshape(1, -1) * 100
    contributions = np.tile(contributions, (n_paths, 1))
    
    paths = simulate_equity_portfolio(
        initial, contributions,
        mu=0, sigma=0, fee=0,
        n_months=n_months, n_paths=n_paths, rng=rng
    )
    
    # With no growth, should be initial + cumsum of contributions
    expected = initial + np.sum(contributions[0])
    assert np.allclose(paths[:, -1], expected, rtol=1e-10)

def test_fee_drag():
    """Test that fees reduce returns."""
    n_paths = 1000
    n_months = 120  # 10 years
    initial = 100000
    rng = np.random.RandomState(42)
    
    contributions = np.zeros((n_paths, n_months))
    
    # Without fees
    paths_no_fee = simulate_equity_portfolio(
        initial, contributions,
        mu=0.07, sigma=0.15, fee=0,
        n_months=n_months, n_paths=n_paths, rng=rng
    )
    
    # With fees
    rng = np.random.RandomState(42)  # Same seed
    paths_with_fee = simulate_equity_portfolio(
        initial, contributions,
        mu=0.07, sigma=0.15, fee=0.01,
        n_months=n_months, n_paths=n_paths, rng=rng
    )
    
    # Average terminal value should be lower with fees
    assert np.mean(paths_with_fee[:, -1]) < np.mean(paths_no_fee[:, -1])

def test_deterministic_seed():
    """Test that same seed produces same results."""
    n_paths = 100
    n_months = 60
    initial = 50000
    contributions = np.full((n_paths, n_months), 1000)
    
    # First run
    rng1 = np.random.RandomState(42)
    paths1 = simulate_equity_portfolio(
        initial, contributions,
        mu=0.08, sigma=0.16, fee=0.0015,
        n_months=n_months, n_paths=n_paths, rng=rng1
    )
    
    # Second run with same seed
    rng2 = np.random.RandomState(42)
    paths2 = simulate_equity_portfolio(
        initial, contributions,
        mu=0.08, sigma=0.16, fee=0.0015,
        n_months=n_months, n_paths=n_paths, rng=rng2
    )
    
    assert np.allclose(paths1, paths2)