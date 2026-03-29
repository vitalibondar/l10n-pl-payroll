# TASK-021 Report

## What was done

- Added base payroll contract types in `data/pl_payroll_contract_type_data.xml` and switched module/demo references to those shared XMLIDs, including the new `Umowa o dzieło`.
- Added a dedicated `umowa o dzieło` calculation path in `pl.payroll.payslip`: no ZUS, no health, no PPK, 20% or 50% KUP on gross, flat 12% PIT, and the `<= 200 PLN` ryczałt case without KUP.
- Updated module metadata to reflect support for `umowa o dzieło`.
- Added `test_dzielo.py` with 7 task-specific tests and registered it in `tests/__init__.py`.
- Updated `scripts/seed_realistic_data.py` with a fictional `dzieło` contractor (`Bartosz Nowicki`) and 4 monthly payslips.
- Removed a demo-calendar dependency from `test_student_exemption.py` so the touched regression test can run in local `omdev`.

## Verification

- `python3 -m py_compile l10n_pl_payroll/__manifest__.py l10n_pl_payroll/models/pl_payroll_payslip.py l10n_pl_payroll/tests/__init__.py l10n_pl_payroll/tests/test_dzielo.py l10n_pl_payroll/tests/test_student_exemption.py l10n_pl_payroll/tests/test_part_time.py l10n_pl_payroll/tests/test_fixtures.py l10n_pl_payroll/tests/test_cumulative.py scripts/seed_realistic_data.py`
- `xmllint --noout l10n_pl_payroll/data/pl_payroll_contract_type_data.xml l10n_pl_payroll/data/demo/pl_payroll_demo.xml`
- `docker compose -f "$HOME/odoo-docker-compose.yml" run -v /Users/vb/l10n-pl-payroll/tools:/mnt/extra-addons/tools --rm odoo odoo -d omdev -u l10n_pl_payroll --test-enable --test-tags post_install/l10n_pl_payroll:TestDzielo,post_install/l10n_pl_payroll:TestStudentExemption --stop-after-init`

## Notes

- Full local suite in `omdev` is still blocked by older tests that depend on demo XMLIDs not present in this database, including `TestPayrollFixtures`, `TestPayrollPayslip`, `TestPayrollCumulative`, and `TestPartTime`.
