# bootstrap_stage12.py
from pathlib import Path

ROOT = Path(".").resolve()

def w(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("[write]", path)

# --- Stage 1: CLAUDE.md + subfolder specs + context + commands ---
w(ROOT / "CLAUDE.md", """
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
```
"""
)




from pathlib import Path

ROOT = Path(".").resolve()

def w(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("[write]", path)

# --- Stage 1: CLAUDE.md + subfolder specs + context + commands ---
w(ROOT / "CLAUDE.md", """
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

* UI sliders/toggles work; tooltips present.
* P10/P50/P90 bands for both strategies; x-axis = yearly majors + monthly minor grid.
* Probability card + terminal P50 metrics update with inputs.
* FHA↔Conventional; finance vs pay-cash MIP; tax-base toggles behave as documented.
* Baseline Snapshot overlays **dotted P50** for baseline + terminal deltas.
* Same seed → same results.
* Default run (5k paths, 30y) renders within a few seconds on a laptop.

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
""")

w(ROOT / "core" / "CLAUDE.md", """

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
  """)

w(ROOT / "charts" / "CLAUDE.md", """

# CLAUDE.md — /charts

* Plotly net-worth bands & medians
* X-axis: yearly majors + monthly minor grid
* Legends map 1:1 to visible elements
* Invest=blue, Buy=orange, rent overlays=gray dashed
* Baseline Snapshot medians = dotted lines
* `hovermode="x unified"`, minimal clutter, Nominal/Real y-label switch
  """)

w(ROOT / "context" / "requirements.md", """

# Requirements

* Single budget **S**; enforce t0 parity (Invest gets Buy closing spend).
* Invest contrib: `max(0, S − rent_t)`; Buy-liquid contrib: `max(0, S − housing_outflow_t)`.
* Housing outflow: P\&I, taxes, maintenance, insurance, HOA, PMI/MIP.
* Toggles: FHA vs Conventional, finance vs pay-cash upfront MIP, tax base current vs original, real-dollars display.
* Outputs: P10/P50/P90 bands; P(Invest>Buy) at T; city overlay medians; Baseline Snapshot overlay + deltas.
* Perf: default (5k paths, 30y) in a few seconds; fixed seed reproducible.
  """)

w(ROOT / "context" / "design-principles.md", """

# Design Principles

* Clarity > flash; fairness first; explicit uncertainty; sane defaults.
* Deterministic seeds; rent variance only if user opts in.
* Minimal code paths; avoid premature abstractions.
  """)

w(ROOT / "context" / "acceptance-criteria.md", """

# Acceptance Criteria

Functional

* Sidebar controls update bands & metrics; toggles behave as documented.
* Baseline Snapshot shows dotted medians + terminal deltas.
* City overlay shows Chicago/Tampa medians.

Numerical

* Tests pass; reproducible with fixed seed; no negative contributions.

UX

* Yearly majors + monthly minor grid; unambiguous legends; Nominal/Real y-label switch.
  """)

w(ROOT / "commands" / "code-review\.md", """

# Command: Code Review (Claude prompt)

Checklist: acceptance criteria; edit-vs-add; PMI removal & liquidate edge cases; perf issues.
Output: summary, file\:line issues, minimal-diff suggestions.
""")

w(ROOT / "commands" / "perf-check.md", """

# Command: Performance Check (Claude prompt)

Checklist: no loops over paths/months in hot paths; reuse arrays; seeded RNG; minimize temporaries.
Output: risks + locations; minimal refactor plan.
""")

w(ROOT / "commands" / "doc-review\.md", """

# Command: Doc Review (Claude prompt)

Checklist: README/CLAUDE/context reflect behavior; tooltips match UI; changelog snippet if needed.
Output: proposed doc edits (file + snippet).
""")

w(ROOT / "docs" / "claude-code-best-practices-summary.md", """

# Claude Code Best Practices — Actionable Summary

* Explore → Plan → Execute. Use /resume; keep context in repo (CLAUDE.md + /context).
* Role prompts for focus; small diffs with tests.
* Parallel work: git worktrees + separate PRs; CI runs tests.
* Avoid risky watch-mode; run tests frequently.
  """)

w(ROOT / "CLAUDE.md.template", """

# CLAUDE.md (template)

\[Copy this to CLAUDE.md if you want to regenerate the project memory.]
""")

# --- Stage 2: CI + Worktrees ---

w(ROOT / ".github" / "workflows" / "ci.yml", """
name: CI
on:
pull\_request:
push:
branches: \[ main, master ]
workflow\_dispatch:
jobs:
test:
runs-on: ubuntu-latest
steps:
\- uses: actions/checkout\@v4
\- uses: actions/setup-python\@v5
with:
python-version: "3.11"
\- name: Upgrade pip
run: python -m pip install --upgrade pip
\- name: Install deps
run: pip install -r requirements.txt
\- name: Run tests
run: pytest -q
""")

w(ROOT / "ops" / "worktrees.md", """

# Git Worktrees — Parallel Agent Work

## Create

git fetch origin
git worktree add ../feat-snapshot-overlay -b feat/snapshot-overlay origin/main

## List

git worktree list

## Remove (after merge)

git worktree remove ../feat-snapshot-overlay

## Recommended

* One major change per worktree → one PR → CI runs → merge → remove
  """)

# .gitignore (append lines if missing)

gi = ROOT / ".gitignore"
existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
extras = [".venv/", "**pycache**/", "*.pyc", ".streamlit/", ".pytest_cache/", ".DS_Store",
".github/", "ops/", "commands/", "context/"]
lines = set([l for l in existing.splitlines() if l.strip()])
lines.update(extras)
gi.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")
print("[update]", gi)

print("\nDone. Stage 1 + Stage 2 files written.")
print("Next:")
print("  git add -A && git commit -m 'Add Stage 1+2 (CLAUDE.md, context, commands, CI, worktrees)'")

