# TASK-023: PIT-11 annual declaration generation

**Status:** done
**Branch:** task/023-pit11
**Created:** 2026-03-29
**Depends on:** none (uses existing YTD data)

## Goal

Generate PIT-11 annual information document. This is a mandatory document the employer must produce for each employee by end of February following the tax year. It summarizes all income, ZUS, health, and PIT paid.

For now: generate as a structured data model + printable PDF/HTML report. Official XML schema for e-Deklaracje is a later task.

Write your completion report to `tasks/TASK-023-report.md`.

## What PIT-11 contains

Key fields (simplified):
- Employee: name, PESEL, address
- Employer: name, NIP, address
- Tax year
- **Section D**: Income and costs
  - Income from employment (gross minus ZUS employee)
  - KUP amount (total for year)
  - Tax advance paid (total pit_due for year)
  - Health contribution (7.75% of basis — the tax-deductible part, NOT the full 9%)
- **Section E**: ZUS contributions
  - Total ZUS employee (emerytalne + rentowe + chorobowe)
- **Section F**: Health contributions
  - Total health contributions paid
- **Section G**: Tax advance paid

## What to implement

### 1. Create PIT-11 model

Create `l10n_pl_payroll/models/pl_payroll_pit11.py`:

```python
class PlPayrollPit11(models.Model):
    _name = "pl.payroll.pit11"
    _description = "PIT-11 Annual Tax Information"
    _order = "year desc, employee_id"

    employee_id = fields.Many2one("hr.employee", required=True)
    company_id = fields.Many2one("res.company", required=True)
    year = fields.Integer(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft')

    # Aggregated fields from payslips
    total_gross = fields.Float(readonly=True)
    total_zus_ee = fields.Float(readonly=True, string="ZUS EE łącznie")
    total_health = fields.Float(readonly=True, string="Składka zdrowotna łącznie")
    health_deductible = fields.Float(readonly=True, string="Składka zdrowotna odliczana (7.75%)")
    total_kup = fields.Float(readonly=True, string="KUP łącznie")
    total_income = fields.Float(readonly=True, string="Dochód (przychód - KUP)")
    total_pit_paid = fields.Float(readonly=True, string="Zaliczki PIT zapłacone")
    total_ppk_er = fields.Float(readonly=True, string="PPK pracodawcy (przychód)")

    payslip_count = fields.Integer(readonly=True)
```

### 2. Generation wizard

Create `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard.py`:

A wizard that:
1. Takes a year as input
2. Finds all employees with confirmed payslips in that year
3. Sums up all relevant fields from their payslips
4. Creates (or updates) PIT-11 records

```python
class PlPayrollPit11Wizard(models.TransientModel):
    _name = "pl.payroll.pit11.wizard"
    _description = "Generate PIT-11"

    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year - 1)

    def action_generate(self):
        Payslip = self.env["pl.payroll.payslip"]
        Pit11 = self.env["pl.payroll.pit11"]

        date_from = f"{self.year}-01-01"
        date_to = f"{self.year}-12-31"

        payslips = Payslip.search([
            ('state', '=', 'confirmed'),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
        ])

        employees = payslips.mapped('employee_id')
        created = 0

        for emp in employees:
            emp_payslips = payslips.filtered(lambda p: p.employee_id == emp)

            total_gross = sum(p.gross for p in emp_payslips)
            total_zus_ee = sum(p.zus_total_ee for p in emp_payslips)
            total_health = sum(p.health for p in emp_payslips)
            total_kup = sum(p.kup_amount for p in emp_payslips)
            total_pit = sum(p.pit_due for p in emp_payslips)
            total_ppk_er = sum(p.ppk_er for p in emp_payslips)

            # Health deductible = 7.75% of health basis (not 9%)
            health_deductible = sum(
                p.health_basis * 0.0775 for p in emp_payslips
            )

            income = total_gross - total_zus_ee - total_kup

            # Find or create PIT-11
            existing = Pit11.search([
                ('employee_id', '=', emp.id),
                ('year', '=', self.year),
            ], limit=1)

            vals = {
                'employee_id': emp.id,
                'company_id': emp.company_id.id,
                'year': self.year,
                'total_gross': total_gross,
                'total_zus_ee': total_zus_ee,
                'total_health': total_health,
                'health_deductible': health_deductible,
                'total_kup': total_kup,
                'total_income': income,
                'total_pit_paid': total_pit,
                'total_ppk_er': total_ppk_er,
                'payslip_count': len(emp_payslips),
                'state': 'draft',
            }

            if existing:
                existing.write(vals)
            else:
                Pit11.create(vals)
                created += 1

        return {
            'type': 'ir.actions.act_window',
            'name': f'PIT-11 za {self.year}',
            'res_model': 'pl.payroll.pit11',
            'view_mode': 'list,form',
            'domain': [('year', '=', self.year)],
        }
```

### 3. Views

- List view: employee, year, total_gross, total_pit_paid, state
- Form view: all fields grouped logically (Section D, E, F, G)
- Wizard form: year field + "Generuj PIT-11" button
- Menu item under Polish Payroll → Raporty → PIT-11

### 4. Security

Add `pl.payroll.pit11` to security CSV with access for payroll_officer and payroll_manager.

### 5. QWeb report (printable)

Create a QWeb template for PIT-11 that can be printed as PDF. This is an internal summary, NOT the official government form (that needs XML schema). Include:
- Header with company NIP and name
- Employee name and PESEL
- Year
- Income summary table
- ZUS summary
- PIT summary
- Footer with generation date

### 6. Tests

Create `tests/test_pit11.py`:

- `test_pit11_generation`: generate PIT-11 for 2025 → verify aggregated amounts match sum of payslips
- `test_pit11_health_deductible`: verify health_deductible = 7.75% of health_basis (not 9%)
- `test_pit11_regeneration`: run wizard twice → same PIT-11 updated, not duplicated
- `test_pit11_ppk_er_included`: PPK employer contribution included in gross income

## Important

- Health deductible in PIT-11 is 7.75% of basis, NOT the full 9% that was actually paid. The remaining 1.25% is non-deductible. This is a common mistake.
- PPK employer contribution counts as income in PIT-11 (it's already included in PIT calculation in our module).
- Do NOT add PESEL field to employee model — it already exists as a standard field in Polish Odoo localization. If missing, skip it in the report.

## Files to create/modify

- CREATE: `l10n_pl_payroll/models/pl_payroll_pit11.py`
- CREATE: `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard.py`
- CREATE: `l10n_pl_payroll/views/pl_payroll_pit11_views.xml`
- CREATE: `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml`
- CREATE: `l10n_pl_payroll/report/pl_payroll_pit11_template.xml`
- CREATE: `l10n_pl_payroll/tests/test_pit11.py`
- CREATE: `l10n_pl_payroll/security/pl_payroll_pit11_security.xml`
- MODIFY: `l10n_pl_payroll/models/__init__.py` (add pit11)
- MODIFY: `l10n_pl_payroll/__init__.py` (add wizard)
- MODIFY: `l10n_pl_payroll/__manifest__.py` (add all new files)
- MODIFY: `l10n_pl_payroll/security/ir.model.access.csv` (add pit11 access)
