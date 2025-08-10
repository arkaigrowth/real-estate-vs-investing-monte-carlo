"""P&I payment and amortization helpers."""

import numpy as np

def monthly_payment(principal, annual_rate, years):
    """Calculate monthly P&I payment."""
    if annual_rate == 0:
        return principal / (years * 12)
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)

def amortization_schedule(principal, annual_rate, years):
    """Return monthly interest, principal payments, and remaining balance arrays."""
    n_months = years * 12
    payment = monthly_payment(principal, annual_rate, years)
    
    if annual_rate == 0:
        principal_payments = np.full(n_months, payment)
        interest_payments = np.zeros(n_months)
        balance = np.linspace(principal, 0, n_months + 1)[:-1]
        return interest_payments, principal_payments, balance
    
    r = annual_rate / 12
    interest_payments = np.zeros(n_months)
    principal_payments = np.zeros(n_months)
    balance = np.zeros(n_months)
    
    remaining = principal
    for i in range(n_months):
        interest = remaining * r
        principal_pay = payment - interest
        interest_payments[i] = interest
        principal_payments[i] = principal_pay
        remaining -= principal_pay
        balance[i] = max(0, remaining)
    
    return interest_payments, principal_payments, balance