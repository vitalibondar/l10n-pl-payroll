# TASK-023 Report

## What was done

- Added `pl.payroll.pit11` with yearly aggregated PIT-11 totals, unique employee/company/year constraint, and reusable aggregation logic from confirmed payslips.
- Added `pl.payroll.pit11.wizard` to generate or refresh PIT-11 records for a selected year and return the filtered list view.
- Added PIT-11 list/form views, wizard form, payroll menu entry under `Reports`, company-level security rule, and access rights for officers/managers.
- Added printable QWeb PDF summary for PIT-11 with employer data, employee data, annual totals, and generation footer.
- Added `test_pit11.py` with coverage for generation, 7.75% health deductible, regeneration without duplicates, and PPK employer contribution included in income.

## Verification

- `python3 -m py_compile l10n_pl_payroll/models/pl_payroll_pit11.py l10n_pl_payroll/wizard/pl_payroll_pit11_wizard.py l10n_pl_payroll/tests/test_pit11.py`
- `xmllint --noout l10n_pl_payroll/views/pl_payroll_pit11_views.xml l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml l10n_pl_payroll/report/pl_payroll_pit11_template.xml l10n_pl_payroll/security/pl_payroll_pit11_security.xml l10n_pl_payroll/views/pl_payroll_menus.xml`
- `docker compose -f "$HOME/odoo-docker-compose.yml" run -v /Users/vb/l10n-pl-payroll/tools:/mnt/extra-addons/tools --rm odoo odoo -d omdev -u l10n_pl_payroll --test-enable --test-tags post_install/l10n_pl_payroll:TestPit11 --stop-after-init`

## Notes

- Local `omdev` already contains older confirmed payslips and PIT-11 data, so the tests isolate assertions to the employees created inside `TestPit11`.
