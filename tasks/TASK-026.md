# TASK-026: Batch payslip generation wizard

**Status:** done
**Branch:** task/026-batch-payslip
**Created:** 2026-03-29
**Depends on:** none

## Goal

Create a wizard to generate payslips for ALL employees for a given month in one click. Currently each payslip must be created manually. For 82 employees, this is impractical.

Write your completion report to `tasks/TASK-026-report.md`.

## What to implement

### 1. Create batch generation wizard

`wizard/pl_payroll_batch_wizard.py`:

```python
class PlPayrollBatchWizard(models.TransientModel):
    _name = "pl.payroll.batch.wizard"
    _description = "Batch Payslip Generation"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    department_ids = fields.Many2many("hr.department", string="Departments (empty = all)")
    auto_compute = fields.Boolean(default=True, string="Auto-compute after creation")

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from:
            # Auto-set date_to to last day of month
            import calendar
            d = fields.Date.to_date(self.date_from)
            last_day = calendar.monthrange(d.year, d.month)[1]
            self.date_to = d.replace(day=last_day)
            self.date_from = d.replace(day=1)

    def action_generate(self):
        Contract = self.env["hr.contract"]
        Payslip = self.env["pl.payroll.payslip"]

        domain = [
            ('state', '=', 'open'),
            ('company_id', '=', self.company_id.id),
            ('date_start', '<=', self.date_to),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', self.date_from),
        ]
        if self.department_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))

        contracts = Contract.search(domain)
        created_ids = []
        skipped = 0

        for contract in contracts:
            # Check if payslip already exists
            existing = Payslip.search([
                ('employee_id', '=', contract.employee_id.id),
                ('date_from', '=', self.date_from),
                ('state', '!=', 'cancelled'),
            ], limit=1)
            if existing:
                skipped += 1
                continue

            payslip = Payslip.create({
                'employee_id': contract.employee_id.id,
                'contract_id': contract.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
            created_ids.append(payslip.id)

        if self.auto_compute and created_ids:
            Payslip.browse(created_ids).compute_payslip()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated Payslips',
            'res_model': 'pl.payroll.payslip',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_ids)],
        }
```

### 2. Batch confirm action

Add server action for mass-confirming payslips from list view:

In `pl_payroll_payslip.py`, the `action_confirm` already works on recordsets. Add a server action XML that calls it from the list view "Action" dropdown.

### 3. Views

- Wizard form: date_from, date_to, department filter, auto_compute checkbox, Generate button
- Server action for batch confirm
- Menu: Polish Payroll → Listy płac → Generuj listę

### 4. Security

Add wizard to security CSV.

### 5. Tests

Create `tests/test_batch_wizard.py`:

- `test_batch_creates_payslips`: wizard with valid date → creates payslips for all active contracts
- `test_batch_skips_existing`: payslip already exists → skipped
- `test_batch_department_filter`: only selected department gets payslips
- `test_batch_auto_compute`: auto_compute=True → payslips in "computed" state
- `test_batch_confirm_action`: mass confirm from list

## Files to create/modify

- CREATE: `l10n_pl_payroll/wizard/pl_payroll_batch_wizard.py`
- CREATE: `l10n_pl_payroll/wizard/pl_payroll_batch_wizard_views.xml`
- CREATE: `l10n_pl_payroll/tests/test_batch_wizard.py`
- MODIFY: `l10n_pl_payroll/__init__.py` (wizard import)
- MODIFY: `l10n_pl_payroll/__manifest__.py`
- MODIFY: `l10n_pl_payroll/security/ir.model.access.csv`
- MODIFY: `l10n_pl_payroll/views/pl_payroll_payslip_views.xml` (batch confirm server action)
