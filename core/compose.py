"""Fair Invest vs Buy composition logic."""

import numpy as np
from .mortgage import monthly_payment, amortization_schedule
from .housing import simulate_home_values
from .mc_equity import simulate_equity_portfolio

def compose_invest_vs_buy(params):
    """Compose fair Invest vs Buy simulation.
    
    Returns dict with invest_paths, buy_paths, rent_paths, and metadata.
    """
    # Extract parameters
    n_paths = params["n_paths"]
    n_months = params["years"] * 12
    rng = np.random.RandomState(params["seed"])
    
    # Calculate down payment and closing costs
    down_payment = params["home_price"] * params["down_payment_pct"]
    loan_amount = params["home_price"] - down_payment
    
    # Handle upfront MIP for FHA loans
    upfront_mip = 0
    if params["loan_type"] == "FHA":
        upfront_mip = loan_amount * params["mip_upfront"]
        if params["mip_finance_upfront"]:
            loan_amount += upfront_mip
            upfront_mip = 0  # Financed, not paid upfront
    
    # Total closing costs (down payment + any upfront MIP if paying cash)
    closing_costs = down_payment + upfront_mip
    
    # Simulate home values
    home_paths = simulate_home_values(
        params["home_price"], 
        params["home_mu"], 
        params["home_sigma"],
        n_months, 
        n_paths, 
        rng
    )
    
    # Calculate mortgage payment and amortization
    payment = monthly_payment(loan_amount, params["mortgage_rate"], params["years"])
    interest_payments, principal_payments, balance = amortization_schedule(
        loan_amount, 
        params["mortgage_rate"], 
        params["years"]
    )
    
    # Calculate property taxes based on tax basis setting
    if params["tax_basis"] == "current":
        # Tax based on current home value
        property_tax = home_paths[:, :-1] * (params["property_tax_rate"] / 12)
    else:
        # Tax based on original price
        property_tax = np.full((n_paths, n_months), 
                              params["home_price"] * params["property_tax_rate"] / 12)
    
    # Other housing costs
    insurance = home_paths[:, :-1] * (params["insurance_rate"] / 12)
    maintenance = home_paths[:, :-1] * (params["maintenance_rate"] / 12)
    hoa = np.full((n_paths, n_months), params["hoa_monthly"])
    
    # Income/savings paths (accounting for salary growth)
    monthly_savings = params["monthly_savings"]
    income_growth = params.get("income_growth", 0)  # Default to 0 if not specified
    savings_paths = np.zeros((n_paths, n_months))
    for t in range(n_months):
        savings_paths[:, t] = monthly_savings * (1 + income_growth) ** (t / 12)
    
    # Calculate PMI/MIP
    pmi_mip = np.zeros((n_paths, n_months))
    if params["loan_type"] == "FHA":
        # FHA MIP
        for t in range(n_months):
            if params.get("mip_remove_ltv") is None or balance[t] / home_paths[:, t] > params.get("mip_remove_ltv"):
                pmi_mip[:, t] = balance[t] * (params.get("mip_rate", 0.0085) / 12)
    else:
        # Conventional PMI  
        for t in range(n_months):
            ltv = balance[t] / home_paths[:, t]
            # Check if any path needs PMI
            needs_pmi = ltv > params.get("pmi_remove_ltv", 0.78)
            pmi_mip[:, t] = np.where(needs_pmi, balance[t] * (params.get("pmi_rate", 0.005) / 12), 0)
    
    # Total housing outflow
    housing_outflow = (np.full((n_paths, n_months), payment) + 
                      property_tax + insurance + maintenance + hoa + pmi_mip)
    
    # Buy strategy liquid contributions (also benefits from income growth)
    buy_contributions = np.maximum(0, savings_paths - housing_outflow)
    
    # Simulate buy liquid portfolio
    buy_liquid_paths = simulate_equity_portfolio(
        0,  # Start with 0 (closing costs spent on house)
        buy_contributions,
        params["equity_mu"],
        params["equity_sigma"],
        params["equity_fee"],
        n_months,
        n_paths,
        rng
    )
    
    # Calculate home equity (value - remaining balance)
    balance_array = np.tile(balance, (n_paths, 1))
    balance_with_final = np.column_stack([balance_array, np.zeros(n_paths)])
    home_equity = home_paths - balance_with_final
    
    # Apply selling costs at terminal time if specified
    if params.get("selling_cost_rate", 0) > 0:
        selling_costs = home_paths[:, -1] * params["selling_cost_rate"]
        home_equity[:, -1] -= selling_costs
    
    # Total buy net worth
    buy_paths = buy_liquid_paths + home_equity
    
    # Rent paths
    rent = params["rent"]
    rent_growth = params.get("rent_growth", 0.03)
    rent_paths = np.zeros((n_paths, n_months))
    for t in range(n_months):
        rent_paths[:, t] = rent * (1 + rent_growth) ** (t / 12)
    
    # Invest strategy contributions (gets closing costs + monthly after rent)
    # Note: savings_paths already calculated above with income growth
    invest_contributions = np.maximum(0, savings_paths - rent_paths)
    
    # Initial investment: either parity (closing costs) or custom amount
    if params.get("enforce_parity", True):
        invest_initial = closing_costs
    else:
        invest_initial = params.get("invest_initial", closing_costs)
    
    # Simulate invest portfolio
    invest_paths = simulate_equity_portfolio(
        invest_initial,
        invest_contributions,
        params["equity_mu"],
        params["equity_sigma"],
        params["equity_fee"],
        n_months,
        n_paths,
        rng
    )
    
    return {
        "invest_paths": invest_paths,
        "buy_paths": buy_paths,
        "rent_paths": rent_paths,
        "home_paths": home_paths,
        "buy_liquid_paths": buy_liquid_paths,
        "home_equity": home_equity,
        "closing_costs": closing_costs,
        "payment": payment,
        "n_months": n_months,
        "invest_contributions": invest_contributions,
        "buy_contributions": buy_contributions,
        "housing_outflow": housing_outflow
    }