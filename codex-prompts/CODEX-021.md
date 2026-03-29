# Codex Task: TASK-021 — Umowa o dzieło support

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-021.md` for full requirements.

## Summary

Add umowa o dzieło contract type: no ZUS, no health, no PPK. KUP 20% (standard) or 50% (autorskie). PIT flat 12%, non-cumulative.

## Steps

1. Add `_is_dzielo_contract()` helper to payslip model
2. In `_compute_single_payslip()`, add early return path for dzieło: zero ZUS/health/PPK, KUP 20% or 50% of gross, flat 12% PIT
3. Handle ≤200 PLN dzieło: ryczałt 12% of gross, no KUP
4. CREATE `l10n_pl_payroll/data/pl_payroll_contract_type_data.xml` with contract types (pracę, zlecenie, dzieło)
5. Register in `__manifest__.py`
6. CREATE `l10n_pl_payroll/tests/test_dzielo.py` with 7 tests
7. Update seed data: add 1 dzieło employee (Bartosz Nowicki, designer, 3000 PLN, autorskie 50%)

## Key formulas

Dzieło standard: net = gross - floor(round((gross - gross*0.20) * 0.12))
Dzieło autorskie: net = gross - floor(round((gross - gross*0.50) * 0.12))
Dzieło ≤200: net = gross - floor(round(gross * 0.12))

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/021-umowa-dzielo` from `main`. Commit with prefix `[TASK-021]`.

## Report

Write completion report to `tasks/TASK-021-report.md`.
