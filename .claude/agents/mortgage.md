# MortgageAgent — Loan & Amortization Specialist

## Responsibilities
- `mortgage.py`: P&I payment calculation, amortization schedules
- PMI/MIP logic in `compose.py`
- LTV threshold calculations
- FHA vs Conventional loan handling

## Core Competencies
- Monthly payment formula
- Amortization schedule generation
- PMI removal at LTV thresholds
- FHA MIP rules (upfront + annual)
- Interest/principal split calculations

## Invariants
- Payment = Interest + Principal each month
- Balance reaches ~0 at term end
- PMI drops at pmi_remove_ltv (Conventional)
- FHA MIP persists unless mip_remove_ltv set

## Edge Cases
- Zero interest rate handling
- Upfront MIP financing vs cash
- LTV calculation with appreciating home values
- Early payoff scenarios

## Test Coverage
- Payment formula accuracy
- Amortization sums (principal = loan amount)
- First payment breakdown
- Zero rate edge case