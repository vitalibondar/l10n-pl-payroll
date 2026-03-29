# TASK-022: Minimum health contribution basis

**Status:** done
**Branch:** task/022-health-min-basis
**Created:** 2026-03-29
**Depends on:** TASK-019 (needs MINIMUM_WAGE parameter)

## Goal

Polish law requires that health insurance contribution cannot be calculated on a basis lower than the proportional minimum wage (after ZUS deduction). This affects very low earners and part-time employees. Implement this floor.

Write your completion report to `tasks/TASK-022-report.md`.

## Rule

Health contribution basis = max(actual_health_basis, minimum_health_basis)

Where:
- actual_health_basis = gross - ZUS_employee
- minimum_health_basis = minimum_wage × etat_fraction - ZUS_employee_on_minimum

In practice: if someone earns exactly the minimum wage, health basis = minimum_wage - ZUS. If they earn less (shouldn't happen legally, but part-time or short month), the minimum applies.

## What to implement

### 1. Add minimum health basis calculation

In `pl_payroll_payslip.py`:

```python
def _get_minimum_health_basis(self):
    """Minimum basis for health contribution calculation."""
    self.ensure_one()
    try:
        min_wage = self._get_parameter("MINIMUM_WAGE")
    except UserError:
        return Decimal("0.00")
    etat = self._get_etat_fraction()
    min_gross = self._round_amount(min_wage * etat)
    zus_rate = (
        self._get_parameter("ZUS_EMERY_EE")
        + self._get_parameter("ZUS_RENT_EE")
        + self._get_parameter("ZUS_CHOR_EE")
    ) / Decimal("100")
    return self._round_amount(min_gross * (Decimal("1") - zus_rate))
```

### 2. Apply floor in _compute_single_payslip

After calculating `health_basis`:

```python
health_basis = self._round_amount(gross - zus_total_ee)
min_health_basis = self._get_minimum_health_basis()
if health_basis < min_health_basis:
    health_basis = min_health_basis
```

### 3. Tests

Create `tests/test_health_minimum.py`:

- `test_health_basis_at_minimum`: gross = minimum wage → health basis unchanged
- `test_health_basis_below_minimum`: gross < minimum (partial month) → health basis = minimum
- `test_health_basis_above_minimum`: gross > minimum → health basis = gross - ZUS (normal)
- `test_health_basis_part_time_minimum`: 0.5 etat, low gross → minimum is proportional

### 4. No seed changes needed

Existing seed data already has minimum wage workers (4806 PLN). The floor only triggers in edge cases.

## Important

- This depends on TASK-019 for the `MINIMUM_WAGE` parameter and `_get_etat_fraction` method.
- If TASK-019 is not yet merged, Codex should add the parameter and helper locally.
- Does NOT apply to dzieło or zlecenie with student exemption.

## Files to create/modify

- CREATE: `l10n_pl_payroll/tests/test_health_minimum.py`
- MODIFY: `l10n_pl_payroll/models/pl_payroll_payslip.py` (minimum health basis logic)
