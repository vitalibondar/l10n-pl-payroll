# TASK-030: Fix locale formatting and EN translations

**Status:** done
**Branch:** task/030-locale-format-fixes
**Created:** 2026-03-29

## Goal

Fix two regressions found during manual UI testing:

1. Year fields in PIT-11 and ZUS DRA wizards render with locale number grouping (`2,025`, `2,026`) instead of plain year values.
2. English Odoo UI still shows Polish labels and hints inside the payroll module instead of proper English localization tied to the selected Odoo language.

Write completion notes to `tasks/TASK-030-report.md`.

## Scope

- Disable locale grouping for integer year and month inputs in payroll wizards.
- Ensure `en_US` translations are applied reliably for module menus, actions, fields, and translated view content.
- Refresh and normalize module translation files for `pl`, `en_US`, `uk`, and `ru`.

## Files

- `l10n_pl_payroll/__manifest__.py`
- `l10n_pl_payroll/models/__init__.py`
- `l10n_pl_payroll/models/pl_payroll_translation_loader.py`
- `l10n_pl_payroll/data/pl_payroll_en_us_translation_loader.xml`
- `l10n_pl_payroll/i18n/pl.po`
- `l10n_pl_payroll/i18n/en_US.po`
- `l10n_pl_payroll/i18n/uk.po`
- `l10n_pl_payroll/i18n/ru.po`
- `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml`
- `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml`

## Acceptance Criteria

- [x] PIT-11 wizard shows year as `2025`, not `2,025`
- [x] ZUS DRA wizard shows year/month as plain numbers
- [x] English UI shows translated payroll menus and wizard labels
- [x] Translation files validate successfully
- [x] Module upgrade applies changes without XML errors

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull
git checkout -b task/030-locale-format-fixes

git add tasks/TASK-030.md
git add tasks/TASK-030-report.md
git add l10n_pl_payroll/__manifest__.py
git add l10n_pl_payroll/models/__init__.py
git add l10n_pl_payroll/models/pl_payroll_translation_loader.py
git add l10n_pl_payroll/data/pl_payroll_en_us_translation_loader.xml
git add l10n_pl_payroll/i18n/pl.po
git add l10n_pl_payroll/i18n/en_US.po
git add l10n_pl_payroll/i18n/uk.po
git add l10n_pl_payroll/i18n/ru.po
git add l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml
git add l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml

git commit -m "[TASK-030] Fix locale formatting and English translations"
git push -u origin task/030-locale-format-fixes
```
