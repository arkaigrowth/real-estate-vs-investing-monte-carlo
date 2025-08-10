# ComposerAgent — Fair Comparison Specialist

## Responsibilities
- `compose.py`: Orchestrate fair Invest vs Buy comparison
- Enforce down-payment parity
- Calculate housing outflows
- Manage contribution flows

## Core Principles
- **Parity**: Invest gets same t0 cash as Buy spends at closing
- **Fairness**: Single budget S for both strategies
- **Contributions**: max(0, S - obligations)
- **No gaming**: Symmetric assumptions

## Key Calculations
- Closing costs = down payment + upfront MIP (if cash)
- Housing outflow = P&I + taxes + insurance + maintenance + HOA + PMI/MIP
- Invest contrib = max(0, S - rent_t)
- Buy-liquid contrib = max(0, S - housing_outflow_t)

## Invariants
- No negative contributions
- Invest starts with closing_costs
- Buy liquid starts at 0
- Terminal selling costs applied if specified

## Tax Basis Logic
- "current": Property tax on current home value
- "original": Property tax on purchase price

## Test Coverage
- Fairness baseline (no growth → similar outcomes)
- Parity enforcement
- No negative contributions
- Deterministic results