# CLAUDE.md — Project Memory
Repo: **real-estate-vs-investing-monte-carlo**

## Mission

Interactive Monte Carlo simulator comparing **Invest vs Buy** with a *fair cashflow* model:
- One monthly savings budget **S**
- **Down-payment parity** (Invest gets same t0 cash that Buy spends at closing)
- **FHA** default with finance / pay-cash upfront MIP toggle; or **Conventional** w/ PMI + drop threshold
- **Tax base** toggle: current value vs original price
- **Real dollars** display (CPI deflation)
- **Baseline Snapshot (A/B)** overlay (median dotted lines + delta metrics)
- City overlay **Chicago vs Tampa** (median-only)
- **Educational tooltips** on all sliders with examples, typical values, and trade-offs

## Architecture

- `app.py` — Streamlit UI (sidebar controls, tooltips, A/B snapshot, city overlay)
- `charts/timeseries.py` — Plotly builders (P10–P90 bands, medians, ticks, legends)
- `core/`
  - `compose.py` — fair Invest vs Buy (parity, contributions, PMI/MIP, tax base)
  - `mc_equity.py` — equity GBM (monthly) + variable contributions + fee drag
  - `housing.py` — home value GBM (monthly)
  - `mortgage.py` — P&I + amortization helpers
  - `presets.py` — city + global defaults
  - `stats.py` — percentiles, probability, drawdown
- `tests/` — amortization, fairness, contributions
- `.claude/` — orchestrator & role prompts
- `context/` — requirements, design principles, acceptance criteria
- `commands/` — reusable prompts (code-review, perf-check, doc-review)
- `.github/workflows/ci.yml` — PR test runner (Stage 2)

## Run / Test
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
streamlit run app.py
````

## Acceptance Criteria (MVP)

* UI sliders/toggles work; comprehensive educational tooltips present.
* P10/P50/P90 bands for both strategies; x-axis = yearly majors + monthly minor grid.
* Probability card + terminal P50 metrics update with inputs.
* FHA↔Conventional; finance vs pay-cash MIP; tax-base toggles behave as documented.
* Baseline Snapshot overlays **dotted P50** for baseline + terminal deltas.
* Same seed → same results.
* Default run (5k paths, 30y) renders within a few seconds on a laptop.
* All tooltips provide educational value with real-world context and examples.

## Prompts (Claude Code)

**Plan (before coding):**

> Think hardest. Write a minimal plan for the change. List files to edit, functions to add/update, and 2–3 tests (names + 1-line purpose). Avoid unnecessary scaffolding.

**Execute (small diffs):**

> Implement step 1 only as a minimal diff. After writing, run tests and stop. If tests fail, propose the smallest fix and apply it. Do not add new files unless explicitly requested.

**Review (“my developer”):**

> My developer made this change. High-level + specific critique: what should have been edited instead of added? Any edge cases, perf risks, or simpler designs?

## Roles

* **SimAgent** (mc\_equity & housing math), **MortgageAgent** (PMI/MIP, amortization),
  **ComposerAgent** (parity, contributions), **ChartsAgent** (bands, ticks),
  **TestsAgent**, **DocsAgent**

## Context Docs

See `context/requirements.md`, `context/design-principles.md`, `context/acceptance-criteria.md`.
