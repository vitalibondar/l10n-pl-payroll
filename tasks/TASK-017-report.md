# TASK-017 Report

## Done

- Added `scripts/upgrade_module.sh` to stop local Odoo, run module upgrade for `l10n_pl_payroll`, and start Odoo again.
- Added `scripts/seed_and_verify.sh` to run the upgrade, wait 5 seconds, and then call `scripts/seed_realistic_data.py`.
- Added `scripts/README.md` with brief usage notes.
- Updated `tasks/TASK-017.md` status to `done`.

## Verification

- Ran `bash -n scripts/upgrade_module.sh`
- Ran `bash -n scripts/seed_and_verify.sh`
- Set both shell scripts as executable

## Notes

- `scripts/seed_realistic_data.py` is not present on this branch yet, so `scripts/seed_and_verify.sh` was only syntax-checked, not executed end-to-end.
