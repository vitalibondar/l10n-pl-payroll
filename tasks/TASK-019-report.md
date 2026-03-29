# TASK-019 Report

## Done

- Added `etat_fraction` and `below_minimum_wage` computed fields to `pl.payroll.payslip`
- Made standard KUP proportional to employment fraction
- Kept autorskie KUP and `standard_20` unchanged
- Added `MINIMUM_WAGE` parameter records for 2025 and 2026
- Added payslip form warning for proportional minimum wage
- Added `l10n_pl_payroll/tests/test_part_time.py` with 5 part-time scenarios
- Updated `scripts/seed_realistic_data.py` to create normalized part-time calendars and assign them to Natalia Ivanchuk and Yuliia Kravchuk

## Verification

- Module upgrade passed with `docker compose -f \"$HOME/odoo-docker-compose.yml\" run --rm odoo odoo -d omdev -u l10n_pl_payroll --stop-after-init`
- Manual XML-RPC verification on `omdev` confirmed:
  - `0.5 etat` + standard KUP => `etat_fraction=0.5`, `kup_amount=125.0`
  - `0.5 etat` + autorskie KUP => `etat_fraction=0.5`, `kup_amount=2157.25` from actual income basis, not halved
  - `0.5 etat` + `gross=2000` => `below_minimum_wage=True`
  - no contract calendar => `etat_fraction=1.0`, `kup_amount=250.0`

## Note

- Full `--test-enable` run is currently blocked by an existing path issue in `l10n_pl_payroll/tests/test_fixtures.py` looking for `/mnt/extra-addons/tools/expected_results.py`.
