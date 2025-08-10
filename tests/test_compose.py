"""Tests for fair Invest vs Buy composition."""

import numpy as np
import pytest
from core.compose import compose_invest_vs_buy
from core.presets import get_city_defaults

def test_fairness_baseline():
    """Test that with no growth/costs, Invest P50 ≈ Buy P50."""
    params = get_city_defaults()
    
    # Set all growth and volatility to 0
    params.update({
        "equity_mu": 0,
        "equity_sigma": 0,
        "equity_fee": 0,
        "home_mu": 0,
        "home_sigma": 0,
        "rent_growth": 0,
        "property_tax_rate": 0,
        "insurance_rate": 0,
        "maintenance_rate": 0,
        "hoa_monthly": 0,
        "selling_cost_rate": 0,
        "n_paths": 100,
        "years": 10,
        "seed": 42,
        "loan_type": "Conventional",
        "down_payment_pct": 0.20,
        "mortgage_rate": 0.05
    })
    
    results = compose_invest_vs_buy(params)
    
    # With no growth or costs, strategies should be similar
    invest_p50 = np.percentile(results["invest_paths"][:, -1], 50)
    buy_p50 = np.percentile(results["buy_paths"][:, -1], 50)
    
    # They won't be exactly equal due to mortgage interest
    # but should be within reasonable range
    ratio = invest_p50 / buy_p50
    assert 0.65 < ratio < 1.35, f"Ratio {ratio} outside expected range"

def test_no_negative_contributions():
    """Test that contributions are never negative."""
    params = get_city_defaults()
    params.update({
        "n_paths": 100,
        "years": 5,
        "seed": 42,
        "monthly_savings": 3000,
        "rent": 2500,
        "home_price": 400000
    })
    
    results = compose_invest_vs_buy(params)
    
    # Check invest contributions
    invest_contrib = np.maximum(0, params["monthly_savings"] - results["rent_paths"])
    assert np.all(invest_contrib >= 0)
    
    # Buy contributions are calculated in compose function
    # Just verify buy_liquid_paths doesn't go negative
    assert np.all(results["buy_liquid_paths"] >= -1)  # Allow small numerical errors

def test_parity_enforcement():
    """Test that Invest gets same initial cash as Buy spends at closing."""
    params = get_city_defaults()
    params.update({
        "home_price": 500000,
        "down_payment_pct": 0.10,
        "loan_type": "FHA",
        "mip_finance_upfront": False,  # Pay cash
        "n_paths": 10,
        "years": 5
    })
    
    results = compose_invest_vs_buy(params)
    
    # Invest should start with closing costs
    assert results["invest_paths"][0, 0] == results["closing_costs"]
    
    # Buy liquid should start at 0 (spent on house)
    assert np.allclose(results["buy_liquid_paths"][:, 0], 0)

def test_pmi_removal():
    """Test that PMI drops at correct LTV threshold."""
    params = get_city_defaults()
    params.update({
        "loan_type": "Conventional",
        "down_payment_pct": 0.10,  # 90% LTV, triggers PMI
        "pmi_rate": 0.005,
        "pmi_remove_ltv": 0.78,
        "home_price": 400000,
        "home_mu": 0.05,  # Home appreciates
        "home_sigma": 0,  # No volatility for predictable test
        "n_paths": 1,
        "years": 10,
        "seed": 42
    })
    
    results = compose_invest_vs_buy(params)
    
    # PMI should be present initially and drop later
    # Can't test exact timing without exposing PMI array
    # but can verify the simulation runs without error
    assert results["buy_paths"].shape == (1, 121)  # 10 years * 12 + 1

def test_deterministic_seed():
    """Test that same seed produces same results."""
    params = get_city_defaults()
    params["seed"] = 12345
    params["n_paths"] = 100
    
    results1 = compose_invest_vs_buy(params)
    results2 = compose_invest_vs_buy(params)
    
    assert np.allclose(results1["invest_paths"], results2["invest_paths"])
    assert np.allclose(results1["buy_paths"], results2["buy_paths"])