# TASK-037: Repeat localization audit with live UK/RU payslip-view verification

**Status:** done
**Assignee:** codex
**Branch:** main
**Created:** 2026-03-30
**Depends on:** TASK-030, TASK-033, TASK-035

## Context

After `TASK-035`, manual screenshot review still showed mixed-language UI on the payslip form in `uk` and `ru`.

This pass starts from two confirmed facts:

- some generic visible `uk.po` / `ru.po` labels still keep unnecessary Polish tails in parentheses
- more importantly, local Odoo still returns Polish payslip form XML for `uk_UA` and `ru_RU` through `pl.payroll.payslip.get_view()`, even when matching `.po` entries already exist

So the problem is not only translation-file completeness. It is also live translation application into the actual view path used by the UI.

## Goal

Make the repeat localization fix actually visible in the live `uk` / `ru` UI:

- clean the remaining mixed generic labels on the payslip surface
- close any still-empty user-facing translation gaps
- ensure `uk_UA` and `ru_RU` view translations are applied during module upgrade, not only `en_US`

## Scope

- `l10n_pl_payroll/models/pl_payroll_translation_loader.py`
- `l10n_pl_payroll/data/pl_payroll_en_us_translation_loader.xml`
- `l10n_pl_payroll/i18n/uk.po`
- `l10n_pl_payroll/i18n/ru.po`
- `codex-prompts/CODEX-037.md`
- `tasks/TASK-037.md`
- `tasks/TASK-037-report.md`

Primary UI area:

- payslip form (`view_pl_payroll_payslip_form`)

## What to fix

### A. Mixed generic UI in `uk` / `ru`

- Remove unnecessary Polish tails from generic visible strings:
  - warning texts
  - warning badges
  - notebook tabs
  - section labels
  - status labels
  - action/menu labels when they are just generic UI chrome

### B. Remaining user-facing gaps

- Fill any still-empty `msgstr` entries that affect report/view completeness.
- Focus on strings that a real user can still see in module UI or generated payroll reports.

### C. Live translation application

- Extend the translation loader so module upgrade writes database-backed translations for:
  - `en_US`
  - `uk_UA`
  - `ru_RU`
- Apply `model_terms` updates against the real Polish source layer used by the module, so `get_view()` can resolve `uk` / `ru` view terms correctly.
- After upgrade, verify translated output through `pl.payroll.payslip.get_view()`, not just `ir.ui.view.read()`.

## Acceptance Criteria

- [x] The payslip warning text about minimum wage is translated in live `uk_UA` and `ru_RU` `get_view()` output
- [x] The payslip minimum-wage badge is translated in live `uk_UA` and `ru_RU` `get_view()` output
- [x] The payslip notebook tabs `Rozliczenie pracownika`, `Raport twórczy`, and `Uwagi` are translated in live `uk_UA` and `ru_RU` `get_view()` output
- [x] Generic `uk` / `ru` UI strings no longer keep unnecessary Polish tails in the targeted payslip/localization surface
- [x] Remaining empty user-facing report strings fixed in `uk.po` and `ru.po`
- [x] `.po` files validate successfully
- [x] Translation loader compiles successfully
- [x] Module upgrade succeeds
- [x] Completion report written to `tasks/TASK-037-report.md`

## Required verification

1. Validate translation files:
   - `msgfmt --check-format l10n_pl_payroll/i18n/en_US.po`
   - `msgfmt --check-format l10n_pl_payroll/i18n/uk.po`
   - `msgfmt --check-format l10n_pl_payroll/i18n/ru.po`
2. Validate loader syntax:
   - `python3 -m py_compile l10n_pl_payroll/models/pl_payroll_translation_loader.py`
3. Upgrade the module:
   - `bash scripts/upgrade_module.sh`
4. Verify via XML-RPC with `context.lang` that `pl.payroll.payslip.get_view()` returns translated payslip form XML in:
   - `uk_UA`
   - `ru_RU`
5. Write a report to `tasks/TASK-037-report.md`.

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull

git add codex-prompts/CODEX-037.md
git add tasks/TASK-037.md
git add tasks/TASK-037-report.md
git add l10n_pl_payroll/models/pl_payroll_translation_loader.py
git add l10n_pl_payroll/data/pl_payroll_en_us_translation_loader.xml
git add l10n_pl_payroll/i18n/uk.po
git add l10n_pl_payroll/i18n/ru.po

git commit -m "[TASK-037] Finish live UK/RU localization coverage"
git push origin main
```
