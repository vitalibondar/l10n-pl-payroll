# Codex Task: TASK-016 — UI polish and bugfixes

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-016.md` for full requirements.

## Summary

Fix UI issues in the payslip module views for Odoo 18:

1. Add `notes = fields.Text(string="Notes")` to `pl.payroll.payslip` model if missing
2. Set human-readable `string` attributes on all ZUS/PIT/PPK fields in the Python model
3. Reorganize the payslip form view into logical notebook pages (Wynagrodzenie, Koszty pracodawcy, Linie, Raport twórczy, Notatki)
4. Expand the list view with more optional columns (kup_type, zus_total_ee, pit_due, total_employer_cost)
5. Fix menu ordering in `pl_payroll_menus.xml`

## Key constraints

- Odoo 18: use `list` not `tree` in view_mode
- Do NOT change computation logic — UI only
- Check if `pl.payroll.payslip.line` model exists (from TASK-014) before referencing it in views
- All XML IDs must follow existing naming convention (check existing files)
- Update `ir.model.access.csv` if you add any fields that need new access rules

## Files to modify

- `models/pl_payroll_payslip.py`
- `views/pl_payroll_payslip_views.xml`
- `views/pl_payroll_menus.xml`

## Branch

Create branch `task/016-ui-polish` from `main`. Commit with prefix `[TASK-016]`.

## Report

Write your completion report to `tasks/TASK-016-report.md` describing what you changed and why.
