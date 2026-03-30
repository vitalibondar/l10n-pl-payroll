# TASK-041: Batch wizard for adding components to multiple payslips

**Status:** done
**Phase:** 6 — Component Constructor
**Depends on:** TASK-039
**Architecture:** ARCHITECTURE-PHASE6.md § 4, Mode B

## What

Transient model `pl.payroll.component.batch.wizard` — a wizard that lets the accountant add a component (e.g., "ekwiwalent za pranie 150 PLN") to ALL selected employees in one action.

## Model: `wizard/pl_payroll_component_batch_wizard.py`

```
Fields:
- component_type_id (Many2one, required)
- amount (Float, required)
- date_from (Date, required) — first day of target month
- date_to (Date, required) — last day of target month
- employee_ids (Many2many hr.employee)
- all_active_employees (Boolean)
- department_id (Many2one hr.department) — filter employees by department
- note (Text)
```

### Logic: `action_apply()`

1. Determine employee list (explicit selection OR all active with open contracts)
2. For each employee:
   a. Find existing draft payslip for the period
   b. If not found: create new payslip (employee + contract + dates)
   c. Add payslip line with component_type, amount, PIT/ZUS flags from type
3. Return action to show affected payslips

### View: `wizard/pl_payroll_component_batch_wizard_views.xml`

Form wizard with:
- Component type selector
- Amount
- Period (date_from, date_to)
- Employee selection (many2many_tags or list)
- "All active" checkbox
- Department filter
- Apply button

### Menu access

Płace → Narzędzia → Dodaj składnik zbiorczy

Also accessible from payslip list view as server action.

## Don't

- Don't auto-compute payslips after adding lines (user triggers compute manually)
- Don't create confirmed payslips — always draft
