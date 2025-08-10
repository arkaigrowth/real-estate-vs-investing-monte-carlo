# CLAUDE.md — /core

## Responsibilities

* `compose.py`: parity, contributions, housing outflows, equity, buy\_paths
* `mc_equity.py`: equity GBM (monthly), per-path variable contributions, fee drag
* `housing.py`: home value GBM (monthly)
* `mortgage.py`: payment + amortization arrays
* `stats.py`: percentiles (axis=0), P(A>B), max drawdown
* `presets.py`: city defaults (Chicago, Tampa) + globals

## Invariants

* Path shapes: (n\_paths, n\_months+1); contrib arrays: (n\_paths, n\_months)
* No negative contributions
* PMI drops at `pmi_remove_ltv` if set; FHA MIP persists unless `mip_remove_ltv`
* Selling costs only at horizon when toggled

## Tests

* Amortization sums; payment formula == schedule\[0]
* mc\_equity: mu=sigma=0 + variable contrib → linear sum
* compose: fairness baseline (no growth/costs) → Invest P50 == Buy P50

## Perf

* Vectorized NumPy; minimize temporaries
