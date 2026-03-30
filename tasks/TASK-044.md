# TASK-044: UI — move NET to right side, update form layout

**Status:** done
**Phase:** 6 — Component Constructor
**Depends on:** —
**Architecture:** ARCHITECTURE-PHASE6.md § UI changes

## What

Vitalik's feedback: NET amount should be on the RIGHT side of the payslip form (prominent, eye-catching). LEFT side should have accountant working fields (employee, contract, dates, overtime, etc.).

## Changes to `views/pl_payroll_payslip_views.xml`

### Current layout (top of form)
```
[NET big]                    ← LEFT (oe_title)
[employee] [state]  [gross]
[contract] [name]   [cost]
[dates]    [dept]
```

### New layout
```
[employee] [state]          [NET big]  ← RIGHT
[contract] [name]           [gross]
[dates]    [dept]           [cost]
```

Implementation: Move the `oe_title` block with NET to a right-aligned `div` or use Odoo's `oe_right` class. The `<group col="3">` stays but the big NET moves to the third group or uses `oe_button_box` area trick.

### Approach
```xml
<sheet>
    <!-- Alerts stay at top -->
    <div class="oe_button_box" name="button_box">
        <!-- Future buttons go here -->
    </div>
    <div class="oe_title oe_right">
        <label for="net"/>
        <h1>
            <field name="net" readonly="1"/>
            <span class="text-muted">PLN</span>
        </h1>
    </div>
    <group col="2">
        <group string="Pracownik i umowa">
            <field name="employee_id"/>
            <field name="contract_id"/>
            <field name="date_from"/>
            <field name="date_to"/>
        </group>
        <group string="Info">
            <field name="state"/>
            <field name="name"/>
            <field name="department_id"/>
            <field name="gross"/>
            <field name="total_employer_cost"/>
        </group>
    </group>
    <!-- ... notebook tabs ... -->
</sheet>
```

## Don't

- Don't change any business logic
- Don't change field order in notebook tabs
- Don't change the list view (only form view)
