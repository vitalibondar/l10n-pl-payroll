# TASK-032: Restore net-first payslip UI hierarchy

**Status:** done
**Branch:** task/032-payslip-ui-ux-polish
**Created:** 2026-03-30
**Depends on:** TASK-016, TASK-027, TASK-030, TASK-031

## Goal

Restore a strong visual focus on `net` in the payslip form without changing payroll computation logic. Keep the tabbed structure, improve first-screen scanability, and close the most visible localization and formatting regressions found in `TASK-031`.

Write the completion report to `tasks/TASK-032-report.md`.

## Scope

- Update `l10n_pl_payroll/views/pl_payroll_payslip_views.xml` to bring back a hero-style `net` amount and a compact summary block above tabs.
- Rebalance the first payslip tab so `gross`, `net`, and the main deduction/tax sections are easier to scan.
- Keep the current warning banners visible.
- Make `PIT-11` and `ZUS DRA` easier to discover from the payroll menu.
- Add short explanatory context to the `PIT-11` and `ZUS DRA` wizards.
- Disable locale grouping for year/month display in `ZUS DRA` list/form views.
- Fill the most visible English translation gaps tied to these UI surfaces.

## Acceptance Criteria

- [x] `net` is the first visually dominant number on the payslip form
- [x] employee, period, state, gross, and total employer cost are visible above tabs
- [x] warnings about creative report and minimum wage remain clearly visible
- [x] first tab is more readable without removing tabs
- [x] `PIT-11` and `ZUS DRA` are directly discoverable in the payroll menu
- [x] `ZUS DRA` year no longer renders as `2,026` in list/form views
- [x] `bash scripts/upgrade_module.sh` passes
- [x] live UI check on `http://localhost:8069` confirms layout stability

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull
git checkout -b task/032-payslip-ui-ux-polish

git add tasks/TASK-032.md
git add tasks/TASK-032-report.md
git add l10n_pl_payroll/views/pl_payroll_payslip_views.xml
git add l10n_pl_payroll/views/pl_payroll_menus.xml
git add l10n_pl_payroll/views/pl_payroll_zus_dra_views.xml
git add l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml
git add l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml
git add l10n_pl_payroll/i18n/en_US.po

git commit -m "[TASK-032] Restore net-first payslip UI"
git push -u origin task/032-payslip-ui-ux-polish
```
