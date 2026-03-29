# TASK-024: ZUS DRA monthly declaration generation

**Status:** pending
**Branch:** task/024-zus-dra
**Created:** 2026-03-29
**Depends on:** none

## Goal

Generate ZUS DRA (Deklaracja rozliczeniowa) monthly declaration — the employer's monthly summary of all ZUS contributions for all employees. This is what gets submitted to ZUS via Płatnik or ePłatnik.

For now: generate as a data model + printable summary report. Official KEDU XML export is a later task.

Write your completion report to `tasks/TASK-024-report.md`.

## What ZUS DRA contains

A monthly declaration summarizing per-employee and total:
- Emerytalne (employee + employer portions)
- Rentowe (employee + employer)
- Chorobowe (employee only)
- Wypadkowe (employer only)
- Zdrowotne (health)
- FP (employer)
- FGŚP (employer)
- Number of insured employees

## What to implement

### 1. Create ZUS DRA model

Create `l10n_pl_payroll/models/pl_payroll_zus_dra.py`:

```python
class PlPayrollZusDra(models.Model):
    _name = "pl.payroll.zus.dra"
    _description = "ZUS DRA Monthly Declaration"
    _order = "year desc, month desc"

    company_id = fields.Many2one("res.company", required=True)
    year = fields.Integer(required=True)
    month = fields.Integer(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft')

    # Totals
    employee_count = fields.Integer(readonly=True)
    payslip_count = fields.Integer(readonly=True)

    total_emerytalne_ee = fields.Float(readonly=True)
    total_emerytalne_er = fields.Float(readonly=True)
    total_rentowe_ee = fields.Float(readonly=True)
    total_rentowe_er = fields.Float(readonly=True)
    total_chorobowe = fields.Float(readonly=True)
    total_wypadkowe = fields.Float(readonly=True)
    total_health = fields.Float(readonly=True)
    total_fp = fields.Float(readonly=True)
    total_fgsp = fields.Float(readonly=True)

    total_zus_employee = fields.Float(readonly=True, string="ZUS EE łącznie")
    total_zus_employer = fields.Float(readonly=True, string="ZUS ER łącznie")
    total_all = fields.Float(readonly=True, string="Suma do zapłaty")

    line_ids = fields.One2many("pl.payroll.zus.dra.line", "dra_id")
```

### 2. Create DRA Line model (per employee)

```python
class PlPayrollZusDraLine(models.Model):
    _name = "pl.payroll.zus.dra.line"
    _description = "ZUS DRA Line (per employee)"

    dra_id = fields.Many2one("pl.payroll.zus.dra", ondelete="cascade")
    employee_id = fields.Many2one("hr.employee")
    payslip_id = fields.Many2one("pl.payroll.payslip")

    gross = fields.Float()
    emerytalne_ee = fields.Float()
    emerytalne_er = fields.Float()
    rentowe_ee = fields.Float()
    rentowe_er = fields.Float()
    chorobowe = fields.Float()
    wypadkowe = fields.Float()
    health = fields.Float()
    fp = fields.Float()
    fgsp = fields.Float()
```

### 3. Generation wizard

`wizard/pl_payroll_zus_dra_wizard.py`:

Takes year + month, finds all confirmed payslips for that period, creates DRA with lines.

### 4. Views

- DRA list: month/year, employee_count, total_all, state
- DRA form: header totals + embedded list of per-employee lines
- Wizard: year + month fields + "Generuj DRA" button
- Menu: Polish Payroll → Raporty → ZUS DRA

### 5. Security

Add models to security CSV.

### 6. Tests

Create `tests/test_zus_dra.py`:

- `test_dra_totals_match_payslips`: sum of DRA lines = sum of individual payslip ZUS fields
- `test_dra_employee_count`: employee_count = distinct employees in payslips
- `test_dra_regeneration`: running wizard twice updates, doesn't duplicate
- `test_dra_student_excluded`: student zlecenie employee has zero ZUS in DRA line

## Files to create/modify

- CREATE: `l10n_pl_payroll/models/pl_payroll_zus_dra.py`
- CREATE: `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard.py`
- CREATE: `l10n_pl_payroll/views/pl_payroll_zus_dra_views.xml`
- CREATE: `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml`
- CREATE: `l10n_pl_payroll/tests/test_zus_dra.py`
- MODIFY: `l10n_pl_payroll/models/__init__.py`
- MODIFY: `l10n_pl_payroll/__init__.py` (wizard)
- MODIFY: `l10n_pl_payroll/__manifest__.py`
- MODIFY: `l10n_pl_payroll/security/ir.model.access.csv`
