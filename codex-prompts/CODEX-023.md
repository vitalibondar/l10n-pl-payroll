# Codex Task: TASK-023 — PIT-11 annual declaration

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-023.md` for full requirements.

## Summary

Create PIT-11 data model, generation wizard, and printable report. PIT-11 = annual income summary per employee.

## Steps

1. CREATE `l10n_pl_payroll/models/pl_payroll_pit11.py` — model with aggregated yearly fields
2. CREATE `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard.py` — wizard that aggregates payslips by employee per year
3. CREATE views for both (list, form, wizard form)
4. CREATE QWeb report template for printable PDF
5. Add security (ir.model.access.csv)
6. Register everything in __init__.py and __manifest__.py
7. CREATE `l10n_pl_payroll/tests/test_pit11.py` with 4 tests

## Key gotcha

Health deductible in PIT-11 = 7.75% of health_basis (NOT the full 9% paid). The 1.25% difference is non-deductible.

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/023-pit11` from `main`. Commit with prefix `[TASK-023]`.

## Report

Write completion report to `tasks/TASK-023-report.md`.
