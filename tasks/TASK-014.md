# TASK-014: Bonuses and deductions (premie, potrącenia)

**Status:** done
**Branch:** task/014-bonuses-deductions
**Created:** 2026-03-28

## Goal

Add support for additional earnings (bonuses/premie) and deductions (potrącenia/kary) on payslips. These modify gross before ZUS/PIT chain.

## Context

Currently gross = contract wage + overtime. Real payroll also has:
- Bonuses (premia regulaminowa, nagroda, dodatek funkcyjny, etc.)
- Deductions (kara porządkowa, potrącenie komornicze, etc.)

Some are gross-affecting (before ZUS), some are net-affecting (after all deductions). Both types needed.

## Requirements

### New model: `pl.payroll.payslip.line`

One-to-many child of payslip. Each line = one bonus or deduction.

Fields:
- `payslip_id` — Many2one to pl.payroll.payslip
- `name` — Char, description (e.g. "Premia za marzec")
- `category` — Selection: `bonus_gross` (dodane do brutto), `deduction_gross` (odjęte od brutto), `deduction_net` (odjęte od netto)
- `amount` — Float, always positive
- `note` — Text, optional

### Payslip changes

- `payslip_line_ids` — One2many to pl.payroll.payslip.line
- `bonus_gross_total` — computed, sum of bonus_gross lines
- `deduction_gross_total` — computed, sum of deduction_gross lines
- `deduction_net_total` — computed, sum of deduction_net lines

### Computation chain update

```
base_gross (from contract)
  + overtime_amount
  + bonus_gross_total
  - deduction_gross_total
  = gross (input to ZUS chain)
  ... ZUS → Health → KUP → PIT → PPK ...
  = net_before_deductions
  - deduction_net_total
  = net
```

### Views

- Payslip form: notebook tab "Bonuses & Deductions" with inline tree of payslip lines
- Lines editable only in draft state

### Security

- Same RBAC as payslip (officer can edit, employee reads own)

### Tests

- Payslip with bonus_gross: verify gross increases, ZUS/PIT recalculates
- Payslip with deduction_net: verify net decreases but gross/ZUS untouched
- Payslip with deduction_gross: verify gross decreases
- Mix of all three types
- Empty lines: no effect on calculation

## Scope boundary — DO NOT touch

- `_compute_overtime_amount()` — already done in TASK-012
- `_link_creative_report()` — already done in TASK-013
- Do NOT add new fields to these methods or rename them

## Files

- `models/pl_payroll_payslip_line.py` — new model
- `models/pl_payroll_payslip.py` — add line fields + update `_compute_single_payslip()`
- `models/__init__.py` — add import
- `views/pl_payroll_payslip_views.xml` — add Bonuses & Deductions tab
- `security/ir.model.access.csv` — access rules for new model
- `tests/test_payslip.py` — add bonus/deduction tests
- `__manifest__.py` — include new files
