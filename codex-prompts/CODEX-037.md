# TASK-037 prompt

```text
Read CLAUDE.md, then LESSONS.md, then tasks/TASK-037.md.

This is another repeat localization audit after TASK-035.
Do not trust `.po` coverage alone.

The screenshot regression proves two separate failures:

1. some visible `uk` / `ru` strings on the payslip form still read as mixed Polish UI
2. some `uk_UA` / `ru_RU` view translations do not reliably land in the live Odoo database after upgrade, even when the `.po` entries exist

Do the work in this order:

1. Compare the highlighted payslip-form strings from the screenshot against `uk.po` and `ru.po`.
2. Remove unnecessary Polish tails from generic visible UI labels, tabs, badges, and statuses in `uk.po` and `ru.po`.
3. Fill any remaining empty user-facing `msgstr` entries that still affect report/view completeness.
4. Make the translation loader apply not only `en_US`, but also `uk_UA` and `ru_RU` database-backed translations during module upgrade.
5. Verify the loader against the real `get_view` path used by the UI, not just raw `.po` files.
6. Upgrade the module locally.
7. Verify via XML-RPC that `pl.payroll.payslip.get_view()` for `view_pl_payroll_payslip_form` is actually translated in `uk_UA` and `ru_RU`.

Hard rules:

- Do not stop at `.po` edits if the live DB still serves Polish payslip form XML.
- Do not keep Polish in parentheses for generic UI strings like tabs, buttons, warnings, section names, or statuses.
- Keep Polish only for genuinely document-facing payroll/legal terms where it helps orientation.
- Do not expand this into a full rewrite of all translation files.

Verification:

- msgfmt --check-format l10n_pl_payroll/i18n/en_US.po
- msgfmt --check-format l10n_pl_payroll/i18n/uk.po
- msgfmt --check-format l10n_pl_payroll/i18n/ru.po
- python3 -m py_compile l10n_pl_payroll/models/pl_payroll_translation_loader.py
- bash scripts/upgrade_module.sh
- XML-RPC check confirming `pl.payroll.payslip.get_view()` in `uk_UA` and `ru_RU` contains translated payslip warning/badge/tab strings
- Write completion report to tasks/TASK-037-report.md.

Work on main for this task.
Commit with prefix [TASK-037].
```
