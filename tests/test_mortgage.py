"""Tests for mortgage calculations."""

import numpy as np
import pytest
from core.mortgage import monthly_payment, amortization_schedule

def test_monthly_payment_formula():
    """Test monthly payment calculation matches expected values."""
    # Test case: $400k loan at 6% for 30 years
    principal = 400000
    rate = 0.06
    years = 30
    
    payment = monthly_payment(principal, rate, years)
    expected = 2398.20  # From mortgage calculator
    
    assert abs(payment - expected) < 1.0, f"Payment {payment} != {expected}"

def test_monthly_payment_zero_rate():
    """Test payment calculation with 0% interest."""
    principal = 360000
    rate = 0
    years = 30
    
    payment = monthly_payment(principal, rate, years)
    expected = principal / (years * 12)
    
    assert abs(payment - expected) < 0.01

def test_amortization_schedule_sums():
    """Test that amortization schedule sums correctly."""
    principal = 400000
    rate = 0.06
    years = 30
    
    interest, principal_pay, balance = amortization_schedule(principal, rate, years)
    
    # Total principal payments should equal loan amount
    assert abs(np.sum(principal_pay) - principal) < 1.0
    
    # Final balance should be ~0
    assert abs(balance[-1]) < 1.0
    
    # Payment should equal interest + principal each month
    payment = monthly_payment(principal, rate, years)
    for i in range(len(interest)):
        assert abs((interest[i] + principal_pay[i]) - payment) < 0.01

def test_amortization_first_payment():
    """Test that first payment matches formula."""
    principal = 400000
    rate = 0.06
    years = 30
    
    payment = monthly_payment(principal, rate, years)
    interest, principal_pay, balance = amortization_schedule(principal, rate, years)
    
    # First month interest
    expected_interest = principal * (rate / 12)
    assert abs(interest[0] - expected_interest) < 0.01
    
    # First month principal
    expected_principal = payment - expected_interest
    assert abs(principal_pay[0] - expected_principal) < 0.01