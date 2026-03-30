# TASK-035: Repeat localization completeness audit for view coverage

**Status:** done
**Assignee:** codex
**Branch:** main
**Created:** 2026-03-30
**Depends on:** TASK-033, TASK-034

## Context

TASK-034 cleaned up source labels and filled live `msgstr` gaps, but the next screenshot review still showed mixed-language UI on the payslip form.

Root cause for this follow-up task:

- some strings existed in `uk.po` / `ru.po` only as field translations, not as view-level entries
- some user-facing view strings present in `en_US.po` were missing entirely from `uk.po` / `ru.po`
- some short visible labels still carried unnecessary Polish leftovers, which made the UI look half-translated

This task is not another full human rewrite. It is a completeness audit focused on actual missing UI coverage.

## Goal

Close the remaining localization gaps that still let Polish leak into `uk` / `ru` user-facing UI, especially on the payslip form and payroll-generation wizards.

Use `en_US.po` as the coverage baseline for user-facing entries and compare `uk.po` / `ru.po` against it.

## Scope

- `l10n_pl_payroll/i18n/uk.po`
- `l10n_pl_payroll/i18n/ru.po`
- `tasks/TASK-035-report.md`
- `codex-prompts/CODEX-035.md`

Primary UI areas:

- payslip form (`view_pl_payroll_payslip_form`)
- PIT-11 generation wizard
- ZUS DRA generation wizard

## What to fix

### A. Missing coverage

- Add missing `msgid` entries that exist in `en_US.po` but not in `uk.po` / `ru.po`.
- Add missing `model_terms:ir.ui.view,...` occurrences where `uk.po` / `ru.po` only cover the field label but not the visible view text.

### B. Mixed visible UI

- Rewrite short visible labels that still look hybrid because of unnecessary Polish leftovers:
  - buttons
  - status labels
  - section headers
  - warning badges

Keep Polish only where it is genuinely useful to map the UI to Polish payroll/legal documents. Generic UI labels should read like native UI.

## Acceptance Criteria

- [x] `uk.po` covers the same user-facing payslip/wizard view entries as `en_US.po`
- [x] `ru.po` covers the same user-facing payslip/wizard view entries as `en_US.po`
- [x] Missing view occurrences for payslip warning badges and section headers are added
- [x] Missing PIT-11 / ZUS DRA wizard helper copy and primary action labels are added
- [x] Short visible `uk` / `ru` labels no longer carry unnecessary Polish tails for generic UI states and buttons
- [x] `.po` files validate successfully
- [x] Completion report written to `tasks/TASK-035-report.md`

## Required verification

1. Validate translation files:
   - `msgfmt --check-format l10n_pl_payroll/i18n/en_US.po`
   - `msgfmt --check-format l10n_pl_payroll/i18n/uk.po`
   - `msgfmt --check-format l10n_pl_payroll/i18n/ru.po`
2. Run a coverage diff script comparing `en_US.po` occurrence coverage against `uk.po` and `ru.po`.
3. Confirm that the specific payslip/wizard gaps found in this task are gone.
4. Write a report to `tasks/TASK-035-report.md`.

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull

git add codex-prompts/CODEX-035.md
git add tasks/TASK-035.md
git add tasks/TASK-035-report.md
git add l10n_pl_payroll/i18n/uk.po
git add l10n_pl_payroll/i18n/ru.po

git commit -m "[TASK-035] Close remaining localization gaps"
git push origin main
```
