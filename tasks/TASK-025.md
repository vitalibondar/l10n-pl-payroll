# TASK-025: Vacation pay (wynagrodzenie za urlop)

**Status:** done
**Branch:** task/025-vacation-pay
**Created:** 2026-03-29
**Depends on:** TASK-019 (etat fraction)

## Goal

Implement vacation pay calculation. In Poland, vacation pay equals the employee's average salary including variable components (bonuses, overtime) from the last 3 or 12 months. For employees with fixed salary only, vacation pay = regular salary (no difference). But for those with variable components, the calculation differs.

Write your completion report to `tasks/TASK-025-report.md`.

## Polish rules

1. **Fixed salary only**: vacation pay = regular monthly salary. No special calculation needed.
2. **Variable components** (overtime, bonuses): average from last 3 months (if components don't change much) or 12 months (if they fluctuate significantly). Our module uses 3 months as default.
3. **Formula**: sum of variable components from last 3 months / sum of hours worked in those months × hours of vacation taken.
4. **Ekwiwalent za urlop** (vacation equivalent on termination): calculated differently — uses a coefficient published by GUS each year.

## What to implement

### 1. Add vacation fields to payslip

```python
vacation_days = fields.Float(string="Dni urlopowe", default=0)
vacation_pay = fields.Float(string="Wynagrodzenie za urlop", readonly=True)
```

### 2. Vacation pay calculation

Add `_compute_vacation_pay`:

```python
def _compute_vacation_pay(self, base_gross):
    self.ensure_one()
    vacation_days = self._to_decimal(self.vacation_days or 0)
    if vacation_days <= Decimal("0"):
        return Decimal("0.00"), base_gross

    # Check if employee has variable components in recent months
    prior_payslips = self.search([
        ('employee_id', '=', self.employee_id.id),
        ('state', '=', 'confirmed'),
        ('date_from', '<', self.date_from),
    ], order='date_from desc', limit=3)

    total_variable = sum(
        p.overtime_amount + p.bonus_gross_total
        for p in prior_payslips
    )

    if total_variable == 0 or not prior_payslips:
        # Fixed salary only — vacation pay = regular pay portion
        # No adjustment needed, gross stays the same
        return Decimal("0.00"), base_gross

    # Variable components: calculate average
    total_hours_worked = Decimal("0")
    total_variable_dec = Decimal("0")
    standard_hours = self._get_parameter("STANDARD_MONTHLY_HOURS")

    for p in prior_payslips:
        variable = self._to_decimal(p.overtime_amount) + self._to_decimal(p.bonus_gross_total)
        total_variable_dec += variable
        # Approximate hours worked (full month minus any sick/vacation in that month)
        total_hours_worked += standard_hours

    if total_hours_worked <= Decimal("0"):
        return Decimal("0.00"), base_gross

    hourly_variable_rate = total_variable_dec / total_hours_worked
    vacation_hours = vacation_days * Decimal("8")  # standard 8h day
    vacation_variable_supplement = self._round_amount(hourly_variable_rate * vacation_hours)

    return vacation_variable_supplement, base_gross
```

### 3. Integrate into gross calculation

In `_compute_single_payslip`, after overtime:

```python
vacation_supplement, base_gross_adj = self._compute_vacation_pay(base_gross)
# Add vacation supplement to gross
gross = self._round_amount(base_gross + overtime_amount + vacation_supplement + bonus_gross_total - deduction_gross_total)
```

Store `vacation_pay` field.

### 4. Add to payslip form

Add vacation_days (editable in draft) and vacation_pay (readonly) to the Wynagrodzenie page.

### 5. Tests

Create `tests/test_vacation_pay.py`:

- `test_fixed_salary_no_supplement`: no overtime/bonuses in history → vacation_pay = 0
- `test_variable_supplement_calculated`: overtime in prior months → supplement > 0
- `test_zero_vacation_days_no_effect`: vacation_days = 0 → no change

### 6. Seed data

Add vacation_days to 2-3 payslips in seed data.

## Important

- For most Om Energy production workers with fixed salary and no regular bonuses, vacation pay = regular pay. The supplement only applies when there are variable components.
- This task handles the simple case. Full ekwiwalent za urlop (termination equivalent) is deferred.
- Vacation days are entered manually by the payroll officer (integration with leave management is a separate feature).

## Files to create/modify

- CREATE: `l10n_pl_payroll/tests/test_vacation_pay.py`
- MODIFY: `l10n_pl_payroll/models/pl_payroll_payslip.py`
- MODIFY: `l10n_pl_payroll/views/pl_payroll_payslip_views.xml`
- MODIFY: `scripts/seed_realistic_data.py`
