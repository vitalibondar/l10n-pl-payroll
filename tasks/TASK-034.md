# TASK-034: Human-pass localization cleanup for PL, EN, UK, RU

**Status:** done
**Assignee:** codex
**Depends on:** TASK-027, TASK-030, TASK-033
**Branch:** task/034-localization-human-pass
**Created:** 2026-03-30

## Context

Previous localization passes improved the module, but the result is still inconsistent:

- some user-facing labels and report strings are still untranslated or fall back to Polish
- some source field labels are still auto-generated or technical instead of professional Polish
- some EN / UK / RU tooltip translations are literal, awkward, or misleading
- the intended UX model is not fully respected: professional labels for experts, explanatory tooltips for non-experts

This task is a full human review pass, not a partial PO cleanup.

## Goal

Make localization actually feel finished to a real user in all supported languages:

1. **PL source layer**
   - professional Polish labels for payroll experts
   - clear, human tooltip help where the concept is not obvious
2. **EN / UK / RU localized layer**
   - labels that read naturally for a professional non-Polish user
   - tooltips that explain the concept for a non-expert
   - Polish payroll/legal terms preserved in parentheses where that helps orientation

## Required UX model

Treat every user-facing string as belonging to one of two layers:

1. **Explicit layer = label / title / button / visible section name**
   - written for the expert user of that locale
   - concise, professional, native-sounding
   - no dumbing down
2. **Implicit layer = tooltip / help text / short explanatory sentence**
   - written for the non-expert or for the expert who forgot a detail
   - explains the payroll concept, not just the field name
   - in EN / UK / RU also explains Polish-specific concepts that a local Polish user would already know

## Scope

- `l10n_pl_payroll/models/*.py`
- `l10n_pl_payroll/views/*.xml`
- `l10n_pl_payroll/wizard/*.py`
- `l10n_pl_payroll/wizard/*.xml`
- `l10n_pl_payroll/report/*.xml`
- `l10n_pl_payroll/i18n/en_US.po`
- `l10n_pl_payroll/i18n/uk.po`
- `l10n_pl_payroll/i18n/ru.po`
- `l10n_pl_payroll/i18n/pl.po` if source terms change

## What to fix

### A. Source-language cleanup

- Replace any auto-generated / technical / English field labels that leaked into source UI.
- Review Polish `help=` texts and improve the ones that are too thin, vague, or robotic.
- Keep Polish source labels optimized for a payroll professional, not for a beginner.

### B. Translation cleanup

- Fill missing translations for visible strings in EN / UK / RU.
- Fix awkward, literal, machine-sounding, or misleading translations.
- Keep professional Polish terms in parentheses where needed for cross-reference:
  - e.g. `koszty uzyskania przychodu`
  - `kwota zmniejszająca podatek`
  - `raport pracy twórczej`
  - `lista płac`
- Keep universal abbreviations as-is where appropriate: `ZUS`, `PIT`, `PPK`, `PESEL`.

### C. Reports and views

- Audit report copy and view text, not just model fields.
- Do not leave report badges, section captions, warnings, or helper copy in Polish in EN / UK / RU UI unless intentionally preserved as a Polish legal term.

## Hard rules

- Do **not** stop after fixing a handful of empty `msgstr`.
- Do **not** accept literal translation if it sounds unnatural to a real user.
- Do **not** translate blindly word-by-word where the locale needs a different phrasing.
- Do **not** remove the Polish source term from EN / UK / RU when that term is needed to match Polish payroll documents.
- Do **not** over-explain obvious professional labels.

## Acceptance Criteria

- [x] No important user-facing payroll labels remain auto-generated, technical, or English in the Polish source UI
- [x] EN UI no longer shows unfinished Polish report/view strings except deliberate Polish terms in parentheses
- [x] UK UI no longer shows unfinished Polish report/view strings except deliberate Polish terms in parentheses
- [x] RU UI no longer shows unfinished Polish report/view strings except deliberate Polish terms in parentheses
- [x] Tooltips in EN / UK / RU read like human localization, not literal machine translation
- [x] The two-layer UX model is visible in the result: expert labels + explanatory tooltips
- [x] `.po` files validate successfully

## Required verification

1. Validate translation files:
   - `msgfmt --check-format l10n_pl_payroll/i18n/en_US.po`
   - `msgfmt --check-format l10n_pl_payroll/i18n/uk.po`
   - `msgfmt --check-format l10n_pl_payroll/i18n/ru.po`
2. Grep for remaining suspicious untranslated strings in user-facing areas.
3. Write a report to `tasks/TASK-034-report.md`:
   - what source labels/help changed
   - what translation gaps were closed
   - what awkward translations were rewritten manually
   - residual risk if any

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull
git checkout -b task/034-localization-human-pass

git add tasks/TASK-034.md
git add tasks/TASK-034-report.md
git add codex-prompts/CODEX-034.md
git add l10n_pl_payroll/models/*.py
git add l10n_pl_payroll/views/*.xml
git add l10n_pl_payroll/wizard/*.py
git add l10n_pl_payroll/wizard/*.xml
git add l10n_pl_payroll/report/*.xml
git add l10n_pl_payroll/i18n/*.po

git commit -m "[TASK-034] Human-pass localization cleanup"
git push -u origin task/034-localization-human-pass
gh pr create --title "[TASK-034] Human-pass localization cleanup" --body "Full localization pass for PL, EN, UK, and RU."
```
