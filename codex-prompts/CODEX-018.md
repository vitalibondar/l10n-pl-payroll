# Codex Task: TASK-018 — Student on zlecenie: ZUS exemption

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-018.md` for full requirements.

## Summary

Students under 26 on umowa zlecenie pay ZERO ZUS (both employee and employer side). Implement this.

## Steps

1. CREATE `l10n_pl_payroll/models/hr_employee.py` — inherit `hr.employee`, add `is_student` Boolean field
2. Add `hr_employee` import to `l10n_pl_payroll/models/__init__.py`
3. In `pl_payroll_payslip.py`, add method `_is_student_zlecenie_exempt()` — returns True if mandate contract + is_student + age < 26 (use `self.employee_id.birthday`)
4. In `_compute_single_payslip()`, wrap ZUS calculation (both EE and ER) with exemption check: if student zlecenie exempt → all ZUS fields = 0, health = 0
5. CREATE `l10n_pl_payroll/views/pl_payroll_employee_views.xml` — add `is_student` checkbox to employee form via xpath on `hr.view_employee_form`
6. Add the view XML to `__manifest__.py` data list
7. CREATE `l10n_pl_payroll/tests/test_student_exemption.py` with 4 tests: student+zlecenie=no ZUS, student+praca=normal ZUS, non-student+zlecenie=normal ZUS, student turns 26=exemption stops
8. Update `scripts/seed_realistic_data.py`: add 2 student employees (Jakub Wiśniewski age 22, Oliwia Kowalska age 24) on umowa zlecenie with `is_student=True`

## Key rule

On umowa o pracę, student status does NOT exempt from ZUS. Exemption is ONLY for zlecenie.

Also: health insurance is also zero for exempt students (no ZUS basis → no health). Net = gross - PIT only.

## Branch

Create branch `task/018-student-zus-exemption` from `main`. Commit with prefix `[TASK-018]`.

## Report

Write completion report to `tasks/TASK-018-report.md`.
