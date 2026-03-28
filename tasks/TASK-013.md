# TASK-013: Add creative work report tracking (raport autorski)

**Status:** done
**Branch:** task/013-creative-report
**Created:** 2026-03-28

## Goal

Build `pl.payroll.creative.report` model for tracking monthly creative work documentation required for autorskie koszty (50% KUP) compliance.

## Requirements

- New model with workflow: draft > submitted > accepted > rejected
- Link to payslip: auto-search accepted report during computation
- Warning on payslip if report missing but autorskie KUP is used
- Views: form with statusbar, tree, menu under Payroll > Creative Reports
- Security: employee (read own), officer (CRUD), manager (full)
- Tests: workflow, payslip linkage, missing flag

## Files

- `models/pl_payroll_creative_report.py` — new model
- `models/pl_payroll_payslip.py` — add creative_report fields + logic
- `models/__init__.py` — add import
- `views/pl_payroll_creative_report_views.xml` — form/tree/search/action
- `views/pl_payroll_menus.xml` — add Creative Reports menu item
- `security/ir.model.access.csv` — access rules
- `security/pl_payroll_security.xml` — record rules
- `tests/test_creative_report.py` — tests
- `__manifest__.py` — include new files
