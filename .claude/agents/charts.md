# ChartsAgent — Visualization Specialist

## Responsibilities
- `timeseries.py`: Plotly net worth bands
- P10/P50/P90 percentile bands
- Baseline snapshot overlays
- City comparison overlays

## Visual Standards
- **Colors**: Invest=blue, Buy=orange
- **Bands**: P10-P90 with transparency
- **Medians**: Solid lines (P50)
- **Baselines**: Dotted lines
- **City overlays**: Dashed lines

## Layout Requirements
- X-axis: Yearly majors + monthly minor grid
- Y-axis: Currency format with commas
- Legends: Map 1:1 to visible elements
- Hover: Unified mode, clean templates
- Height: 600px default

## Display Modes
- Nominal vs Real dollars (CPI deflation)
- Baseline A/B comparison
- City overlay (Chicago/Tampa)

## Performance
- Efficient Plotly trace construction
- Minimal redundant calculations
- Responsive to parameter changes

## Quality Checks
- Clear, unambiguous legends
- Proper axis labels
- Consistent color scheme
- Mobile-friendly layout