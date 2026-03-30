# TASK-035 prompt

```text
Read CLAUDE.md, then LESSONS.md, then tasks/TASK-035.md.

This is a repeat localization completeness audit after TASK-034.
A screenshot still shows mixed-language UI on the payslip form, so do not trust “all msgstr are filled” as proof of completeness.

Treat en_US.po as the coverage baseline for user-facing UI entries.

Do the work in this order:

1. Compare user-facing msgid coverage in en_US.po vs uk.po and ru.po.
2. Check not only msgid/msgstr presence, but also occurrence coverage for model_terms:ir.ui.view entries.
3. Focus first on the payslip form and the PIT-11 / ZUS DRA generation wizards.
4. Add missing view-level entries or occurrences in uk.po and ru.po.
5. Fix short visible labels that still read like mixed UI because of unnecessary Polish leftovers in buttons, badges, section headers, or status labels.
6. Keep Polish only where it is genuinely needed to match Polish payroll/legal documents. Generic UI labels should read as native UI, not hybrid UI.

Hard rules:

- Do not stop at empty msgstr audit.
- Do not assume an existing field-level translation also covers the matching view text.
- Do not preserve Polish in parentheses for generic states or buttons.
- Do not expand scope into another full rewrite of every PO file. Fix the concrete completeness gaps.

Verification:

- msgfmt --check-format l10n_pl_payroll/i18n/en_US.po
- msgfmt --check-format l10n_pl_payroll/i18n/uk.po
- msgfmt --check-format l10n_pl_payroll/i18n/ru.po
- Run a script that compares en_US.po occurrence coverage against uk.po and ru.po for user-facing view/model entries.
- Write completion report to tasks/TASK-035-report.md.

Work on main for this task.
Commit with prefix [TASK-035].
```
