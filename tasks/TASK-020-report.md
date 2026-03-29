# TASK-020 Report

## What was done

- Added sick leave fields, sick leave basis calculation, sick leave amount calculation, and YTD sick day tracking to `pl.payroll.payslip`.
- Integrated sick leave into payslip computation so ZUS and PPK use only the working-day gross, while health insurance and PIT include sick leave pay.
- Added sick leave fields to the payslip form view.
- Added sick leave history entries to `scripts/seed_realistic_data.py`.
- Added `test_sick_leave.py` with 6 task-specific tests and registered it in `tests/__init__.py`.

## Verification

- `python3 -m py_compile l10n_pl_payroll/models/pl_payroll_payslip.py l10n_pl_payroll/tests/test_sick_leave.py scripts/seed_realistic_data.py`
- `docker compose -f "$HOME/odoo-docker-compose.yml" run -v /Users/vb/l10n-pl-payroll/tools:/mnt/extra-addons/tools --rm odoo odoo -d omdev -u l10n_pl_payroll --test-enable --test-tags post_install/l10n_pl_payroll:TestSickLeave --stop-after-init`

## Notes

- Full module test suite in local `omdev` is still blocked by older demo-data assumptions in pre-existing tests (`demo_*` XMLIDs are missing in this database). TASK-020 tests pass independently.
