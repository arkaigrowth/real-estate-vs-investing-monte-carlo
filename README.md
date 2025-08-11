# real-estate-vs-investing-monte-carlo

Interactive Monte Carlo simulator to compare **investing in a stock portfolio while renting** vs **buying a home with a mortgage**, with a **fair-cashflow** model and city presets (Chicago, Tampa).

## Highlights

* **Fairness model**: one monthly savings budget **S** for both paths.
  * Invest contrib = `max(0, S − rent_t)`
  * Buy-liquid contrib = `max(0, S − housing_outflow_t)`
  * **Down-payment parity**: Invest starts with the same cash the Buy path spends at closing.
* **Loan insurance toggles**: **FHA** (annual MIP + upfront MIP, finance or pay-cash) vs **Conventional** (PMI with drop threshold).
* **Tax base toggle**: property tax & maintenance on **current value** (realistic) or **original price** (conservative).
* **Uncertainty**: GBM for equities & home appreciation, P10/P50/P90 bands, probability that Invest beats Buy at horizon.
* **City overlay**: Chicago vs Tampa, median lines.
* **Baseline Snapshot (A/B)**: freeze Scenario A, tweak inputs → chart overlays **dotted baseline medians** + shows terminal P50 deltas.
* **Deterministic**: RNG seed for reproducible runs.
* Built with **Streamlit + NumPy + Plotly**.

---

## Quickstart

```bash
# 0) cd into the project root
cd real-estate-vs-investing-monte-carlo

# 1) (Recommended) Create a virtual env
python -m venv .venv
# mac/linux:
source .venv/bin/activate
# windows (powershell):
# .\.venv\Scripts\Activate.ps1

# 2) Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3) Run tests
pytest -q

# 4) Launch the app
streamlit run app.py
```

Open the URL Streamlit prints (usually [http://localhost:8501](http://localhost:8501)).

---

## Using Claude Code (Windsurf)

1. Open `.claude/orchestrator.md` and paste it as your first Claude message.
2. Tell it to **follow `CLAUDE.md` (root)** and use `context/acceptance-criteria.md` as a pass/fail target.
3. Work in the **Plan → Execute → Review** loop with **small diffs** and tests after each change.
4. Role prompts live in `.claude/agents/` (Sim/Mortgage/Composer/Charts/Tests/Docs). Call them like:
   * "**Act as MortgageAgent**: plan edits + 2 tiny tests, then minimal patch, run `pytest -q`."
5. For parallel "agents," use **git worktrees** (see `ops/worktrees.md`) and open separate Claude tabs per worktree.

---

## UI Guide (Sidebar)

* **City preset**: loads defaults (taxes, insurance, appreciation, rent).
* **RNG seed**: reproducibility.
* **Horizon & Paths**: years and Monte Carlo path count.
* **Budget (Fairness)**:
  * **Use monthly savings model** (recommended): invest only what's left after housing costs.
  * **Monthly savings S**: your average monthly saving before housing.
  * **Down-payment parity**: ON to avoid one side starting richer.
* **Invest (Stocks)**: annual return μ, volatility σ, fee drag, (manual contrib if fairness model OFF).
* **Rent**:
  * **Primary rent**: drives Invest contributions (grows at 5%/yr by default).
  * **Overlay rents**: comma list, plotted as dashed context lines (don't affect contributions).
  * **Rent growth (mean/std)**: optional variance.
* **Home (Buy)**: price, down %, rate, term, tax rate, insurance/HOA, maintenance rate, appreciation μ/σ.
* **Loan Insurance**:
  * **FHA**: annual MIP, upfront MIP %, **finance upfront MIP** (checkbox).
  * **Conventional**: PMI annual rate & **PMI removal LTV** (e.g., 0.80).
* **Other toggles**:
  * **Tax/Maintenance base**: current vs original.
  * **Closing/Selling costs** and **Liquidate at horizon** (apply selling costs at the end).
  * **Real dollars**: CPI deflation for charts (set CPI in sidebar).
* **Snapshots**:
  * **Save baseline**: freeze current scenario; overlays dotted baseline medians on the chart.
  * **Clear baseline**: remove overlay.

---

## Reading the Chart

* **Invest vs Buy**: P10/P50/P90 bands for net worth over time.
* **Rent overlays**: dashed lines compounding at 5%/yr for context.
* **Baseline**: if saved, **dotted median** lines show Scenario A vs current.
* **KPIs**:
  * `P(Invest > Buy at horizon)`
  * `Terminal P50 (Invest / Buy)`
  * Baseline comparison (deltas vs baseline) in an expander.

---

## City Defaults & Presets

* Edit `core/presets.py`.
* Example defaults (you can adjust):
  * **Chicago**: primary rent ≈ **\$2,200**, higher tax rate;
  * **Tampa**: primary rent ≈ **\$2,000** (adjust to your local).
* Appreciation μ/σ, property tax rates, insurance, HOA, maintenance are set per city.

---

## Architecture

```text
app.py                     # Streamlit UI, tooltips, toggles, Baseline Snapshot, city overlay
charts/
  timeseries.py            # Plotly bands, medians, yearly majors + monthly minor grid
core/
  compose.py               # Fairness: S-budget, parity; builds contributions & buy/invest paths
  mc_equity.py             # Equity GBM w/ variable contributions + fee drag
  housing.py               # Home value GBM
  mortgage.py              # Amortization + payment helpers; PMI/MIP logic at monthly level
  presets.py               # City and global defaults
  stats.py                 # Percentiles, P(A>B), drawdown helpers
tests/
  ...                      # pytest sanity: amortization, variable contribs, fairness baseline
.claude/
  orchestrator.md, agents/ # Claude Code operating rules + role prompts
context/
  requirements.md          # Scope & constraints
  design-principles.md     # UX & modeling principles
  acceptance-criteria.md   # Pass/fail checks
commands/
  code-review.md           # Reusable prompt for objective review
  perf-check.md            # Hot-path & memory checklist
  doc-review.md            # Doc alignment checklist
.github/workflows/
  ci.yml                   # PR test runner (pytest) on GitHub
ops/
  worktrees.md             # Git worktrees playbook for parallel agent work
docs/
  claude-code-best-practices-summary.md
```

---

## Testing

```bash
pytest -q
```

Covers:

* Mortgage payment & amortization sums
* Equity path with **variable contributions** (μ=σ=0 → linear sum)
* Fairness baseline sanity (no growth/costs → Invest P50 ≈ Buy P50)

---

## Baseline Snapshot (A/B) — How-To

1. Set your parameters and **click "Save baseline"**.
2. Change any inputs; the main chart overlays **Baseline Invest/Buy (P50)** as **dotted lines**.
3. Open **"Baseline comparison"** to see **terminal P50 deltas** vs baseline.

---

## CI (Stage 2)

* `.github/workflows/ci.yml` runs `pytest -q` on PRs and pushes to `main`/`master`.
* If your default branch is different, update the `branches:` list.

---

## Parallel Agent Work with Worktrees (Stage 2)

Use `ops/worktrees.md`:

```bash
git fetch origin
git worktree add ../feat-mortgage -b feat/mortgage origin/main
# open the new folder in a separate IDE/Claude tab
# ... work, commit, push, PR ...
git worktree remove ../feat-mortgage   # after merge
```

---

## Troubleshooting

* **"requirements.txt not found"** → you're probably in the wrong folder.

  ```bash
  pwd && ls -la && find . -maxdepth 3 -iname "requirements.txt"
  cd real-estate-vs-investing-monte-carlo
  ```

* **Port already in use** → `streamlit run` picks a new port automatically or stop the previous run.
* **Plotly/Streamlit not found** → ensure virtualenv is **activated** and install deps.
* **Slow runs** → lower `n_paths`; shorten horizon; keep CPI/variance reasonable.
* **Weird results** → check seed, inputs, and whether **Real dollars** is ON (deflates values).

---

## License

MIT

---

## Acknowledgments

Built with Streamlit, Plotly, and NumPy. Developed using Claude Code with agent-based architecture.