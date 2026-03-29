# TASK-018: Student on zlecenie — ZUS exemption

**Status:** done
**Branch:** task/018-student-zus-exemption
**Created:** 2026-03-29
**Depends on:** none

## Goal

Students under 26 on umowa zlecenie are fully exempt from ALL ZUS contributions (both employee and employer side). This is a fundamental Polish payroll rule. Implement it.

Write your completion report to `tasks/TASK-018-report.md`.

## Current state

- `hr.contract` has field `ulga_type` (selection) — handles PIT exemptions but NOT ZUS exemptions
- `pl.payroll.payslip._compute_single_payslip()` always computes ZUS regardless of student status
- `pl.payroll.payslip._is_mandate_contract()` detects umowa zlecenie
- There is NO `is_student` or `birthday` field on `hr.employee`

## What to implement

### 1. Add fields to hr.employee

In `l10n_pl_payroll/models/hr_employee.py` (CREATE this file — it doesn't exist yet):

```python
from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_student = fields.Boolean(default=False, string="Student / uczeń")
```

Note: `birthday` field already exists on `hr.employee` in base Odoo (it's a standard field). Do NOT create it. Just use `self.employee_id.birthday`.

### 2. Register the new model file

Add `'models/hr_employee.py'` to `__init__.py` in models folder.

### 3. Add helper method to payslip

In `pl_payroll_payslip.py`, add method:

```python
def _is_student_zlecenie_exempt(self):
    """Student under 26 on umowa zlecenie = no ZUS at all."""
    self.ensure_one()
    if not self._is_mandate_contract():
        return False
    if not self.employee_id.is_student:
        return False
    # Check age at payslip date
    birthday = self.employee_id.birthday
    if not birthday:
        return False
    payslip_date = fields.Date.to_date(self.date_from)
    age = (payslip_date - birthday).days / 365.25
    return age < 26
```

### 4. Modify _compute_single_payslip

In the ZUS calculation block (lines ~154-157), wrap with exemption check:

```python
if self._is_student_zlecenie_exempt():
    zus_emerytalne_ee = Decimal("0.00")
    zus_rentowe_ee = Decimal("0.00")
    zus_chorobowe_ee = Decimal("0.00")
    zus_total_ee = Decimal("0.00")
else:
    zus_emerytalne_ee = self._percent_of_amount(zus_cap_basis, "ZUS_EMERY_EE")
    zus_rentowe_ee = self._percent_of_amount(zus_cap_basis, "ZUS_RENT_EE")
    zus_chorobowe_ee = self._percent_of_gross(gross, "ZUS_CHOR_EE")
    zus_total_ee = self._round_amount(zus_emerytalne_ee + zus_rentowe_ee + zus_chorobowe_ee)
```

Same for employer-side ZUS (lines ~174-178):

```python
if self._is_student_zlecenie_exempt():
    zus_emerytalne_er = Decimal("0.00")
    zus_rentowe_er = Decimal("0.00")
    zus_wypadkowe_er = Decimal("0.00")
    zus_fp = Decimal("0.00")
    zus_fgsp = Decimal("0.00")
else:
    zus_emerytalne_er = self._percent_of_amount(zus_cap_basis, "ZUS_EMERY_ER")
    # ... existing code
```

### 5. Add view for is_student field

In `views/pl_payroll_employee_views.xml` (CREATE this file), add `is_student` checkbox to employee form. Use `xpath` to inherit `hr.view_employee_form`:

```xml
<record id="view_employee_form_inherit_pl_payroll" model="ir.ui.view">
    <field name="name">hr.employee.form.inherit.pl.payroll</field>
    <field name="model">hr.employee</field>
    <field name="inherit_id" ref="hr.view_employee_form"/>
    <field name="arch" type="xml">
        <xpath expr="//group[@name='identification_group']" position="inside">
            <field name="is_student"/>
        </xpath>
    </field>
</record>
```

Register this view in `__manifest__.py` data list.

### 6. Tests

Create `tests/test_student_exemption.py`:

- `test_student_zlecenie_no_zus`: student under 26 on zlecenie → all ZUS = 0, health = 0, only PIT calculated
- `test_student_praca_normal_zus`: student under 26 on umowa o pracę → ZUS calculated normally (exemption only for zlecenie!)
- `test_non_student_zlecenie_normal_zus`: non-student on zlecenie → normal ZUS
- `test_student_turns_26_mid_year`: student turns 26 mid-year → exemption stops from that month

### 7. Update seed script

In `scripts/seed_realistic_data.py`, add 2 student employees (e.g., Jakub Wiśniewski, 22, and Oliwia Kowalska, 24) on umowa zlecenie with `is_student=True`. Generate payslips for them. Verify ZUS = 0.

## Important

- On umowa o pracę, student status does NOT exempt from ZUS. Only zlecenie.
- Health insurance also exempted for student on zlecenie (because health is calculated on post-ZUS basis, and if no ZUS... actually: student on zlecenie has NO health insurance from employer at all).
- The exemption ends the day the student turns 26 OR loses student status, whichever comes first.
- `birthday` in Odoo is `fields.Date` on `hr.employee` — might be stored as `birthday` or `birthday`. Check with `fields_get` if unsure.

## Files to create/modify

- CREATE: `l10n_pl_payroll/models/hr_employee.py`
- CREATE: `l10n_pl_payroll/views/pl_payroll_employee_views.xml`
- CREATE: `l10n_pl_payroll/tests/test_student_exemption.py`
- MODIFY: `l10n_pl_payroll/models/__init__.py` (add hr_employee import)
- MODIFY: `l10n_pl_payroll/models/pl_payroll_payslip.py` (ZUS exemption logic)
- MODIFY: `l10n_pl_payroll/__manifest__.py` (add employee view XML)
- MODIFY: `scripts/seed_realistic_data.py` (add 2 student employees)
