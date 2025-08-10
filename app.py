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
        help="Your total monthly budget for both housing and investing. This is the 'fair comparison' amount - both strategies get the same budget. For renters: pays rent first, remainder goes to stocks. For buyers: pays mortgage/taxes/insurance first, remainder to liquid investments. Think of this as your monthly surplus after all non-housing expenses."
    )
    
    params["rent"] = st.slider(
        "Monthly Rent ($)",
        500, 10000, params["rent"], 100,
        help="Starting monthly rent if you choose to invest instead of buy. This grows over time based on 'Rent Growth Rate'. Higher rent means less money available to invest each month. Compare this to the monthly mortgage payment to see the cashflow difference. Typically rent for a comparable home is initially lower than ownership costs but grows over time."
    )
    
    params["home_price"] = st.slider(
        "Home Price ($)",
        100000, 2000000, params["home_price"], 10000,
        help="Purchase price of the home you're considering. This determines your down payment, loan amount, property taxes, insurance, and maintenance costs. The home value will appreciate (or depreciate) randomly based on the Home Appreciation and Volatility settings. Higher price means larger down payment and monthly costs, but also more potential appreciation."
    )
    
    # Fairness Model Settings
    st.subheader("⚖️ Fairness Model")
    
    params["enforce_parity"] = st.checkbox(
        "Enforce Down-Payment Parity",
        value=True,
        help="IMPORTANT for fair comparison! When ON: The 'Invest' strategy starts with the exact same cash that 'Buy' spends at closing (down payment + closing costs). This ensures neither strategy has an unfair advantage. When OFF: You can set a custom starting amount for investing, but this may bias the comparison. Example: If buying requires $50k at closing, investing also starts with $50k."
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
        help="FHA loans: Government-backed, allowing 3.5% down but requiring mortgage insurance premium (MIP) often for the life of the loan. Good for first-time buyers with limited savings. Conventional loans: Require 5-20% down. With <20% down, you pay private mortgage insurance (PMI) until reaching 78% loan-to-value. PMI can be removed, unlike most FHA MIP."
    )
    
    if params["loan_type"] == "FHA":
        # Get default value correctly (it's stored as decimal, display as percentage)
        default_down = params.get("down_payment_pct", 0.035) * 100 if params.get("down_payment_pct", 0.035) < 1 else params.get("down_payment_pct", 3.5)
        params["down_payment_pct"] = st.slider(
            "Down Payment (%)",
            3.5, 20.0, default_down, 0.5,
            help="FHA minimum is 3.5% of home price. Lower down payment means: 1) Less cash needed upfront, 2) Higher loan amount and monthly payment, 3) More interest paid over time, 4) MIP for the life of the loan in most cases. Example: 3.5% down on $400k home = $14k down payment + $386k loan."
        ) / 100
        
        col1, col2 = st.columns(2)
        with col1:
            # Handle both decimal and percentage formats
            default_mip = params.get("mip_rate", 0.0085)
            default_mip = default_mip * 100 if default_mip < 1 else default_mip
            params["mip_rate"] = st.slider(
                "Annual MIP (%)",
                0.0, 1.5, default_mip, 0.05,
                help="FHA annual mortgage insurance premium, paid monthly as part of your payment. Typically 0.55-0.85% of loan amount per year. This protects the lender if you default. Unlike PMI, FHA MIP usually can't be removed without refinancing. Adds ~$200-300/month on a $400k loan."
            ) / 100
            
            default_upfront = params.get("mip_upfront", 0.0175)
            default_upfront = default_upfront * 100 if default_upfront < 1 else default_upfront
            params["mip_upfront"] = st.slider(
                "Upfront MIP (%)",
                0.0, 3.0, default_upfront, 0.25,
                help="FHA one-time upfront mortgage insurance premium, typically 1.75% of loan amount. You can either: 1) Finance it (add to loan balance, most common), or 2) Pay cash at closing. Financing means higher loan amount but preserves cash. Example: $7,000 on a $400k loan."
            ) / 100
        
        with col2:
            params["mip_finance_upfront"] = st.checkbox(
                "Finance Upfront MIP",
                value=params.get("mip_finance_upfront", True),
                help="When checked: Adds upfront MIP to your loan balance (most common choice). You'll pay interest on it but keep more cash at closing. When unchecked: Pay upfront MIP in cash at closing, reducing your loan amount but requiring more upfront cash. The 'fair comparison' adjusts the Invest starting amount accordingly."
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
            help="Conventional loans: 20% down avoids PMI entirely (best rate). 10-19% down requires PMI until 78% LTV. 5-9% down has higher PMI rates. More down = lower monthly payment, less interest, potential PMI avoidance. Trade-off: Less cash for investing. Example: 20% on $400k = $80k down, no PMI."
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
                    help="Private mortgage insurance rate for conventional loans with <20% down. Typically 0.3-1.0% annually. Unlike FHA MIP, PMI automatically drops off at 78% LTV (or you can request removal at 80% LTV). Higher down payment = lower PMI rate. Adds $100-400/month on typical loans."
                ) / 100
            
            with col2:
                params["pmi_remove_ltv"] = st.slider(
                    "PMI Remove LTV",
                    0.70, 0.80, params.get("pmi_remove_ltv", 0.78), 0.01,
                    help="Loan-to-value ratio where PMI is removed. By law, PMI must drop at 78% LTV (when you owe 78% of original home value). You can request removal at 80% LTV. Some lenders allow earlier removal with appraisal showing appreciation. Lower = PMI removed sooner = savings on monthly payment."
                )
        else:
            # No PMI needed with >= 20% down
            params["pmi_rate"] = 0
            params["pmi_remove_ltv"] = 0.78  # Won't be used but set a default
    
    params["mortgage_rate"] = st.slider(
        "Mortgage Rate (%)",
        3.0, 10.0, 6.5, 0.1,
        help="Annual interest rate on your mortgage (before any fees/points). Current rates depend on credit score, down payment, and loan type. Higher rate = higher monthly payment and more total interest paid. Example: 6% on $400k loan ≈ $2,400/month. 7% ≈ $2,660/month. Check current rates at banks/credit unions."
    ) / 100
    
    # Return assumptions
    st.subheader("📈 Return Assumptions")
    
    col1, col2 = st.columns(2)
    with col1:
        params["equity_mu"] = st.slider(
            "Equity Return (%)",
            0.0, 15.0, 7.0, 0.5,
            help="Expected annual return for stock market investments (before fees). Historical S&P 500: ~10% nominal, ~7% real (after inflation). This is the 'drift' in the Monte Carlo simulation. Higher returns favor investing over buying, but come with higher volatility. International stocks, bonds, or conservative portfolios may have lower returns."
        ) / 100
        
        params["home_mu"] = st.slider(
            "Home Appreciation (%)",
            0.0, 10.0, 4.0, 0.5,
            help="Expected annual home price appreciation. Historical US average: ~3-4% nominal (matches inflation long-term). Hot markets may see 5-7%. This affects your home equity growth and final sale value. Remember: You're leveraged 5-20x with a mortgage, amplifying gains AND losses. Location matters more than national averages."
        ) / 100
    
    with col2:
        params["equity_sigma"] = st.slider(
            "Equity Volatility (%)",
            5.0, 30.0, 15.0, 1.0,
            help="Annual stock market volatility (standard deviation). Historical S&P 500: ~15-20%. Higher volatility = wider range of outcomes (both good and bad). This creates the 'bands' in the chart. Conservative portfolios: 8-12%. Aggressive/tech: 20-30%. Volatility is why the P10-P90 range is wide for stocks."
        ) / 100
        
        params["home_sigma"] = st.slider(
            "Home Volatility (%)",
            2.0, 20.0, 10.0, 1.0,
            help="Annual home price volatility. Real estate is typically less volatile than stocks (5-15% vs 15-20%). But leverage amplifies this: with 20% down, you're 5x leveraged, so 10% home volatility feels like 50% on your equity. Local markets vary: stable suburbs (5-8%), hot markets (10-15%), speculation zones (15-20%)."
        ) / 100
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        params["years"] = st.slider(
            "Time Horizon (years)", 10, 40, 30, 5,
            help="How long to simulate into the future. Longer horizons favor buying (mortgage gets paid down, rent keeps rising). Shorter horizons may favor renting (avoid transaction costs). Most mortgages are 30 years. Consider your life plans: Will you stay put or move?"
        )
        params["n_paths"] = st.slider(
            "Simulation Paths", 1000, 10000, 5000, 1000,
            help="Number of Monte Carlo simulations to run. More paths = smoother probability estimates but slower computation. 1000 = quick and rough. 5000 = good balance. 10000 = smooth and accurate. Each path is one possible future scenario."
        )
        params["seed"] = st.number_input(
            "Random Seed", 0, 10000, 42,
            help="Sets the random number generator for reproducible results. Same seed = same results every time. Change this to see different random scenarios. Default 42 is a programmer joke (Hitchhiker's Guide to the Galaxy)."
        )
        
        params["property_tax_rate"] = st.slider(
            "Property Tax Rate (%)", 0.5, 3.0, 1.5, 0.1,
            help="Annual property tax as % of home value. Varies widely by location: Texas ~2%, California ~0.75%, New Jersey ~2.5%. This is a major ongoing cost of ownership. Can be based on current value (realistic) or original price (some states). Check your county assessor website for local rates."
        ) / 100
        
        params["insurance_rate"] = st.slider(
            "Insurance Rate (%)", 0.2, 1.0, 0.4, 0.05,
            help="Annual homeowners insurance as % of home value. Varies by location and coverage: Low risk areas ~0.3%, hurricane zones ~1%+. Covers damage, liability, theft. Required by lenders. Separate from mortgage insurance (PMI/MIP). Add flood/earthquake if needed."
        ) / 100
        
        params["maintenance_rate"] = st.slider(
            "Maintenance Rate (%)", 0.5, 2.0, 1.0, 0.1,
            help="Annual maintenance/repairs as % of home value. Rule of thumb: 1% annually. New homes: 0.5-1%. Older homes: 1-2%. Includes: roof, HVAC, plumbing, painting, appliances. Renters don't pay this directly (included in rent). Major expense often overlooked by first-time buyers."
        ) / 100
        
        params["hoa_monthly"] = st.slider(
            "HOA Monthly ($)", 0, 500, 100, 25,
            help="Homeowners Association monthly fee. Covers shared amenities, landscaping, exterior maintenance. Condos: $200-500+. Townhomes: $100-300. Single family: $0-200. Can increase over time. Check HOA finances before buying - underfunded HOAs mean special assessments later."
        )
        
        params["selling_cost_rate"] = st.slider(
            "Selling Costs (%)", 0.0, 10.0, 7.0, 0.5,
            help="Transaction costs when selling the home at the end. Typically 6-10% total: Realtor commission (5-6%), closing costs (1-2%), repairs/staging (1-2%). This reduces your final proceeds. Stocks have minimal selling costs (<0.1%). High selling costs favor staying put longer."
        ) / 100
        
        params["rent_growth"] = st.slider(
            "Rent Growth Rate (%)", 0.0, 5.0, 3.0, 0.25,
            help="Annual rent increase rate. Historical average ~3-4% (slightly above inflation). Hot markets: 5-7%. Rent control areas: 1-2%. This compounds over time - 3% for 30 years means rent triples! Higher rent growth favors buying (locks in housing cost). Consider local market trends."
        ) / 100
        
        params["income_growth"] = st.slider(
            "Income Growth Rate (%)", 0.0, 5.0, 2.0, 0.25,
            help="Annual salary/income growth from raises and promotions. Typical: 2-3% (matches inflation). Early career: 4-6%. Late career: 1-2%. This increases your monthly savings budget over time, allowing larger contributions to either strategy. Critical for keeping up with rising rents."
        ) / 100
        
        params["cpi"] = st.slider(
            "CPI Inflation (%)", 0.0, 5.0, 2.5, 0.25,
            help="Consumer Price Index inflation for 'real dollar' calculations. Historical average ~2-3%. When 'Show Real Dollars' is ON, all values are adjusted to today's purchasing power. This helps you understand true wealth vs inflated numbers. Example: $1M in 30 years ≈ $400k today at 3% inflation."
        ) / 100
        
        params["equity_fee"] = st.slider(
            "Equity Fee (%)", 0.0, 2.0, 0.15, 0.05,
            help="Annual expense ratio for stock investments. Index funds: 0.03-0.20%. Active mutual funds: 0.5-1.5%. Robo-advisors: 0.25-0.50%. This drag reduces returns every year and compounds over time. Low fees are crucial for long-term investing. Vanguard/Fidelity/Schwab offer <0.1% index funds."
        ) / 100
    
    # Display options
    st.subheader("📊 Display Options")
    
    params["tax_basis"] = st.radio(
        "Property Tax Basis",
        ["current", "original"],
        format_func=lambda x: "Current Value" if x == "current" else "Original Price",
        help="How to calculate property tax over time. 'Current Value': Tax increases with home appreciation (realistic for most states). 'Original Price': Tax stays based on purchase price (like California's Prop 13). Current value means higher taxes but reflects reality. Original is conservative for planning."
    )
    
    params["show_real"] = st.checkbox(
        "Show Real Dollars",
        help="Adjusts all dollar amounts for inflation to show 'today's purchasing power'. When ON: Shows what future dollars are worth in today's terms. When OFF: Shows nominal (face value) dollars. Real dollars help you understand true wealth. Example: $2M nominal might be $1M real after 30 years of 2.5% inflation."
    )
    
    # City overlay
    show_city_overlay = st.checkbox(
        "Show City Comparison",
        help="Overlays median outcomes for Chicago and Tampa using their city-specific defaults (home prices, rent, appreciation rates). Useful for comparing how location affects the invest vs buy decision. Cities use the same return assumptions but different housing parameters."
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