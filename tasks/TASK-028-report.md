# TASK-028 Report

## What was done

- Added `scripts/verify_calculations.py` for end-to-end XML-RPC verification of confirmed payslips, PIT-11, ZUS DRA, and batch regeneration.
- Updated `scripts/upgrade_module.sh` so the Odoo docker compose run mounts the addon from the current repo checkout instead of hardcoding `~/l10n-pl-payroll`.
- Fixed Odoo translation files `l10n_pl_payroll/i18n/*.po` by adding the module metadata format that Odoo expects during module upgrade.
- Fixed missing create/write access for `pl.payroll.zus.dra.line` in `l10n_pl_payroll/security/ir.model.access.csv`, which was blocking ZUS DRA generation.
- Fixed `scripts/verify_calculations.py` field mismatches between `payslip_line_ids` and `line_ids`.
- Fixed `scripts/seed_realistic_data.py` so historical sick leave, bonus, deduction, and vacation changes recompute all later payslips for the same employee.
- Made `scripts/seed_realistic_data.py` idempotent after verification runs by cleaning `pl.payroll.pit11`, `pl.payroll.zus.dra.line`, and `pl.payroll.zus.dra` before deleting employees.

## Bugs found and fixed

- `ZUS DRA` wizard failed with access error because users could not create `pl.payroll.zus.dra.line` records.
- Full verification initially failed because the verifier queried wrong relation field names.
- Seeded payroll data became inconsistent after backdated adjustments; later months were not recomputed, so YTD PIT for `Aleksander Volkov` crossed the threshold one month late.
- Re-running the seed after verification left stale `PIT-11` and `ZUS DRA` data, which blocked employee cleanup.

## Verification

- `bash scripts/upgrade_module.sh`
- `python3 scripts/seed_realistic_data.py`
- `python3 scripts/verify_calculations.py`
- `python3 -m py_compile scripts/seed_realistic_data.py scripts/verify_calculations.py`

## Final result

- Seed creates 23 employees, 23 contracts, and 282 payslips with 0 failures.
- All scenario checks pass, including threshold crossing, student zlecenie, dzieło, PPK opt-out, half-time, and sick leave.
- `PIT-11` verification: 23 records, 0 differences.
- `ZUS DRA` verification: 1 record, 0 differences.
- Batch wizard verification: 23 payslips recreated, 0 differences.
- `TOTAL_FAILURES=0`.
