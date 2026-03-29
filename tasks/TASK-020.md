# TASK-020: Zwolnienie chorobowe (sick leave pay)

**Status:** done
**Branch:** task/020-sick-leave
**Created:** 2026-03-29
**Depends on:** TASK-019 (needs etat fraction helper)

## Goal

Implement sick leave (zwolnienie chorobowe) — the employer pays 80% of average salary for the first 33 days of illness per calendar year (14 days for employees over 50). After that, ZUS pays zasiłek chorobowy. Our module handles only the employer-paid portion.

Write your completion report to `tasks/TASK-020-report.md`.

## Polish sick leave rules summary

1. **Wynagrodzenie chorobowe** (employer pays, first 33 days/year; 14 days for employees 50+):
   - 80% of average daily salary (calculated from 12 prior months)
   - 100% if illness during pregnancy or caused by work accident
   - Base = average monthly gross from last 12 months minus ZUS employee (13.71%)
   - Daily rate = base / 30
   - Sick days do NOT attract ZUS contributions (neither employee nor employer)
   - Sick days DO attract health insurance and PIT

2. **Zasiłek chorobowy** (ZUS pays, after 33/14 days): OUT OF SCOPE for this module.

3. **Base calculation**:
   - Take gross from last 12 months (or fewer if employed less than 12 months)
   - Subtract ZUS employee contributions (13.71%) from each month
   - Average = sum / number_of_months
   - Daily rate = average / 30
   - Pay = daily_rate × sick_days × percentage (80% or 100%)

## What to implement

### 1. Add sick leave fields to payslip

In `pl_payroll_payslip.py`, add fields:

```python
sick_days = fields.Integer(string="Dni chorobowe (wynagrodzenie)", default=0)
sick_days_100 = fields.Integer(string="Dni chorobowe 100%", default=0,
    help="Ciąża lub wypadek przy pracy")
sick_leave_amount = fields.Float(string="Wynagrodzenie chorobowe", readonly=True)
sick_leave_basis = fields.Float(string="Podstawa chorobowego", readonly=True)
working_days_in_month = fields.Integer(string="Dni robocze w miesiącu", default=0,
    help="Actual working days in month. If 0, treated as full month.")
```

### 2. Implement sick leave calculation

Add method `_compute_sick_leave`:

```python
def _compute_sick_leave(self, gross):
    self.ensure_one()
    sick_80 = self.sick_days or 0
    sick_100 = self.sick_days_100 or 0
    total_sick = sick_80 + sick_100
    if total_sick <= 0:
        return Decimal("0.00"), Decimal("0.00"), gross

    # Calculate base from last 12 months
    basis = self._compute_sick_leave_basis()

    daily_rate = basis / Decimal("30")
    sick_amount = self._round_amount(
        daily_rate * Decimal(str(sick_80)) * Decimal("0.80")
        + daily_rate * Decimal(str(sick_100)) * Decimal("1.00")
    )

    # Reduce gross proportionally for sick days
    # Gross is for working days only; sick leave replaces part of it
    working_days = self.working_days_in_month or 30
    if working_days > 0 and total_sick > 0:
        gross_reduction = self._round_amount(
            gross / Decimal(str(working_days)) * Decimal(str(total_sick))
        )
        adjusted_gross = max(Decimal("0.00"), gross - gross_reduction)
    else:
        adjusted_gross = gross

    return sick_amount, basis, adjusted_gross
```

Add `_compute_sick_leave_basis`:

```python
def _compute_sick_leave_basis(self):
    """Average of (gross - ZUS_EE) from last 12 confirmed payslips."""
    self.ensure_one()
    prior_payslips = self.search([
        ('employee_id', '=', self.employee_id.id),
        ('state', '=', 'confirmed'),
        ('date_from', '<', self.date_from),
    ], order='date_from desc', limit=12)

    if not prior_payslips:
        # No history — use current contract wage minus ZUS
        wage = self._to_decimal(self.contract_id.wage)
        zus_rate = (
            self._get_parameter("ZUS_EMERY_EE")
            + self._get_parameter("ZUS_RENT_EE")
            + self._get_parameter("ZUS_CHOR_EE")
        ) / Decimal("100")
        return self._round_amount(wage * (Decimal("1") - zus_rate))

    total = sum(
        (self._to_decimal(p.gross) - self._to_decimal(p.zus_total_ee)
         for p in prior_payslips),
        Decimal("0.00")
    )
    return self._round_amount(total / Decimal(str(len(prior_payslips))))
```

### 3. Integrate into _compute_single_payslip

In the main computation method, BEFORE ZUS calculation:

```python
# After computing gross:
sick_amount, sick_basis, adjusted_gross = self._compute_sick_leave(gross)

# ZUS is calculated on adjusted_gross (working days portion), NOT on sick_amount
# Use adjusted_gross for ZUS calculation:
zus_cap_basis = self._get_zus_cap_basis(ytd["zus_basis"], adjusted_gross)
# ... ZUS on adjusted_gross only ...

# Sick leave amount is added to health basis and taxable income but NOT to ZUS basis
health_basis = self._round_amount(adjusted_gross - zus_total_ee + sick_amount)
```

Important accounting:
- ZUS employee + employer: calculated on adjusted_gross (excluding sick days)
- Health insurance: calculated on (adjusted_gross - ZUS + sick_amount)
- PIT: calculated on (adjusted_gross - ZUS + sick_amount - KUP)
- Net: adjusted_gross + sick_amount - ZUS - health - PIT - PPK

Store `sick_leave_amount` and `sick_leave_basis` on the payslip.

### 4. Add to payslip form view

Add sick leave fields to the Wynagrodzenie page, after gross and before ZUS:

```xml
<separator string="Zwolnienie chorobowe"/>
<group>
    <field name="sick_days"/>
    <field name="sick_days_100"/>
    <field name="working_days_in_month"/>
    <field name="sick_leave_basis" readonly="1"/>
    <field name="sick_leave_amount" readonly="1"/>
</group>
```

These fields are editable only in draft state, like overtime.

### 5. YTD sick days tracking

Add to `_get_ytd_totals`:

```python
"sick_days_used": sum(
    ((p.sick_days or 0) + (p.sick_days_100 or 0) for p in payslips), 0
),
```

Add computed field to payslip:

```python
ytd_sick_days = fields.Integer(compute="_compute_ytd_sick_days", string="Dni chorobowe (rocznie)")
```

This lets the payroll officer see how many of the 33 days have been used. Display in form view.

### 6. Tests

Create `tests/test_sick_leave.py`:

- `test_sick_leave_80_percent`: 5 sick days at 80% — verify amount = daily_rate × 5 × 0.80
- `test_sick_leave_100_percent`: 3 pregnancy sick days at 100% — verify amount = daily_rate × 3 × 1.00
- `test_sick_leave_no_zus_on_sick_portion`: ZUS only on working days gross, not on sick amount
- `test_sick_leave_health_includes_sick`: health insurance calculated on (adjusted_gross - ZUS + sick_amount)
- `test_sick_leave_basis_from_history`: basis = average of (gross - ZUS) from prior 12 months
- `test_no_sick_days_unchanged`: sick_days=0 → payslip identical to before

### 7. Update seed script

Add sick leave entries for 3-4 payslips in history:
- Tomasz Kowalski: 5 sick days in October 2025
- Anna Wiśniewska: 10 sick days in March 2025
- Ewa Krawczyk: 15 sick days (5 at 100% pregnancy) in July 2025

## Important

- Sick leave does NOT attract ZUS contributions. This is the key difference from normal salary.
- Health insurance IS calculated on sick leave amount.
- PIT IS calculated on sick leave amount.
- PPK is calculated only on the working portion of gross, NOT on sick leave.
- The 33-day limit is per calendar year. After that, ZUS takes over (zasiłek chorobowy) — that's a separate mechanism we don't implement now.
- For employees over 50, the limit is 14 days (not 33). We track this but don't enforce it in this task — just count and display.

## Files to create/modify

- CREATE: `l10n_pl_payroll/tests/test_sick_leave.py`
- MODIFY: `l10n_pl_payroll/models/pl_payroll_payslip.py` (sick leave fields, computation, basis, YTD)
- MODIFY: `l10n_pl_payroll/views/pl_payroll_payslip_views.xml` (sick leave section in form)
- MODIFY: `scripts/seed_realistic_data.py` (add sick leave entries)
