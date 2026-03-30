# TASK-040: Update salary engine for PIT/ZUS exemptions

**Status:** ready
**Phase:** 6 — Component Constructor
**Depends on:** TASK-039
**Architecture:** ARCHITECTURE-PHASE6.md § 3

## What

Modify `_compute_single_payslip()` to respect PIT/ZUS flags on payslip lines. Currently ALL bonus_gross lines enter both ZUS and PIT basis. After this task, only lines with the respective flag do.

## Key logic changes

### ZUS basis calculation

Currently:
```python
gross = base_wage + overtime + vacation + bonus_gross_total - deduction_gross_total
zus_basis = gross  # implicit
```

After:
```python
# Cash gross stays the same (ALL bonuses/deductions affect what employee receives)
gross = base_wage + overtime + vacation + ALL_bonus_gross - ALL_deduction_gross

# ZUS basis = only components that are ZUS-included
zus_basis = base_wage + overtime + vacation + zus_included_bonus - zus_deduction_gross + benefit_in_kind_zus
```

### ZUS exempt limit handling

For components with `zus_exempt_limit > 0` (e.g., posiłki 450 PLN):
- If line amount ≤ limit → entire amount is ZUS-exempt
- If line amount > limit → excess above limit enters ZUS basis
- Limit is per component TYPE per month (not per line)

### PIT basis calculation

Currently:
```python
taxable_income = health_basis - kup_amount + ppk_er
```

After:
```python
taxable_income = health_basis - kup_amount + ppk_er + benefit_in_kind_pit
```

Where `health_basis` is computed from `zus_basis` (not gross).

### New stored fields on payslip

```python
zus_basis = fields.Float("Podstawa wymiaru składek ZUS")
```

## Critical: cumulative PIT

The YTD calculation must also account for PIT-exempt components in prior months. When computing cumulative income, only sum PIT-taxable portions.

## Test scenarios

1. Payslip with 100% taxable bonus → same result as before (regression)
2. Payslip with ekwiwalent za pranie 150 PLN → no PIT, no ZUS impact
3. Payslip with posiłki 400 PLN → PIT taxable, ZUS exempt (under 450 limit)
4. Payslip with posiłki 500 PLN → PIT on 500, ZUS on 50 (500-450 excess)
5. Payslip with mixed: bonus 1000 (PIT+ZUS) + pranie 150 (!PIT, !ZUS) → verify correct bases

## Don't

- Don't touch the dzieło or zlecenie computation paths unless they also use payslip lines
- Don't change the PIT cumulative logic structure — only adjust what enters the basis
- Don't break any existing test scenarios
