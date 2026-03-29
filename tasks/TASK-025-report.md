# TASK-025 Report

## What was done

- Added `vacation_days` and `vacation_pay` fields to `pl.payroll.payslip` and integrated vacation supplement calculation into the gross build-up.
- Implemented `_compute_vacation_pay()` using the last 3 confirmed payslips, variable components (`overtime_amount` + `bonus_gross_total`), and etat-aware hour conversion for vacation days.
- Kept fixed-salary and zero-vacation cases neutral: no supplement, no gross distortion.
- Added vacation fields to the payslip form and extended `scripts/seed_realistic_data.py` with 3 vacation entries applied after bonus adjustments.
- Added `test_vacation_pay.py` with coverage for fixed salary, variable supplement, and zero-day behavior.
- Moved `STANDARD_MONTHLY_HOURS` from demo-only data into regular 2025/2026 payroll parameters so overtime and vacation logic no longer depend on demo XML.

## Verification

- `python3 -m py_compile l10n_pl_payroll/models/pl_payroll_payslip.py l10n_pl_payroll/tests/test_vacation_pay.py scripts/seed_realistic_data.py`
- `xmllint --noout l10n_pl_payroll/views/pl_payroll_payslip_views.xml l10n_pl_payroll/data/pl_payroll_parameters_2025.xml l10n_pl_payroll/data/pl_payroll_parameters_2026.xml`
- `docker compose -f "$HOME/odoo-docker-compose.yml" run -v /Users/vb/l10n-pl-payroll/tools:/mnt/extra-addons/tools --rm odoo odoo -d omdev -u l10n_pl_payroll --test-enable --test-tags post_install/l10n_pl_payroll:TestVacationPay --stop-after-init`

## Notes

- Vacation supplement is applied only to `umowa o pracę`; `umowa zlecenie` and `umowa o dzieło` return zero supplement.
- Hour conversion uses `etat_fraction`, so half-time vacation days do not get counted as 8 full hours.
