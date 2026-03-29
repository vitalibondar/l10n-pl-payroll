# Codex Task: TASK-026 — Batch payslip generation wizard

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-026.md` for full requirements.

## Summary

Wizard to generate payslips for all employees (or selected departments) for a given month in one click. Also add batch confirm server action.

## Steps

1. CREATE `l10n_pl_payroll/wizard/pl_payroll_batch_wizard.py` — takes date_from/date_to, optional department filter, finds active contracts, creates payslips (skips if already exists), optionally auto-computes
2. CREATE wizard view XML with form and menu item
3. Add batch confirm server action to payslip list view (calls action_confirm on selected records)
4. Add security for wizard model
5. CREATE `l10n_pl_payroll/tests/test_batch_wizard.py` with 5 tests
6. Register all in __init__.py and __manifest__.py

## Key behavior

- Idempotent: if payslip exists for employee+month → skip
- Auto-compute option: creates + computes in one go
- Department filter: empty = all departments

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/026-batch-payslip` from `main`. Commit with prefix `[TASK-026]`.

## Report

Write completion report to `tasks/TASK-026-report.md`.
