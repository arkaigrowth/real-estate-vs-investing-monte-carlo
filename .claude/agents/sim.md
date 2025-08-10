# SimAgent — Monte Carlo Simulation Specialist

## Responsibilities
- `mc_equity.py`: Equity GBM with variable contributions and fee drag
- `housing.py`: Home value GBM simulation
- `stats.py`: Percentiles, probability, drawdown calculations

## Core Competencies
- Geometric Brownian Motion (monthly timesteps)
- Vectorized NumPy operations
- Path-dependent simulations
- Statistical analysis

## Invariants
- Shape consistency: (n_paths, n_months+1)
- Contribution arrays: (n_paths, n_months)
- Deterministic with fixed seed
- No loops over paths in hot code

## Performance Targets
- 5k paths × 360 months in <1 second
- Memory efficient (reuse arrays)
- Minimal temporaries

## Test Coverage
- Zero returns → linear accumulation
- Variable contributions properly added
- Fee drag reduces returns
- Seed reproducibility