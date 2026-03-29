# TASK-031: UI/UX audit of payroll module

**Status:** done
**Branch:** task/031-ui-ux-audit
**Created:** 2026-03-29
**Depends on:** TASK-016, TASK-027, TASK-030

## Goal

Do a deep UI/UX audit of the payroll module without changing module code.

Write the audit to `tasks/TASK-031-report.md`.

## Scope

- Review current XML views of the payroll module.
- Compare the current payslip detail form with the older idea where `net` was shown as a large hero number.
- Check the live UI on `http://localhost:8069` when possible.
- Evaluate the module from two roles:
  - Polish bookkeeper doing fast payroll verification
  - Manager / CKO / CFO looking for the main “do wypłaty” result

## Areas to review

- `l10n_pl_payroll/views/pl_payroll_payslip_views.xml`
- `l10n_pl_payroll/views/pl_payroll_menus.xml`
- `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml`
- `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml`
- `l10n_pl_payroll/views/pl_payroll_pit11_views.xml`
- `l10n_pl_payroll/views/pl_payroll_zus_dra_views.xml`
- `l10n_pl_payroll/report/pl_payroll_payslip_template.xml`
- `l10n_pl_payroll/i18n/en_US.po`

## Expected Output

- Clear verdict on whether the UI improved or regressed after tabs + Polish naming + current grouping.
- Prioritized problem list (P1/P2/P3).
- Explicit list of what should stay unchanged.
- Concrete recommendations tied to files or UI zones.
- Separate section: what to restore from the older “big net” version.
- Separate section: what not to do.
- Short implementation checklist for the next Codex.

## Acceptance Criteria

- [x] Current XML views reviewed
- [x] Live UI inspected on `localhost:8069`
- [x] Current payslip form compared with older “big net” layout
- [x] Verdict written from bookkeeper and manager perspectives
- [x] No module code changed

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull
git checkout -b task/031-ui-ux-audit

git add tasks/TASK-031.md
git add tasks/TASK-031-report.md

git commit -m "[TASK-031] Add payroll UI UX audit"
git push -u origin task/031-ui-ux-audit
```
