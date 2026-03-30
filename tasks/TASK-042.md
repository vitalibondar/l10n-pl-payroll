# TASK-042: Grid list view for batch editing + menu

**Status:** ready
**Phase:** 6 — Component Constructor
**Depends on:** —
**Architecture:** ARCHITECTURE-PHASE6.md § 4, Mode C

## What

Create a dedicated list view of payslips that shows ALL key editable fields as columns, with `multi_edit="1"` for spreadsheet-like batch editing. Accountant opens this view, sees all employees for the month in one table, edits any field.

## Deliverables

### 1. New list view in `views/pl_payroll_payslip_views.xml`

```xml
<record id="view_pl_payroll_payslip_grid" model="ir.ui.view">
    <field name="name">pl.payroll.payslip.grid</field>
    <field name="model">pl.payroll.payslip</field>
    <field name="arch" type="xml">
        <list editable="inline" multi_edit="1" default_order="employee_id">
            <field name="employee_id" readonly="1"/>
            <field name="department_id" readonly="1" optional="show"/>
            <field name="contract_id" readonly="1" optional="hide"/>
            <field name="date_from" readonly="1" column_invisible="1"/>
            <field name="working_days_in_month"/>
            <field name="overtime_hours_150"/>
            <field name="overtime_hours_200"/>
            <field name="overtime_amount" readonly="1" optional="hide"/>
            <field name="sick_days"/>
            <field name="sick_days_100"/>
            <field name="vacation_days"/>
            <field name="gross" readonly="1"/>
            <field name="zus_total_ee" readonly="1" optional="hide"/>
            <field name="pit_due" readonly="1" optional="hide"/>
            <field name="bonus_gross_total" readonly="1" optional="show"/>
            <field name="deduction_net_total" readonly="1" optional="show"/>
            <field name="net" readonly="1"/>
            <field name="state" widget="badge" readonly="1"/>
        </list>
    </field>
</record>
```

### 2. New action + menu

Action: `action_pl_payroll_payslip_grid` — opens the grid view filtered to current month's draft payslips.

Default filter: current month + state = draft.

Menu: Płace → Edycja zbiorcza

### 3. "Oblicz zaznaczone" server action

Server action bound to the grid list view — select rows, click "Oblicz zaznaczone" → calls `action_compute()` on selected payslips.

### 4. "Zatwierdź zaznaczone" server action

Already exists (`action_server_pl_payroll_batch_confirm`), verify it works from grid view too.

## Notes

- `multi_edit="1"` is an Odoo 17+ feature. Verify it works in Odoo 18.
- Fields that shouldn't be editable for confirmed payslips: handled by existing `readonly="state != 'draft'"` logic in the model (attrs on form). For list view, may need `readonly` attribute or `decoration-*` to show confirmed rows as non-editable.
- Consider: add `<control>` section for creating new payslips directly from grid?

## Don't

- Don't build a custom JS widget — use native Odoo list view capabilities
- Don't duplicate the existing list view — this is a SEPARATE view with different columns
