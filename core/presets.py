"""City defaults and global settings."""

GLOBAL_DEFAULTS = {
    "n_paths": 5000,
    "years": 30,
    "seed": 42,
    "monthly_savings": 5000,
    "rent": 2500,
    "home_price": 500000,
    "equity_mu": 0.07,
    "equity_sigma": 0.15,
    "equity_fee": 0.0015,
    "home_mu": 0.04,
    "home_sigma": 0.10,
    "cpi": 0.025,
    "mortgage_rate": 0.065,
    "property_tax_rate": 0.015,
    "insurance_rate": 0.004,
    "maintenance_rate": 0.01,
    "hoa_monthly": 100,
    "selling_cost_rate": 0.07,
    "rent_growth": 0.03,
    "loan_type": "FHA",
    "down_payment_pct": 0.035,
    "pmi_rate": 0.005,
    "pmi_remove_ltv": 0.78,
    "mip_rate": 0.0085,
    "mip_upfront": 0.0175,
    "mip_finance_upfront": True,
    "mip_remove_ltv": None,
    "tax_basis": "current",
    "show_real": False,
    "baseline_snapshot": None,
    "city_overlay": None
}

CHICAGO_DEFAULTS = {
    "home_price": 450000,
    "rent": 2200,
    "home_mu": 0.035,
    "home_sigma": 0.08,
    "property_tax_rate": 0.018,
    "insurance_rate": 0.0045,
    "hoa_monthly": 150,
    "rent_growth": 0.025
}

TAMPA_DEFAULTS = {
    "home_price": 400000,
    "rent": 2000,
    "home_mu": 0.05,
    "home_sigma": 0.12,
    "property_tax_rate": 0.012,
    "insurance_rate": 0.006,
    "hoa_monthly": 75,
    "rent_growth": 0.035
}

def get_city_defaults(city=None):
    """Return defaults for a specific city or global defaults."""
    defaults = GLOBAL_DEFAULTS.copy()
    if city == "Chicago":
        defaults.update(CHICAGO_DEFAULTS)
    elif city == "Tampa":
        defaults.update(TAMPA_DEFAULTS)
    return defaults