# Codex Task: TASK-025 — Vacation pay (wynagrodzenie za urlop)

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-025.md` for full requirements.

## Summary

Add vacation_days field to payslip. If employee has variable components (overtime, bonuses) in recent history, calculate vacation pay supplement based on 3-month average.

## Steps

1. Add `vacation_days` (Float) and `vacation_pay` (Float, readonly) fields to payslip
2. Add `_compute_vacation_pay()` method — checks 3 prior payslips for variable components, calculates hourly rate × vacation hours
3. Integrate into gross calculation in `_compute_single_payslip()`
4. Add fields to payslip form view
5. CREATE `l10n_pl_payroll/tests/test_vacation_pay.py` with 3 tests
6. Add vacation_days to 2-3 payslips in seed data

## Key rule

For fixed-salary employees with no overtime/bonuses, vacation pay = regular salary (no supplement needed). The supplement is only for variable components.

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/025-vacation-pay` from `main`. Commit with prefix `[TASK-025]`.

## Report

Write completion report to `tasks/TASK-025-report.md`.
