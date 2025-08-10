"""Streamlit app for Invest vs Buy Monte Carlo simulation."""

import streamlit as st
import numpy as np
from core.presets import get_city_defaults
from core.compose import compose_invest_vs_buy
from core.stats import probability_a_beats_b
from charts.timeseries import create_net_worth_chart

st.set_page_config(
    page_title="Invest vs Buy Monte Carlo",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Real Estate vs Investing: Monte Carlo Simulation")
st.markdown("Interactive simulator comparing **Invest** vs **Buy** strategies with fair cashflow model")

# Initialize session state for baseline snapshot
if "baseline_snapshot" not in st.session_state:
    st.session_state.baseline_snapshot = None
if "baseline_params" not in st.session_state:
    st.session_state.baseline_params = None

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    # City presets
    st.subheader("📍 City Presets")
    city = st.selectbox(
        "Select City",
        ["Global Defaults", "Chicago", "Tampa"],
        help="Load city-specific defaults for home prices, rent, and growth rates"
    )
    
    city_name = None if city == "Global Defaults" else city
    params = get_city_defaults(city_name)
    
    # Basic parameters
    st.subheader("💰 Financial Inputs")
    
    params["monthly_savings"] = st.slider(
        "Monthly Savings Budget ($)",
        1000, 15000, params["monthly_savings"], 500,
        help="Total monthly budget available for housing + investing"
    )
    
    params["rent"] = st.slider(
        "Monthly Rent ($)",
        500, 10000, params["rent"], 100,
        help="Monthly rent payment for Invest strategy"
    )
    
    params["home_price"] = st.slider(
        "Home Price ($)",
        100000, 2000000, params["home_price"], 10000,
        help="Purchase price of the home"
    )
    
    # Loan parameters
    st.subheader("🏦 Mortgage Settings")
    
    params["loan_type"] = st.radio(
        "Loan Type",
        ["FHA", "Conventional"],
        help="FHA: Lower down payment with MIP | Conventional: Higher down with PMI"
    )
    
    if params["loan_type"] == "FHA":
        params["down_payment_pct"] = st.slider(
            "Down Payment (%)",
            3.5, 20.0, 3.5, 0.5,
            help="FHA minimum is 3.5%"
        ) / 100
        
        params["mip_finance_upfront"] = st.checkbox(
            "Finance Upfront MIP",
            value=True,
            help="Roll 1.75% upfront MIP into loan (vs pay cash at closing)"
        )
    else:
        params["down_payment_pct"] = st.slider(
            "Down Payment (%)",
            5.0, 30.0, 20.0, 1.0,
            help="Conventional: PMI required if <20% down"
        ) / 100
    
    params["mortgage_rate"] = st.slider(
        "Mortgage Rate (%)",
        3.0, 10.0, 6.5, 0.1,
        help="Annual mortgage interest rate"
    ) / 100
    
    # Return assumptions
    st.subheader("📈 Return Assumptions")
    
    col1, col2 = st.columns(2)
    with col1:
        params["equity_mu"] = st.slider(
            "Equity Return (%)",
            0.0, 15.0, 7.0, 0.5,
            help="Annual expected equity return"
        ) / 100
        
        params["home_mu"] = st.slider(
            "Home Appreciation (%)",
            0.0, 10.0, 4.0, 0.5,
            help="Annual home price appreciation"
        ) / 100
    
    with col2:
        params["equity_sigma"] = st.slider(
            "Equity Volatility (%)",
            5.0, 30.0, 15.0, 1.0,
            help="Annual equity volatility"
        ) / 100
        
        params["home_sigma"] = st.slider(
            "Home Volatility (%)",
            2.0, 20.0, 10.0, 1.0,
            help="Annual home price volatility"
        ) / 100
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        params["years"] = st.slider("Time Horizon (years)", 10, 40, 30, 5)
        params["n_paths"] = st.slider("Simulation Paths", 1000, 10000, 5000, 1000)
        params["seed"] = st.number_input("Random Seed", 0, 10000, 42)
        
        params["property_tax_rate"] = st.slider(
            "Property Tax Rate (%)", 0.5, 3.0, 1.5, 0.1
        ) / 100
        
        params["insurance_rate"] = st.slider(
            "Insurance Rate (%)", 0.2, 1.0, 0.4, 0.05
        ) / 100
        
        params["maintenance_rate"] = st.slider(
            "Maintenance Rate (%)", 0.5, 2.0, 1.0, 0.1
        ) / 100
        
        params["hoa_monthly"] = st.slider(
            "HOA Monthly ($)", 0, 500, 100, 25
        )
        
        params["selling_cost_rate"] = st.slider(
            "Selling Costs (%)", 0.0, 10.0, 7.0, 0.5,
            help="Realtor fees, closing costs, etc. at sale"
        ) / 100
        
        params["rent_growth"] = st.slider(
            "Rent Growth Rate (%)", 0.0, 5.0, 3.0, 0.25
        ) / 100
        
        params["cpi"] = st.slider(
            "CPI Inflation (%)", 0.0, 5.0, 2.5, 0.25,
            help="For real dollar calculations"
        ) / 100
        
        params["equity_fee"] = st.slider(
            "Equity Fee (%)", 0.0, 2.0, 0.15, 0.05,
            help="Annual expense ratio for equity portfolio"
        ) / 100
    
    # Display options
    st.subheader("📊 Display Options")
    
    params["tax_basis"] = st.radio(
        "Property Tax Basis",
        ["current", "original"],
        format_func=lambda x: "Current Value" if x == "current" else "Original Price",
        help="Calculate property tax on current value or original purchase price"
    )
    
    params["show_real"] = st.checkbox(
        "Show Real Dollars",
        help="Adjust for inflation using CPI"
    )
    
    # City overlay
    show_city_overlay = st.checkbox(
        "Show City Comparison",
        help="Overlay Chicago and Tampa medians"
    )
    
    # Baseline snapshot
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📸 Snapshot A", use_container_width=True):
            results = compose_invest_vs_buy(params)
            st.session_state.baseline_snapshot = {
                "invest_p50": np.percentile(results["invest_paths"], 50, axis=0),
                "buy_p50": np.percentile(results["buy_paths"], 50, axis=0)
            }
            st.session_state.baseline_params = params.copy()
            st.success("Baseline saved!")
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.baseline_snapshot = None
            st.session_state.baseline_params = None
            st.success("Baseline cleared!")

# Run simulation
results = compose_invest_vs_buy(params)

# Calculate city overlays if requested
city_data = None
if show_city_overlay:
    city_data = {}
    for city_name in ["Chicago", "Tampa"]:
        city_params = get_city_defaults(city_name)
        # Use same financial params but city-specific housing
        city_params.update({
            "monthly_savings": params["monthly_savings"],
            "equity_mu": params["equity_mu"],
            "equity_sigma": params["equity_sigma"],
            "equity_fee": params["equity_fee"],
            "years": params["years"],
            "n_paths": params["n_paths"],
            "seed": params["seed"] + hash(city_name) % 1000,
            "loan_type": params["loan_type"],
            "down_payment_pct": params["down_payment_pct"],
            "mortgage_rate": params["mortgage_rate"],
            "selling_cost_rate": params["selling_cost_rate"],
            "tax_basis": params["tax_basis"],
            "show_real": params["show_real"]
        })
        city_results = compose_invest_vs_buy(city_params)
        city_data[city_name] = {
            "invest": city_results["invest_paths"],
            "buy": city_results["buy_paths"]
        }

# Display results
col1, col2, col3 = st.columns(3)

with col1:
    prob = probability_a_beats_b(results["invest_paths"], results["buy_paths"])
    st.metric(
        "P(Invest > Buy)",
        f"{prob:.1%}",
        help="Probability that Invest beats Buy at terminal time"
    )

with col2:
    invest_terminal = np.percentile(results["invest_paths"][:, -1], 50)
    buy_terminal = np.percentile(results["buy_paths"][:, -1], 50)
    
    if params["show_real"]:
        deflator = (1 + params["cpi"]) ** (-params["years"])
        invest_terminal *= deflator
        buy_terminal *= deflator
    
    st.metric(
        "Invest P50 (Terminal)",
        f"${invest_terminal:,.0f}",
        f"${invest_terminal - buy_terminal:+,.0f}" if st.session_state.baseline_snapshot else None
    )

with col3:
    st.metric(
        "Buy P50 (Terminal)",
        f"${buy_terminal:,.0f}",
        f"${buy_terminal - invest_terminal:+,.0f}" if st.session_state.baseline_snapshot else None
    )

# Display baseline delta if snapshot exists
if st.session_state.baseline_snapshot:
    st.info(f"📸 Comparing to baseline snapshot (ΔInvest: ${invest_terminal - st.session_state.baseline_snapshot['invest_p50'][-1]:+,.0f}, ΔBuy: ${buy_terminal - st.session_state.baseline_snapshot['buy_p50'][-1]:+,.0f})")

# Create and display chart
fig = create_net_worth_chart(
    results["invest_paths"],
    results["buy_paths"],
    params,
    st.session_state.baseline_snapshot,
    city_data
)

st.plotly_chart(fig, use_container_width=True)

# Additional metrics
with st.expander("📊 Additional Metrics"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Invest Strategy")
        st.write(f"Initial investment (parity): ${results['closing_costs']:,.0f}")
        st.write(f"Average monthly contribution: ${np.mean(np.maximum(0, params['monthly_savings'] - params['rent'])):,.0f}")
        
    with col2:
        st.subheader("Buy Strategy")
        st.write(f"Down payment: ${params['home_price'] * params['down_payment_pct']:,.0f}")
        st.write(f"Monthly P&I payment: ${results['payment']:,.0f}")
        st.write(f"Terminal home equity P50: ${np.percentile(results['home_equity'][:, -1], 50):,.0f}")