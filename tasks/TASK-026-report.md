# TASK-026 Report

## What was done

- Added a new `pl.payroll.batch.wizard` with company, department filter, explicit period, and optional auto-compute.
- Added wizard view and repointed the existing payroll menu entry from old batch compute to the new generation flow.
- Added a list-view server action `Confirm Payslips` for mass-confirming selected payslips through `records.action_confirm()`.
- Added wizard access rights for payroll officer and manager.
- Added `test_batch_wizard.py` with coverage for creation, skipping existing payslips, department filtering, auto-compute, and mass confirm server action.

## Verification

- `python3 -m py_compile l10n_pl_payroll/wizard/pl_payroll_batch_wizard.py l10n_pl_payroll/tests/test_batch_wizard.py`
- `xmllint --noout l10n_pl_payroll/wizard/pl_payroll_batch_wizard_views.xml l10n_pl_payroll/views/pl_payroll_payslip_views.xml l10n_pl_payroll/views/pl_payroll_menus.xml`
- `docker compose -f "$HOME/odoo-docker-compose.yml" run -v /Users/vb/l10n-pl-payroll/tools:/mnt/extra-addons/tools --rm odoo odoo -d omdev -u l10n_pl_payroll --test-enable --test-tags post_install/l10n_pl_payroll:TestPayrollBatchWizard --stop-after-init`

## Notes

- The legacy `pl.payroll.batch.compute` wizard stays in the codebase for backward compatibility and its existing tests, but the menu now points to the richer batch-generation wizard from TASK-026.
- Batch wizard tests run in a dedicated fictional company, so they do not collide with local `omdev` payroll history.
