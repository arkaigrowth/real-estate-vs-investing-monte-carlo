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

# Add expandable help section
with st.expander("ℹ️ What is Monte Carlo Simulation?"):
    st.markdown("""
    **Monte Carlo simulation** runs thousands of possible future scenarios using random market returns within realistic ranges.
    
    **Why use it?** The future is uncertain! Instead of one "average" projection, we show you the range of possible outcomes:
    
    - **P90 (Optimistic)**: Only 10% of simulations did better than this - your "lucky" scenario
    - **P50 (Median)**: The middle outcome - your "typical" scenario  
    - **P10 (Pessimistic)**: Only 10% of simulations did worse - your "unlucky" scenario
    
    **The shaded bands** show you the uncertainty. Wider bands = more risk/volatility.
    
    **Example**: If Invest P50 is $2M and Buy P50 is $1.8M, the typical investing outcome beats buying by $200k, 
    but look at the P10 values to understand downside risk!
    """)

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
    
    # Fairness Model Settings
    st.subheader("⚖️ Fairness Model")
    
    params["enforce_parity"] = st.checkbox(
        "Enforce Down-Payment Parity",
        value=True,
        help="When checked, Invest gets same initial cash as Buy's closing costs (fair comparison). Uncheck to set custom initial investment."
    )
    
    if not params["enforce_parity"]:
        params["invest_initial"] = st.number_input(
            "Initial Investment Amount ($)",
            min_value=0,
            max_value=1000000,
            value=params.get("invest_initial", 50000),
            step=5000,
            help="Custom starting amount for Invest strategy (when parity is disabled)"
        )
    
    # Loan parameters
    st.subheader("🏦 Mortgage Settings")
    
    params["loan_type"] = st.radio(
        "Loan Type",
        ["FHA", "Conventional"],
        help="FHA: Lower down payment with MIP | Conventional: Higher down with PMI"
    )
    
    if params["loan_type"] == "FHA":
        # Get default value correctly (it's stored as decimal, display as percentage)
        default_down = params.get("down_payment_pct", 0.035) * 100 if params.get("down_payment_pct", 0.035) < 1 else params.get("down_payment_pct", 3.5)
        params["down_payment_pct"] = st.slider(
            "Down Payment (%)",
            3.5, 20.0, default_down, 0.5,
            help="FHA minimum is 3.5%"
        ) / 100
        
        col1, col2 = st.columns(2)
        with col1:
            # Handle both decimal and percentage formats
            default_mip = params.get("mip_rate", 0.0085)
            default_mip = default_mip * 100 if default_mip < 1 else default_mip
            params["mip_rate"] = st.slider(
                "Annual MIP (%)",
                0.0, 1.5, default_mip, 0.05,
                help="FHA annual mortgage insurance premium"
            ) / 100
            
            default_upfront = params.get("mip_upfront", 0.0175)
            default_upfront = default_upfront * 100 if default_upfront < 1 else default_upfront
            params["mip_upfront"] = st.slider(
                "Upfront MIP (%)",
                0.0, 3.0, default_upfront, 0.25,
                help="FHA upfront mortgage insurance premium"
            ) / 100
        
        with col2:
            params["mip_finance_upfront"] = st.checkbox(
                "Finance Upfront MIP",
                value=params.get("mip_finance_upfront", True),
                help="Roll upfront MIP into loan (vs pay cash at closing)"
            )
            
            # MIP removal option (usually life of loan for FHA)
            remove_mip = st.checkbox(
                "MIP Removable",
                value=params.get("mip_remove_ltv") is not None,
                help="Can MIP be removed (rare for FHA)"
            )
            if remove_mip:
                params["mip_remove_ltv"] = st.slider(
                    "MIP Remove LTV",
                    0.5, 0.9, params.get("mip_remove_ltv", 0.78), 0.01,
                    help="LTV threshold for MIP removal"
                )
            else:
                params["mip_remove_ltv"] = None
    else:
        # Conventional loan
        default_down_conv = params.get("down_payment_pct", 0.20)
        default_down_conv = default_down_conv * 100 if default_down_conv < 1 else default_down_conv
        params["down_payment_pct"] = st.slider(
            "Down Payment (%)",
            5.0, 30.0, default_down_conv, 1.0,
            help="Conventional: PMI required if <20% down"
        ) / 100
        
        # Only show PMI settings if down payment < 20%
        if params["down_payment_pct"] < 0.20:
            col1, col2 = st.columns(2)
            with col1:
                default_pmi = params.get("pmi_rate", 0.005)
                default_pmi = default_pmi * 100 if default_pmi < 1 else default_pmi
                params["pmi_rate"] = st.slider(
                    "Annual PMI (%)",
                    0.0, 1.5, default_pmi, 0.05,
                    help="Private mortgage insurance rate"
                ) / 100
            
            with col2:
                params["pmi_remove_ltv"] = st.slider(
                    "PMI Remove LTV",
                    0.70, 0.80, params.get("pmi_remove_ltv", 0.78), 0.01,
                    help="LTV threshold where PMI is removed"
                )
        else:
            # No PMI needed with >= 20% down
            params["pmi_rate"] = 0
            params["pmi_remove_ltv"] = 0.78  # Won't be used but set a default
    
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
        
        params["income_growth"] = st.slider(
            "Income Growth Rate (%)", 0.0, 5.0, 2.0, 0.25,
            help="Annual salary/income growth rate (raises, promotions, etc.)"
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

# Display results with explanatory section
st.info("""
**📊 Understanding the Chart:**
- **P50 (Median)**: The middle outcome - 50% of simulations do better, 50% do worse. This is your "typical" scenario.
- **P10-P90 Band**: The range covering 80% of possible outcomes. P10 means only 10% of simulations did worse, P90 means 90% did worse.
- **Wider bands = More uncertainty**: Investing typically has wider bands due to market volatility.
""")

col1, col2, col3 = st.columns(3)

with col1:
    prob = probability_a_beats_b(results["invest_paths"], results["buy_paths"])
    st.metric(
        "P(Invest > Buy)",
        f"{prob:.1%}",
        help="Percentage of simulations where investing beats buying at the end. >50% favors investing, <50% favors buying."
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
        f"${invest_terminal - buy_terminal:+,.0f}" if st.session_state.baseline_snapshot else None,
        help="Median (P50) terminal value for investing. Half of simulations end up above this, half below."
    )

with col3:
    st.metric(
        "Buy P50 (Terminal)",
        f"${buy_terminal:,.0f}",
        f"${buy_terminal - invest_terminal:+,.0f}" if st.session_state.baseline_snapshot else None,
        help="Median (P50) terminal value for buying. Half of simulations end up above this, half below."
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
        if params.get("enforce_parity", True):
            st.write(f"Initial investment (parity): ${results['closing_costs']:,.0f}")
        else:
            actual_initial = params.get("invest_initial", results['closing_costs'])
            st.write(f"Initial investment (custom): ${actual_initial:,.0f}")
            st.write(f"  vs Buy closing costs: ${results['closing_costs']:,.0f}")
        
        # Calculate actual average contribution from simulation results
        avg_invest_contrib = np.mean(results['invest_contributions'])
        st.metric(
            label="Average monthly contribution",
            value=f"${avg_invest_contrib:,.0f}",
            help="Average of all monthly contributions over time. As rent grows, less money is available to invest. When rent exceeds your budget, contributions become $0. With income growth enabled, your budget also increases over time."
        )
        
        # Show rent growth impact
        initial_rent = params['rent']
        final_rent = initial_rent * (1 + params.get('rent_growth', 0.03)) ** params['years']
        st.write(f"Rent: ${initial_rent:,.0f} → ${final_rent:,.0f}")
        
    with col2:
        st.subheader("Buy Strategy")
        st.write(f"Down payment: ${params['home_price'] * params['down_payment_pct']:,.0f}")
        if params["loan_type"] == "FHA" and not params.get("mip_finance_upfront", True):
            upfront_mip = (params["home_price"] - params["home_price"] * params["down_payment_pct"]) * params.get("mip_upfront", 0.0175)
            st.write(f"Upfront MIP (cash): ${upfront_mip:,.0f}")
            st.write(f"Total closing costs: ${results['closing_costs']:,.0f}")
        else:
            st.write(f"Total closing costs: ${results['closing_costs']:,.0f}")
        
        st.write(f"Monthly P&I payment: ${results['payment']:,.0f}")
        
        # Calculate actual average housing costs and liquid contribution
        avg_housing_outflow = np.mean(results['housing_outflow'])
        avg_buy_contrib = np.mean(results['buy_contributions'])
        st.write(f"Avg housing costs: ${avg_housing_outflow:,.0f}")
        st.write(f"Avg liquid contribution: ${avg_buy_contrib:,.0f}")
        
        st.write(f"Terminal home equity P50: ${np.percentile(results['home_equity'][:, -1], 50):,.0f}")