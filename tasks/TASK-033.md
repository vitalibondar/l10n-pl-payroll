# TASK-033: Fill missing tooltip translations for EN, UK, and RU

**Status:** done
**Branch:** task/033-tooltip-localization
**Created:** 2026-03-30
**Depends on:** TASK-027, TASK-030, TASK-032

## Goal

Close the remaining localization gaps that leave Polish tooltips and labels visible in non-Polish UIs.

The immediate regression is on the payslip form in `en_US`: field labels are translated, but many `help` tooltips still fall back to Polish because the `.po` entries are empty. Check `uk` and `ru` in the same pass and fill the same gaps there.

Write the completion report to `tasks/TASK-033-report.md`.

## Scope

- Audit remaining empty `msgstr` entries in:
  - `l10n_pl_payroll/i18n/en_US.po`
  - `l10n_pl_payroll/i18n/uk.po`
  - `l10n_pl_payroll/i18n/ru.po`
- Fill missing translations for payroll-specific tooltips (`help`) across the module.
- Keep Polish as the source language and preserve Polish legal/payroll terms in parentheses where needed.
- Re-run module upgrade so `en_US` direct translation loading updates database-backed translated fields.

## Acceptance Criteria

- [x] English payroll tooltips no longer fall back to Polish source text
- [x] Ukrainian payroll tooltips no longer fall back to Polish source text
- [x] Russian payroll tooltips no longer fall back to Polish source text
- [x] Translation files validate successfully
- [x] Module upgrade applies translation changes without XML/PO errors
- [x] Live UI and Odoo metadata checks confirm the visible tooltip regression is gone

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull
git checkout -b task/033-tooltip-localization

git add tasks/TASK-033.md
git add tasks/TASK-033-report.md
git add l10n_pl_payroll/i18n/en_US.po
git add l10n_pl_payroll/i18n/uk.po
git add l10n_pl_payroll/i18n/ru.po

git commit -m "[TASK-033] Fill missing tooltip translations"
git push -u origin task/033-tooltip-localization
```
