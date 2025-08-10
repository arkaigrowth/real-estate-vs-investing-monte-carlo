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
