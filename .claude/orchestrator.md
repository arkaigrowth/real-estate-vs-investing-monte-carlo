# Orchestrator — Master Operating Rules

## Primary Mission
Interactive Monte Carlo simulator comparing Invest vs Buy with fair cashflow model.

## Agent Coordination Protocol
1. **SimAgent** → Monte Carlo math (housing.py, mc_equity.py)
2. **MortgageAgent** → Loan calculations (mortgage.py, PMI/MIP logic)
3. **ComposerAgent** → Fair comparison logic (compose.py)
4. **ChartsAgent** → Visualization (timeseries.py)
5. **TestsAgent** → Test coverage (pytest green)
6. **DocsAgent** → Documentation sync

## Quality Gates
- Tests must pass before any merge
- Performance: 5k paths in <3 seconds
- Reproducible with fixed seed
- No negative contributions

## Communication Rules
- Small diffs preferred
- Evidence-based decisions
- Test-driven development
- Document significant changes