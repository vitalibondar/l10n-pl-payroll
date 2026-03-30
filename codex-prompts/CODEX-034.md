# TASK-034 prompt

```text
Read CLAUDE.md, then LESSONS.md, then tasks/TASK-034.md.

This is not another partial PO cleanup.
Do a full human localization pass so the module finally feels finished to real users.

The UX model is strict:

1. Labels, titles, buttons, and section names are for the expert user of that locale.
2. Tooltips and helper text are for the non-expert, or for the expert who forgot a detail.

That means:

- Polish source UI must sound like professional payroll software used by a real księgowa.
- EN / UK / RU must not read like literal machine translation.
- Polish payroll-specific terms must stay in parentheses where that helps users map the interface to Polish documents.
- Report copy and warnings count too, not just model fields.

Do the work in this order:

1. Fix source labels and help text in Python models where auto-generated, weak, or technical text leaked into the UI.
2. Audit and fix EN / UK / RU translations across labels, tooltips, view text, report text, warnings, and wizard helper copy.
3. Rewrite awkward translations manually. If a line sounds robotic, treat it as broken even if it is technically translated.
4. Keep universal abbreviations as-is where appropriate: ZUS, PIT, PPK, PESEL.
5. Keep Polish-specific concepts in parentheses where helpful, including:
   - kwota zmniejszająca podatek
   - koszty uzyskania przychodu
   - raport pracy twórczej
   - lista płac

Non-negotiable quality bar:

- No visible unfinished Polish strings in EN / UK / RU reports and views, unless intentionally preserved as a Polish legal term.
- No obvious machine-translation phrasing.
- No source labels like Bonus Gross Total or similar leaks in user-facing UI.
- Tooltips must explain the concept, not just restate the label.

Files in scope:

- l10n_pl_payroll/models/*.py
- l10n_pl_payroll/views/*.xml
- l10n_pl_payroll/wizard/*.py
- l10n_pl_payroll/wizard/*.xml
- l10n_pl_payroll/report/*.xml
- l10n_pl_payroll/i18n/en_US.po
- l10n_pl_payroll/i18n/uk.po
- l10n_pl_payroll/i18n/ru.po
- l10n_pl_payroll/i18n/pl.po if source terms change
- tasks/TASK-034-report.md

Verification:

- msgfmt --check-format l10n_pl_payroll/i18n/en_US.po
- msgfmt --check-format l10n_pl_payroll/i18n/uk.po
- msgfmt --check-format l10n_pl_payroll/i18n/ru.po
- grep for remaining suspicious untranslated strings in user-facing areas

Work on branch task/034-localization-human-pass.
Commit with prefix [TASK-034].
Write completion report to tasks/TASK-034-report.md.
```
