# Codex Task: TASK-020 — Sick leave pay (zwolnienie chorobowe)

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-020.md` for full requirements.

## Summary

Employer pays 80% (or 100% for pregnancy/accident) of average salary for first 33 sick days/year. Sick days: no ZUS, yes health, yes PIT.

## Steps

1. Add fields to payslip: `sick_days` (Integer), `sick_days_100` (Integer), `sick_leave_amount` (Float), `sick_leave_basis` (Float), `working_days_in_month` (Integer)
2. Add `_compute_sick_leave_basis()` — average of (gross - ZUS_EE) from last 12 confirmed payslips
3. Add `_compute_sick_leave()` — calculates sick pay and reduces gross proportionally
4. Integrate into `_compute_single_payslip()`: ZUS on adjusted_gross only (not sick portion), health on (adjusted_gross - ZUS + sick_amount)
5. Add `ytd_sick_days` computed field for tracking 33-day limit
6. Add sick leave section to payslip form view (after gross, before ZUS)
7. CREATE `l10n_pl_payroll/tests/test_sick_leave.py` with 6 tests (see TASK-020.md)
8. Update seed data: add sick days to 3-4 historical payslips

## Key rules

- Sick days: NO ZUS (neither EE nor ER)
- Sick days: YES health insurance, YES PIT
- Sick days: NO PPK
- Basis = average of (gross - 13.71% ZUS) from last 12 months
- Daily rate = basis / 30

## Depends on

TASK-019 provides `_get_etat_fraction()`. If not merged yet, add it locally.

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/020-sick-leave` from `main`. Commit with prefix `[TASK-020]`.

## Report

Write completion report to `tasks/TASK-020-report.md`.
