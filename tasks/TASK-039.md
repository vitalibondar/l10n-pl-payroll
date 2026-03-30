# TASK-039: Extend pl.payroll.payslip.line with component type + PIT/ZUS flags

**Status:** ready
**Phase:** 6 — Component Constructor
**Depends on:** TASK-038
**Architecture:** ARCHITECTURE-PHASE6.md § 2

## What

Add `component_type_id` field to payslip lines. When user selects a component type, auto-fill name, category, pit_taxable, zus_included from the type. Flags are overridable per line.

## Deliverables

### 1. Modify `models/pl_payroll_payslip_line.py`

New fields:
- `component_type_id` (Many2one to pl.payroll.component.type, optional)
- `pit_taxable` (Boolean, default=True)
- `zus_included` (Boolean, default=True)

New onchange:
- `_onchange_component_type`: when type selected → set name, category, pit_taxable, zus_included, amount (if default_amount > 0)

### 2. Modify `views/pl_payroll_payslip_views.xml`

In the "Składniki dodatkowe" tab, update the inline list:
```xml
<field name="component_type_id"/>
<field name="name"/>
<field name="category"/>
<field name="amount"/>
<field name="pit_taxable" widget="boolean_toggle"/>
<field name="zus_included" widget="boolean_toggle"/>
<field name="note"/>
```

### 3. Update computed totals

Modify `_compute_payslip_line_totals` on payslip to also compute:
- `pit_taxable_bonus_total` — sum of bonus_gross lines where pit_taxable=True
- `zus_included_bonus_total` — sum of bonus_gross lines where zus_included=True
- `benefit_in_kind_total` — sum of benefit_in_kind lines
- `benefit_in_kind_pit` — sum of benefit_in_kind where pit_taxable=True
- `benefit_in_kind_zus` — sum of benefit_in_kind where zus_included=True (respecting zus_exempt_limit)

Add these as computed stored fields on payslip.

### 4. Backward compatibility

- `component_type_id` is NOT required
- Lines without type: pit_taxable=True, zus_included=True (same as current behavior)
- Existing payslip lines in DB don't break

## Don't

- Don't modify the salary computation engine yet (TASK-040)
- Don't add benefit_in_kind to category selection on the OLD payslip.line yet — add it as part of this task (extend the selection field)
