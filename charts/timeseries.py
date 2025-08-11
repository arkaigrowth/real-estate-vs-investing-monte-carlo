"""Plotly chart builders for net worth bands and medians."""

import plotly.graph_objects as go
import numpy as np
from core.stats import compute_percentiles

def create_net_worth_chart(invest_paths, buy_paths, params, baseline_data=None, city_data=None):
    """Create Plotly figure with P10/P50/P90 bands for both strategies.
    
    Args:
        invest_paths: (n_paths, n_months+1) array
        buy_paths: (n_paths, n_months+1) array
        params: Dict with simulation parameters
        baseline_data: Optional dict with baseline percentiles
        city_data: Optional dict with city comparison data
    
    Returns:
        Plotly figure object
    """
    n_months = params["years"] * 12
    months = np.arange(n_months + 1)
    years = months / 12
    
    # Apply CPI deflation if showing real dollars
    deflator = 1.0
    if params.get("show_real", False):
        cpi = params.get("cpi", 0.025)
        deflator = (1 + cpi) ** (-years)
    
    # Compute percentiles
    invest_pcts = compute_percentiles(invest_paths * deflator)
    buy_pcts = compute_percentiles(buy_paths * deflator)
    
    # Create figure
    fig = go.Figure()
    
    # Dark mode friendly colors
    # Invest: Cyan/Teal spectrum (pops on dark background)
    # Buy: Coral/Salmon spectrum (warm contrast)
    
    # Add Invest bands (P10-P90 fill, then P50 line)
    fig.add_trace(go.Scatter(
        x=years, y=invest_pcts[90],
        name="Invest P90",
        line=dict(color="rgba(78, 205, 196, 0)", width=0),  # Teal
        showlegend=False,
        hovertemplate="P90 (Lucky): $%{y:,.0f}<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=invest_pcts[10],
        name="Invest P10-P90 Range",
        line=dict(color="rgba(78, 205, 196, 0)", width=0),
        fill="tonexty",
        fillcolor="rgba(78, 205, 196, 0.25)",  # Semi-transparent teal
        hovertemplate="P10 (Unlucky): $%{y:,.0f}<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=invest_pcts[50],
        name="Invest P50 (Median)",
        line=dict(color="#4ECDC4", width=3),  # Bright teal, thicker for visibility
        hovertemplate="P50 (Typical): $%{y:,.0f}<extra></extra>"
    ))
    
    # Add Buy bands (P10-P90 fill, then P50 line)
    fig.add_trace(go.Scatter(
        x=years, y=buy_pcts[90],
        name="Buy P90",
        line=dict(color="rgba(255, 107, 107, 0)", width=0),  # Coral
        showlegend=False,
        hovertemplate="P90 (Lucky): $%{y:,.0f}<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=buy_pcts[10],
        name="Buy P10-P90 Range",
        line=dict(color="rgba(255, 107, 107, 0)", width=0),
        fill="tonexty",
        fillcolor="rgba(255, 107, 107, 0.25)",  # Semi-transparent coral
        hovertemplate="P10 (Unlucky): $%{y:,.0f}<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=buy_pcts[50],
        name="Buy P50 (Median)",
        line=dict(color="#FF6B6B", width=3),  # Bright coral, thicker for visibility
        hovertemplate="P50 (Typical): $%{y:,.0f}<extra></extra>"
    ))
    
    # Add baseline snapshot if provided
    if baseline_data:
        fig.add_trace(go.Scatter(
            x=years, y=baseline_data["invest_p50"] * deflator,
            name="Baseline Invest P50",
            line=dict(color="#4ECDC4", width=2, dash="dot"),  # Teal for dark mode
            hovertemplate="Baseline: $%{y:,.0f}<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=years, y=baseline_data["buy_p50"] * deflator,
            name="Baseline Buy P50",
            line=dict(color="#FF6B6B", width=2, dash="dot"),  # Coral for dark mode
            hovertemplate="Baseline: $%{y:,.0f}<extra></extra>"
        ))
    
    # Add city overlay if provided
    if city_data:
        for city_name, city_paths in city_data.items():
            city_invest_p50 = np.percentile(city_paths["invest"] * deflator, 50, axis=0)
            city_buy_p50 = np.percentile(city_paths["buy"] * deflator, 50, axis=0)
            
            fig.add_trace(go.Scatter(
                x=years, y=city_invest_p50,
                name=f"{city_name} Invest P50",
                line=dict(width=1, dash="dash"),
                hovertemplate=f"{city_name}: $%{{y:,.0f}}<extra></extra>"
            ))
            
            fig.add_trace(go.Scatter(
                x=years, y=city_buy_p50,
                name=f"{city_name} Buy P50",
                line=dict(width=1, dash="dash"),
                hovertemplate=f"{city_name}: $%{{y:,.0f}}<extra></extra>"
            ))
    
    # Update layout
    y_label = "Real Net Worth ($)" if params.get("show_real", False) else "Nominal Net Worth ($)"
    
    fig.update_layout(
        title="Invest vs Buy: Net Worth Over Time",
        xaxis_title="Years",
        yaxis_title=y_label,
        hovermode="x unified",
        height=600,
        template="plotly_dark",  # Dark mode template
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Add yearly major gridlines and monthly minor ticks
    fig.update_xaxes(
        dtick=1,  # Major tick every year
        minor=dict(dtick=1/12, showgrid=False),  # Minor tick every month
        gridcolor="rgba(128, 128, 128, 0.2)",  # Subtle grid for dark mode
        showgrid=True
    )
    
    fig.update_yaxes(
        gridcolor="rgba(128, 128, 128, 0.2)",  # Subtle grid for dark mode
        tickformat="$,.0f"
    )
    
    return fig