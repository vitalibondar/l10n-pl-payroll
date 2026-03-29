# Codex Task: TASK-022 — Minimum health contribution basis

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-022.md` for full requirements.

## Summary

Health contribution basis cannot be lower than (proportional minimum wage - ZUS). Add floor.

## Steps

1. Add `_get_minimum_health_basis()` method to payslip model
2. In `_compute_single_payslip()`, after calculating `health_basis`, apply floor: `health_basis = max(health_basis, min_health_basis)`
3. Skip floor for dzieło and student-exempt contracts
4. CREATE `l10n_pl_payroll/tests/test_health_minimum.py` with 4 tests

## Depends on

TASK-019 provides MINIMUM_WAGE parameter and `_get_etat_fraction()`. If not merged, add them locally.

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/022-health-min-basis` from `main`. Commit with prefix `[TASK-022]`.

## Report

Write completion report to `tasks/TASK-022-report.md`.
