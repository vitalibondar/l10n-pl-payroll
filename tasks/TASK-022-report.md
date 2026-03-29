# TASK-022 Report

## What was done

- Added `_get_minimum_health_basis()` to `pl.payroll.payslip` using the minimum wage parameter and current etat fraction.
- Applied the minimum floor only to the health contribution basis, while keeping PIT/KUP calculations on the actual post-ZUS base so tax logic does not get distorted.
- Added `test_health_minimum.py` with 4 task-specific tests and registered it in `tests/__init__.py`.

## Verification

- `python3 -m py_compile l10n_pl_payroll/models/pl_payroll_payslip.py l10n_pl_payroll/tests/__init__.py l10n_pl_payroll/tests/test_health_minimum.py`
- `docker compose -f "$HOME/odoo-docker-compose.yml" run -v /Users/vb/l10n-pl-payroll/tools:/mnt/extra-addons/tools --rm odoo odoo -d omdev -u l10n_pl_payroll --test-enable --test-tags post_install/l10n_pl_payroll:TestHealthMinimum,post_install/l10n_pl_payroll:TestDzielo,post_install/l10n_pl_payroll:TestStudentExemption --stop-after-init`

## Notes

- `TestHealthMinimum` uses its own calendars, so it does not depend on demo XMLIDs missing in local `omdev`.
