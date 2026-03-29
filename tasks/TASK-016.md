# TASK-016: UI polish and bugfixes (Odoo 18)

**Status:** done
**Branch:** task/016-ui-polish
**Created:** 2026-03-29

## Goal

Fix several UI issues discovered during manual testing of the module in Odoo 18. This is a cleanup/polish task.

Write your completion report to `tasks/TASK-016-report.md`.

## Bug 1: Notes field inactive on payslip form

**File:** `views/pl_payroll_payslip_views.xml`

The `notes` field at the bottom of the payslip form (inside a notebook page) appears but is not editable / appears inactive. Check that:
1. The field `notes` exists on model `pl.payroll.payslip` (in `models/pl_payroll_payslip.py`)
2. If it doesn't exist — add it: `notes = fields.Text(string="Notes")`
3. If it exists — check the XML: the field might be inside a `<page>` that has `attrs` making it readonly, or it might be missing `nolabel="1"` or wrapped incorrectly
4. Make sure it's editable in states: draft, computed (readonly only in 'done' and 'cancelled')

**Expected behavior:** Notes field is a free-text area where the payroll officer can add comments to a payslip. Editable in draft and computed states, readonly in done/cancelled.

## Bug 2: Labels not translated / field names ugly

Check all view files and ensure:
1. All field labels use human-readable `string` attributes where the Python field name is unclear
2. Specifically these fields should have clean labels:
   - `zus_emerytalne_ee` → "ZUS Emerytalne (EE)"
   - `zus_rentowe_ee` → "ZUS Rentowe (EE)"
   - `zus_chorobowe_ee` → "ZUS Chorobowe (EE)"
   - `zus_total_ee` → "ZUS Łącznie (EE)"
   - `health_basis` → "Podstawa zdrowotna"
   - `health` → "Składka zdrowotna"
   - `kup_amount` → "KUP"
   - `taxable_income` → "Dochód do opodatkowania"
   - `pit_advance` → "Zaliczka PIT"
   - `pit_reducing` → "Kwota zmniejszająca"
   - `pit_due` → "PIT do zapłaty"
   - `ppk_ee` → "PPK (EE)"
   - `ppk_er` → "PPK (ER)"
   - `total_employer_cost` → "Całkowity koszt pracodawcy"
3. Check the strings are set on the Python field definitions (not just XML), so they appear correctly in list views too.

## Bug 3: Payslip list view — show more columns

**File:** `views/pl_payroll_payslip_views.xml`

Current list view only shows: employee, date_from, date_to, gross, net, state.

Add these columns (optional="show" for some, optional="hide" for others):
- `contract_id` (optional="hide")
- `kup_type` (optional="show")
- `zus_total_ee` (optional="hide")
- `pit_due` (optional="hide")
- `total_employer_cost` (optional="hide")

## Bug 4: Form view — reorganize for readability

The form currently dumps all fields. Reorganize into clear groups:

```
Sheet:
  Group "Identyfikacja":
    employee_id, contract_id, date_from, date_to, state

  Notebook:
    Page "Wynagrodzenie" (Salary):
      Group "Brutto":
        gross, overtime_amount, overtime_hours_150, overtime_hours_200
      Group "ZUS Pracownik":
        zus_emerytalne_ee, zus_rentowe_ee, zus_chorobowe_ee, zus_total_ee
      Group "Podatek":
        health_basis, health, kup_type, kup_amount, taxable_income, pit_advance, pit_reducing, pit_due
      Group "PPK i Netto":
        ppk_ee, net

    Page "Koszty pracodawcy" (Employer):
      Group "ZUS Pracodawca":
        zus_emerytalne_er, zus_rentowe_er, zus_wypadkowe_er, zus_fp, zus_fgsp
      Group "PPK i Total":
        ppk_er, total_employer_cost

    Page "Linie" (Bonuses/Deductions):
      payslip_line_ids (tree: name, category, amount, note)
      (only if pl.payroll.payslip.line model exists — check first)

    Page "Raport twórczy" (Creative Report):
      creative_report_id, creative_needs_report
      (only show if kup_type == 'autorskie')

    Page "Notatki" (Notes):
      notes (nolabel, placeholder="Dodatkowe uwagi...")

  Footer:
    Buttons: Compute, Confirm, Cancel (state-dependent)
```

## Bug 5: Menu ordering

**File:** `views/pl_payroll_menus.xml`

Ensure menu items are ordered logically:
1. Payslips (main list)
2. Batch Compute
3. Creative Reports
4. Configuration > Parameters

## Important rules

- Follow Odoo 18 conventions: `list` not `tree` in view_mode
- Test that XML is valid by checking all tags close properly
- Do NOT change any Python computation logic — this is UI only
- Do NOT change model fields except adding `notes` if missing
- Keep all XML IDs consistent with existing naming convention
- Check `ir.model.access.csv` if you add any new model fields

## Files to modify

- `models/pl_payroll_payslip.py` (only if notes field missing)
- `views/pl_payroll_payslip_views.xml` (main changes)
- `views/pl_payroll_menus.xml` (ordering)
