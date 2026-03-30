# TASK-038: Model pl.payroll.component.type + seed data + views

**Status:** ready
**Phase:** 6 — Component Constructor
**Depends on:** —
**Architecture:** ARCHITECTURE-PHASE6.md § 1

## What

Create the Component Type constructor model — `pl.payroll.component.type`. This is the core of Phase 6: users define their own payroll component types with PIT/ZUS rules through the UI.

## Deliverables

### 1. Model file: `models/pl_payroll_component_type.py`

Fields (see ARCHITECTURE-PHASE6.md for full spec):
- `name` (Char, required)
- `code` (Char, required, unique per company)
- `sequence` (Integer, default=10)
- `active` (Boolean, default=True)
- `category` (Selection: bonus_gross, deduction_gross, benefit_in_kind, deduction_net)
- `pit_taxable` (Boolean, default=True)
- `pit_exempt_article` (Char)
- `zus_included` (Boolean, default=True)
- `zus_exempt_limit` (Float, default=0.0)
- `zus_exempt_article` (Char)
- `default_amount` (Float)
- `requires_documentation` (Boolean)
- `documentation_hint` (Char)
- `company_id` (Many2one res.company)
- `note` (Text)

Constraint: `_sql_constraints = [("code_company_uniq", "unique(code, company_id)", "...")]`

### 2. Seed data: `data/pl_payroll_component_type_data.xml`

Pre-seeded types (noupdate="0"):
- PREMIA — Premia (bonus_gross, PIT+ZUS)
- PRANIE — Ekwiwalent za pranie (bonus_gross, !PIT, !ZUS, art. 21(1)(11))
- POSILKI_FIN — Finansowanie posiłków (benefit_in_kind, PIT, !ZUS, limit 450)
- POSILKI_PROF — Posiłki profilaktyczne (benefit_in_kind, !PIT, !ZUS, art. 232 KP)
- KARTA_SPORT — Karta sportowa (benefit_in_kind, PIT+ZUS)
- POTRACENIE_KOMORNICZE — Potrącenie komornicze (deduction_net, !PIT, !ZUS)
- NADGODZINY_ATT — Nadgodziny z ewidencji (bonus_gross, PIT+ZUS)

### 3. Views: `views/pl_payroll_component_type_views.xml`

- List view with columns: sequence, code, name, category, pit_taxable, zus_included, active
- Form view with groups: basic info, tax rules, ZUS rules, defaults, notes
- Search view: filter by category, active

### 4. Security

- Add to `ir.model.access.csv`: read for payroll_officer, full CRUD for payroll_manager
- Add record rule in security XML

### 5. Menu

Płace → Konfiguracja → Typy składników

### 6. Update __manifest__.py

Add new data/view/security files.

### 7. Update models/__init__.py

Import new model.

## Don't

- Don't hardcode any rates in the model — this is a constructor, rates come from parameters
- Don't add translations in this task (TASK-045)
- Don't modify payslip.line yet (TASK-039)
