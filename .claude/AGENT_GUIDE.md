# Agent System Guide

## Overview
The "agents" aren't Python classes—they're **prompted roles**. You tell Claude Code which hat to wear, and it edits files in your current workspace.

## Agent Structure in Repo

* `.claude/orchestrator.md` → Master operating rules
* `.claude/agents/`
  * `sim.md` (SimAgent: equity/home GBM & variable contribs)
  * `mortgage.md` (MortgageAgent: amortization, FHA/PMI, LTV thresholds)
  * `composer.md` (ComposerAgent: fairness, parity, cashflows)
  * `charts.md` (ChartsAgent: Plotly bands, ticks, legends)
  * `tests.md` (TestsAgent: keep pytest green)
  * `docs.md` (DocsAgent: keep README/CLAUDE/context current)
* `CLAUDE.md` (root) → Roles + acceptance criteria + prompts
* `commands/` → Reusable review prompts

## Three Practical Flows

### Flow A — Single Chat (Simplest)

1. **Kickoff**:
```
Open CLAUDE.md and follow it. Use context/acceptance-criteria.md as the target.
Plan → Execute → Review; small diffs; keep tests green.
```

2. **Invoke roles with scoped asks**:
```
Act as MortgageAgent: open core/mortgage.py, verify PMI removal at pmi_remove_ltv, 
FHA MIP life-of-loan. Plan first (files+tests), then minimal diff. Run pytest -q.
```

3. **For reviews**:
```
Run the checklist in commands/code-review.md against the last diff.
```

### Flow B — Multi-Tab Agents

* Open one chat per role in parallel
* Paste corresponding file from `.claude/agents/<role>.md`
* Each tab touches specific files with small diffs
* Merge via PRs

### Flow C — True Parallel Work (Git Worktrees)

```bash
# Create separate worktrees for parallel work
git worktree add ../feat-mortgage -b feat/mortgage origin/main
git worktree add ../feat-charts -b feat/charts origin/main

# Point each agent at their worktree
# Open PRs per worktree
# CI runs tests on each
```

## Copy-Paste Starters

### Initial Setup
```
Open CLAUDE.md and follow it. Use context/acceptance-criteria.md as the target.
Plan → Execute → Review; small diffs; keep tests green.

Terminal:
python -m venv .venv && source .venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt && pytest -q && streamlit run app.py
```

### Role-Scoped Request
```
Act as MortgageAgent.
Read .claude/agents/mortgage.md. Plan first: list exact edits + 2 tiny tests.
Task: verify PMI drops at pmi_remove_ltv and FHA MIP stays unless mip_remove_ltv is set.
Apply smallest safe diff, run pytest -q, report status. Don't echo full files.
```

### Charts Review
```
Use commands/code-review.md to review latest changes in charts/timeseries.py 
against context/acceptance-criteria.md.
Output: 3-bullet summary, file:line issues, minimal diffs.
```

### Performance Check
```
Act as SimAgent. Use commands/perf-check.md on core/mc_equity.py and core/compose.py.
Flag loops over paths/months, big temporaries, avoidable copies. 
Propose minimal refactors.
```

### Objective Critique
```
My developer just implemented X. Use commands/code-review.md to critique:
what should have been edited rather than added, edge cases, simpler designs.
```

## Pro Tips

1. **Always say**: "Plan first (files + tests) → minimal diff → run pytest -q"
2. **Keep asks narrow**: One role, one file/folder
3. **Reference specs**: `CLAUDE.md`, `core/CLAUDE.md`, `context/*`
4. **Run command reviews**: After patches, before next change
5. **For parallel edits**: Worktrees + PRs > one-tab chaos

## Quick Reference

| Agent | Responsibility | Key Files |
|-------|---------------|-----------|
| SimAgent | Monte Carlo math | mc_equity.py, housing.py, stats.py |
| MortgageAgent | Loan calculations | mortgage.py, PMI/MIP logic |
| ComposerAgent | Fair comparison | compose.py |
| ChartsAgent | Visualization | timeseries.py |
| TestsAgent | Test coverage | tests/*.py |
| DocsAgent | Documentation | CLAUDE.md, context/* |