# Codex Task: TASK-019 — Part-time employment (niepełny etat)

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-019.md` for full requirements.

## Summary

Part-time employees need proportional KUP standard and minimum wage validation.

## Steps

1. In `pl_payroll_payslip.py`, add `_get_etat_fraction()` method — computes fraction from `contract.resource_calendar_id.hours_per_week / company.resource_calendar_id.hours_per_week`. Returns Decimal("1") if no calendar set.
2. Modify `_compute_kup_amount()`: for `kup_type == "standard"`, multiply KUP by etat fraction. Autorskie and standard_20 are NOT proportional.
3. Add MINIMUM_WAGE parameters to `l10n_pl_payroll/data/pl_payroll_parameter_data.xml`: 4666 (2025), 4806 (2026)
4. Add `below_minimum_wage` computed Boolean field to payslip. Add `etat_fraction` computed Float field.
5. Add warning display in payslip form view for below_minimum_wage.
6. CREATE `l10n_pl_payroll/tests/test_part_time.py` with 5 tests (see TASK-019.md)
7. Update `scripts/seed_realistic_data.py`: make Natalia Ivanchuk 0.5 etat and Yuliia Kravchuk 0.75 etat (create resource.calendar records)

## Key rule

Only KUP standard 250 PLN is proportional to etat. Autorskie KUP and KUP 20% are NOT proportional (they're already based on actual income).

## Branch

CRITICAL: First run `git fetch origin main && git checkout main && git pull origin main` to ensure you have the latest code. THEN create your branch.

Create branch `task/019-part-time` from `main`. Commit with prefix `[TASK-019]`.

## Report

Write completion report to `tasks/TASK-019-report.md`.
