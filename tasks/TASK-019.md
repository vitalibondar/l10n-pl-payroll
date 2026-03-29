# TASK-019: Niepełny etat (part-time employment)

**Status:** done
**Branch:** task/019-part-time
**Created:** 2026-03-29
**Depends on:** none

## Goal

Part-time employees (niepełny etat) have proportional KUP and minimum wage. Currently the module ignores the employment fraction. Fix it.

Write your completion report to `tasks/TASK-019-report.md`.

## Current state

- Odoo `hr.contract` has field `resource_calendar_id` linking to a work schedule
- `resource.calendar` has field `hours_per_week` — e.g., 40.0 for full time, 20.0 for half time
- Our payslip model does NOT use `resource_calendar_id` at all
- KUP standard is always 250 PLN regardless of etat fraction
- No minimum wage enforcement

## What to implement

### 1. Add etat fraction helper

In `pl_payroll_payslip.py`, add method to compute the fraction:

```python
def _get_etat_fraction(self):
    """Return employment fraction (1.0 for full time, 0.5 for half, etc.)."""
    self.ensure_one()
    calendar = self.contract_id.resource_calendar_id
    if not calendar:
        return Decimal("1")
    company_calendar = self.company_id.resource_calendar_id
    if not company_calendar or not company_calendar.hours_per_week:
        return Decimal("1")
    fraction = Decimal(str(calendar.hours_per_week)) / Decimal(str(company_calendar.hours_per_week))
    return min(fraction, Decimal("1"))  # cap at 1.0
```

### 2. Proportional KUP standard

In `_compute_kup_amount`, when `kup_type == "standard"`:

```python
# Current:
return self._round_amount(self._get_parameter("KUP_STANDARD"))

# New:
kup_full = self._get_parameter("KUP_STANDARD")
etat = self._get_etat_fraction()
return self._round_amount(kup_full * etat)
```

Note: autorskie KUP is NOT proportional (it's % of actual income). Only standard KUP 250 PLN is proportional.

### 3. Add payroll parameter: MINIMUM_WAGE

Add to `l10n_pl_payroll/data/pl_payroll_parameter_data.xml`:

```xml
<record id="param_minimum_wage_2025" model="pl.payroll.parameter">
    <field name="code">MINIMUM_WAGE</field>
    <field name="name">Minimalne wynagrodzenie</field>
    <field name="value">4666</field>
    <field name="date_from">2025-01-01</field>
    <field name="date_to">2025-06-30</field>
</record>
<record id="param_minimum_wage_2025h2" model="pl.payroll.parameter">
    <field name="code">MINIMUM_WAGE</field>
    <field name="name">Minimalne wynagrodzenie</field>
    <field name="value">4666</field>
    <field name="date_from">2025-07-01</field>
    <field name="date_to">2025-12-31</field>
</record>
<record id="param_minimum_wage_2026" model="pl.payroll.parameter">
    <field name="code">MINIMUM_WAGE</field>
    <field name="name">Minimalne wynagrodzenie</field>
    <field name="value">4806</field>
    <field name="date_from">2026-01-01</field>
    <field name="date_to">2026-12-31</field>
</record>
```

### 4. Minimum wage validation

In `_compute_single_payslip`, after calculating gross, add a warning (not a block — employer might have a valid reason):

```python
etat = self._get_etat_fraction()
try:
    min_wage = self._get_parameter("MINIMUM_WAGE")
    min_wage_proportional = self._round_amount(min_wage * etat)
    if gross < min_wage_proportional:
        # Store warning flag but don't block
        pass  # We'll use a computed field for this
except UserError:
    pass  # Parameter missing, skip validation
```

Add a computed boolean field `below_minimum_wage` to the payslip model:

```python
below_minimum_wage = fields.Boolean(compute="_compute_minimum_wage_warning", store=True)
```

Display it as a warning banner in the form view.

### 5. Display etat fraction on payslip form

Add a related field for visibility:

```python
etat_fraction = fields.Float(compute="_compute_etat_fraction", string="Wymiar etatu")
```

Show it in the payslip form header or Wynagrodzenie page.

### 6. Tests

Create `tests/test_part_time.py`:

- `test_half_time_kup_proportional`: 0.5 etat → KUP = 125 PLN (not 250)
- `test_full_time_kup_unchanged`: 1.0 etat → KUP = 250 PLN
- `test_autorskie_kup_not_proportional`: autorskie KUP with 0.5 etat → KUP based on actual income, NOT halved
- `test_below_minimum_wage_warning`: gross below proportional minimum → `below_minimum_wage = True`
- `test_no_calendar_defaults_full`: no work schedule set → treated as full time

### 7. Update seed script

In `scripts/seed_realistic_data.py`, modify 1-2 existing employees to have part-time schedules (e.g., Natalia Ivanchuk 0.5 etat, Yuliia Kravchuk 0.75 etat). This requires:
1. Creating `resource.calendar` records for 20h/week and 30h/week
2. Assigning them to contracts via `resource_calendar_id`

## Important

- KUP standard 250 PLN is proportional to etat. KUP autorskie is NOT.
- KUP standard_20 (20% of income) — NOT proportional either (it's already % of actual income).
- Minimum wage in Poland changes: 4666 PLN (2025), 4806 PLN (2026). Use parameters.
- A 0.5 etat employee earning 2403 PLN gross is legal (half of 4806).

## Files to create/modify

- CREATE: `l10n_pl_payroll/tests/test_part_time.py`
- MODIFY: `l10n_pl_payroll/models/pl_payroll_payslip.py` (etat fraction, proportional KUP, minimum wage warning)
- MODIFY: `l10n_pl_payroll/data/pl_payroll_parameter_data.xml` (MINIMUM_WAGE params)
- MODIFY: `l10n_pl_payroll/views/pl_payroll_payslip_views.xml` (show etat fraction, warning)
- MODIFY: `scripts/seed_realistic_data.py` (part-time employees)
