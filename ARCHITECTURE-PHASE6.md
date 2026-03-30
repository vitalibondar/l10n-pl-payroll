# Phase 6: Payroll Component Constructor — Architecture

> This document defines the architecture for 4 features requested by Vitalik (2026-03-30).
> Must be approved before coding begins.

## Overview

Four interconnected features:
1. **Component Constructor** — user-definable payroll component types with PIT/ZUS rules
2. **Extended payslip lines** — component type reference + PIT/ZUS flags on each line
3. **Batch editing** — three editing modes (individual, batch wizard, grid view)
4. **hr_attendance overtime sync** — pull overtime hours from attendance module

---

## 1. Component Constructor: `pl.payroll.component.type`

### Problem
Current `pl.payroll.payslip.line` has 3 hardcoded categories (bonus_gross, deduction_gross, deduction_net) with no PIT/ZUS exemption logic. ALL lines are treated as fully taxable. This blocks:
- Ekwiwalent za pranie (PIT-exempt, ZUS-exempt)
- Finansowanie posiłków (PIT-taxable, ZUS-exempt up to 450 PLN)
- Posiłki profilaktyczne (PIT-exempt, ZUS-exempt)
- Karty sportowe, dofinansowanie dojazdów, etc.

### Model: `pl.payroll.component.type`

```python
class PlPayrollComponentType(models.Model):
    _name = "pl.payroll.component.type"
    _description = "Typ składnika wynagrodzenia"
    _order = "sequence, name"

    name = fields.Char(required=True)               # e.g. "Ekwiwalent za pranie"
    code = fields.Char(required=True, unique=True)   # e.g. "PRANIE", "POSILKI"
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Category: what does this component do to the payslip?
    category = fields.Selection([
        ("bonus_gross", "Dodatek brutto"),            # adds to gross
        ("deduction_gross", "Potrącenie brutto"),      # subtracts from gross
        ("benefit_in_kind", "Świadczenie rzeczowe"),   # adds to PIT/ZUS base but not to cash
        ("deduction_net", "Potrącenie netto"),          # subtracts from net
    ], required=True)

    # --- Tax rules ---
    pit_taxable = fields.Boolean(
        string="Podlega PIT",
        default=True,
        help="Czy wartość tego składnika wchodzi do podstawy opodatkowania PIT?",
    )
    pit_exempt_article = fields.Char(
        string="Podstawa prawna zwolnienia PIT",
        help="Np. 'art. 21 ust. 1 pkt 11 ustawy o PIT'",
    )

    # --- ZUS rules ---
    zus_included = fields.Boolean(
        string="Podlega składkom ZUS",
        default=True,
        help="Czy wartość tego składnika wchodzi do podstawy wymiaru składek ZUS?",
    )
    zus_exempt_limit = fields.Float(
        string="Limit zwolnienia ZUS (PLN/mies.)",
        default=0.0,
        help="Kwota zwolniona ze składek ZUS miesięcznie. 0 = brak limitu (pełne zwolnienie jeśli zus_included=False).",
    )
    zus_exempt_article = fields.Char(
        string="Podstawa prawna zwolnienia ZUS",
        help="Np. '§ 2 ust. 1 pkt 11 rozp. składkowego'",
    )

    # --- Defaults & behavior ---
    default_amount = fields.Float(
        string="Domyślna kwota",
        help="Podpowiadana kwota przy dodawaniu składnika do listy płac.",
    )
    requires_documentation = fields.Boolean(
        string="Wymaga dokumentacji",
        help="Np. ekwiwalent za pranie wymaga kalkulacji kosztów rzeczywistych.",
    )
    documentation_hint = fields.Char(
        string="Podpowiedź dokumentacji",
        help="Wyświetlana jako hint w polu 'note' na linii payslip.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        default=lambda self: self.env.company,
        help="Puste = dostępny dla wszystkich firm.",
    )

    note = fields.Text(string="Opis / uwagi prawne")
```

### Pre-seeded types (data XML)
Shipped with the module as `noupdate="0"` (updatable):

| code | name | category | pit_taxable | zus_included | zus_exempt_limit |
|------|------|----------|------------|-------------|-----------------|
| PREMIA | Premia | bonus_gross | True | True | 0 |
| PRANIE | Ekwiwalent za pranie | bonus_gross | False | False | 0 |
| POSILKI_FIN | Finansowanie posiłków | benefit_in_kind | True | False | 450.0 |
| POSILKI_PROF | Posiłki profilaktyczne | benefit_in_kind | False | False | 0 |
| KARTA_SPORT | Karta sportowa | benefit_in_kind | True | True | 0 |
| POTRACENIE_KOMORNICZE | Potrącenie komornicze | deduction_net | False | False | 0 |
| NADGODZINY_ATT | Nadgodziny z ewidencji | bonus_gross | True | True | 0 |

These are EXAMPLES. Users create their own types through the UI. That's the whole point of the constructor.

---

## 2. Extended `pl.payroll.payslip.line`

### Changes to existing model

```python
class PlPayrollPayslipLine(models.Model):
    _inherit = "pl.payroll.payslip.line"  # or modify existing

    component_type_id = fields.Many2one(
        "pl.payroll.component.type",
        string="Typ składnika",
        help="Typ składnika determinuje zasady PIT i ZUS.",
    )

    # Copied from component_type on create/change, but OVERRIDABLE per line
    pit_taxable = fields.Boolean(
        string="Podlega PIT",
        default=True,
    )
    zus_included = fields.Boolean(
        string="Podlega ZUS",
        default=True,
    )

    @api.onchange("component_type_id")
    def _onchange_component_type(self):
        if self.component_type_id:
            ct = self.component_type_id
            self.name = ct.name
            self.category = ct.category
            self.pit_taxable = ct.pit_taxable
            self.zus_included = ct.zus_included
            if ct.default_amount:
                self.amount = ct.default_amount
```

### Backward compatibility
- `component_type_id` is optional (not required)
- Lines without a type behave as before (pit_taxable=True, zus_included=True)
- Existing lines in DB keep working — migration not needed

---

## 3. Updated salary computation engine

### Current flow (simplified)
```
gross = base_wage + overtime + vacation + bonus_gross_total - deduction_gross_total
→ ZUS on gross
→ Health on (gross - ZUS)
→ KUP
→ PIT on (health_basis - KUP + PPK_ER)
→ net = gross - ZUS - health - PIT - PPK_EE - deduction_net_total
```

### New flow
```
# Step 1: Categorize payslip lines by PIT/ZUS flags
pit_taxable_bonus = sum of lines where category=bonus_gross AND pit_taxable=True
pit_exempt_bonus = sum of lines where category=bonus_gross AND pit_taxable=False
zus_taxable_bonus = sum of lines where category=bonus_gross AND zus_included=True
zus_exempt_bonus = sum of lines where category=bonus_gross AND zus_included=False

benefit_in_kind_pit = sum of benefit_in_kind lines where pit_taxable=True
benefit_in_kind_zus = sum of benefit_in_kind lines where zus_included=True
# ZUS exempt limit handling: if type has zus_exempt_limit > 0,
# only the excess above limit enters ZUS basis

# Step 2: Compute gross (cash)
gross = base_wage + overtime + vacation + ALL bonus_gross - ALL deduction_gross
# (gross stays the same — all bonuses and deductions affect cash)

# Step 3: Compute ZUS basis
zus_basis = base_wage + overtime + vacation + zus_taxable_bonus - zus_deduction_gross + benefit_in_kind_zus
# Apply ZUS exempt limits per component type

# Step 4: ZUS on zus_basis (not on gross!)
# ... rest stays similar but uses zus_basis instead of gross for ZUS

# Step 5: Compute PIT basis
health_basis = zus_basis - zus_total_ee  # only ZUS-included part
pit_basis = health_basis - KUP + PPK_ER + benefit_in_kind_pit
# Add PIT-taxable benefits-in-kind to PIT basis

# Step 6: PIT, net as before but using correct bases
```

### Key insight
**Gross** (what appears on payslip as brutto) = total cash including all bonuses.
**ZUS basis** and **PIT basis** may differ from gross because some components are exempt.

### New computed fields on payslip
```python
zus_basis = fields.Float("Podstawa wymiaru składek ZUS")
pit_basis = fields.Float("Podstawa opodatkowania PIT")
benefit_in_kind_total = fields.Float("Świadczenia rzeczowe razem")
```

---

## 4. Three editing modes

### Mode A: Individual (current)
Payslip form → tab "Składniki dodatkowe" → inline editable list.
**Change**: add `component_type_id` dropdown to the inline list. Selecting a type auto-fills name, category, PIT/ZUS flags.

### Mode B: Batch wizard
**Model**: `pl.payroll.component.batch.wizard`

Flow:
1. User selects component type from dropdown
2. Sets amount
3. Selects employees (or "all active" checkbox)
4. Selects period (month/year)
5. Clicks "Dodaj składnik"
6. Wizard finds or creates payslip for each employee+period, adds the line

```python
class PlPayrollComponentBatchWizard(models.TransientModel):
    _name = "pl.payroll.component.batch.wizard"

    component_type_id = fields.Many2one("pl.payroll.component.type", required=True)
    amount = fields.Float(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    employee_ids = fields.Many2many("hr.employee")
    all_active = fields.Boolean("Wszyscy aktywni pracownicy")
    note = fields.Text()

    def action_apply(self):
        # For each employee: find/create payslip, add line
        ...
```

### Mode C: Grid view (spreadsheet-like)
This is the most complex. Odoo 18 does NOT have a native spreadsheet grid widget for arbitrary editing. Options:

**Option C1: Custom list view on payslips** (recommended)
- Create a dedicated list view of payslips with ALL key fields shown as columns
- Use `<list editable="inline" multi_edit="1">` for batch inline editing
- Odoo 18 supports `multi_edit="1"` — select multiple rows, edit one field, apply to all selected
- Columns: employee, gross, overtime_150, overtime_200, sick_days, vacation_days, + button to open payslip lines

**Option C2: Wizard-generated pivot-like view**
- Wizard generates a temporary model with one row per employee, columns for each editable field
- User edits in this temporary grid
- On save, wizard writes back to payslips
- More complex, more like a real spreadsheet, but fragile

**Recommendation: Option C1** — it's native Odoo, uses `multi_edit`, and doesn't require custom JS widgets. Not as spreadsheet-like as C2, but 80% of the value at 20% of the cost. Can add C2 later if Asya needs more.

### Grid view fields
```xml
<list editable="inline" multi_edit="1" default_order="employee_id">
    <field name="employee_id" readonly="1"/>
    <field name="department_id" readonly="1" optional="hide"/>
    <field name="gross" readonly="1"/>
    <field name="overtime_hours_150"/>
    <field name="overtime_hours_200"/>
    <field name="sick_days"/>
    <field name="sick_days_100"/>
    <field name="vacation_days"/>
    <field name="working_days_in_month"/>
    <field name="bonus_gross_total" readonly="1"/>
    <field name="deduction_net_total" readonly="1"/>
    <field name="net" readonly="1"/>
    <field name="state" widget="badge"/>
</list>
```

Plus a new menu item: "Edycja zbiorcza" → opens this list view filtered to current month.

---

## 5. hr_attendance overtime sync

### Dependency
`hr_attendance` goes back to `__manifest__.py` as **optional** dependency (soft import).

### Mechanism
New method on payslip: `action_sync_attendance()`

```python
def action_sync_attendance(self):
    """Pull overtime hours from hr.attendance for this employee+period."""
    if not hasattr(self.env, 'hr.attendance'):
        raise UserError("Moduł obecności (hr_attendance) nie jest zainstalowany.")

    attendances = self.env['hr.attendance'].search([
        ('employee_id', '=', self.employee_id.id),
        ('check_in', '>=', self.date_from),
        ('check_in', '<=', self.date_to),
    ])
    # Calculate scheduled hours from resource calendar
    scheduled = self._get_scheduled_hours()
    actual = sum(att.worked_hours for att in attendances)
    overtime = max(actual - scheduled, 0)

    # Split into 150% and 200% based on rules (night/holiday = 200%)
    overtime_150, overtime_200 = self._split_overtime(attendances, scheduled)

    self.write({
        'overtime_hours_150': overtime_150,
        'overtime_hours_200': overtime_200,
    })
```

### Traceability
New fields:
```python
attendance_synced = fields.Boolean("Zsynchronizowano z ewidencją")
attendance_sync_date = fields.Datetime("Data synchronizacji")
overtime_manual_override = fields.Boolean("Ręczna korekta nadgodzin")
```

Flow:
1. User clicks "Synchronizuj z ewidencją" button on payslip
2. System pulls attendance data, calculates overtime
3. Sets `attendance_synced = True`
4. If user manually edits overtime_hours_150 or overtime_hours_200 after sync:
   - `overtime_manual_override = True`
   - Warning badge appears: "Nadgodziny zmienione ręcznie"
5. User can re-sync to reset manual changes

### Batch sync
In the batch wizard, add button "Synchronizuj nadgodziny dla wszystkich" that calls `action_sync_attendance()` on all draft payslips for the period.

---

## UI changes

### NET position
Move NET hero element from LEFT to RIGHT in the form view.
Left side: employee info + working fields (employee, contract, dates, working days).
Right side: NET (big), gross, total employer cost.

### Component type management
New menu: Płace → Konfiguracja → Typy składników
Standard list + form view for `pl.payroll.component.type`.

### Updated payslip form
Tab "Składniki dodatkowe":
```xml
<list editable="bottom">
    <field name="component_type_id"/>   <!-- NEW: dropdown -->
    <field name="name"/>
    <field name="category" readonly="1"/>  <!-- auto-set from type -->
    <field name="amount"/>
    <field name="pit_taxable" widget="boolean_toggle"/>  <!-- NEW -->
    <field name="zus_included" widget="boolean_toggle"/>  <!-- NEW -->
    <field name="note"/>
</list>
```

---

## Task breakdown

| Task | Description | Depends on |
|------|-------------|-----------|
| TASK-038 | Model `pl.payroll.component.type` + seed data + views + menu | — |
| TASK-039 | Extend `pl.payroll.payslip.line` with component_type_id, PIT/ZUS flags | TASK-038 |
| TASK-040 | Update salary computation engine for PIT/ZUS exemptions | TASK-039 |
| TASK-041 | Batch wizard `pl.payroll.component.batch.wizard` | TASK-039 |
| TASK-042 | Grid list view for batch editing + menu item | — |
| TASK-043 | hr_attendance overtime sync + traceability fields | — |
| TASK-044 | UI: move NET to right, update form layout | — |
| TASK-045 | Translations: update all .po files for new strings | TASK-038..044 |
| TASK-046 | Seed data: add component examples to demo data | TASK-038 |

TASK-038, TASK-042, TASK-043, TASK-044 can run in parallel.
TASK-039 depends on TASK-038.
TASK-040 depends on TASK-039.
TASK-041 depends on TASK-039.
TASK-045 depends on all.
