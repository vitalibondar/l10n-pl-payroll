# Codex Task: TASK-024 — ZUS DRA monthly declaration

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-024.md` for full requirements.

## Summary

Create ZUS DRA monthly summary model (with per-employee lines), generation wizard, and views.

## Steps

1. CREATE `l10n_pl_payroll/models/pl_payroll_zus_dra.py` — DRA header model + DRA Line model (per employee)
2. CREATE `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard.py` — wizard takes year+month, aggregates payslips
3. CREATE views for DRA (list with lines), wizard form
4. Add menu: Polish Payroll → Raporty → ZUS DRA
5. Add security
6. CREATE `l10n_pl_payroll/tests/test_zus_dra.py` with 4 tests
7. Register all in __init__.py and __manifest__.py

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/024-zus-dra` from `main`. Commit with prefix `[TASK-024]`.

## Report

Write completion report to `tasks/TASK-024-report.md`.
