# TASK-021: Umowa o dzieło support

**Status:** done
**Branch:** task/021-umowa-dzielo
**Created:** 2026-03-29
**Depends on:** none

## Goal

Add support for umowa o dzieło (contract for a specific work). This is the third major contract type in Polish payroll, alongside umowa o pracę and umowa zlecenie.

Write your completion report to `tasks/TASK-021-report.md`.

## Polish rules for umowa o dzieło

1. **NO ZUS contributions** at all (neither employee nor employer) — UNLESS the dzieło is with the employee's own employer (the same company where they have umowa o pracę). That edge case is out of scope for now.
2. **KUP**: either 20% (standard for dzieło) or 50% (autorskie — if the work is creative/copyrighted)
3. **PIT**: flat 12% advance (no cumulative calculation, no kwota zmniejszająca for dzieło)
4. **No PPK** (PPK applies only to umowa o pracę)
5. **No health insurance** from employer
6. **No FP, FGŚP**

## What to implement

### 1. Detect dzieło contract type

Add to `pl_payroll_payslip.py`:

```python
def _is_dzielo_contract(self):
    self.ensure_one()
    contract_type_name = (self.contract_id.contract_type_id.name or "").strip().lower()
    return contract_type_name == "umowa o dzieło"
```

### 2. Modify _compute_single_payslip

For dzieło contracts, the calculation is radically simpler:

```python
if self._is_dzielo_contract():
    # No ZUS at all
    zus_emerytalne_ee = zus_rentowe_ee = zus_chorobowe_ee = zus_total_ee = Decimal("0.00")
    health_basis = Decimal("0.00")
    health = Decimal("0.00")

    # KUP: 20% or 50% of gross
    if self.contract_id.kup_type == "autorskie":
        kup_amount = self._round_amount(gross * Decimal("0.50"))
    else:
        kup_amount = self._round_amount(gross * Decimal("0.20"))

    taxable_income = self._floor_amount(gross - kup_amount)

    # PIT: flat 12%, no cumulative, no kwota zmniejszająca
    pit_advance = self._round_amount(taxable_income * Decimal("0.12"))
    pit_reducing = Decimal("0.00")
    pit_due = self._floor_amount(pit_advance)

    # No PPK
    ppk_ee = Decimal("0.00")
    ppk_er = Decimal("0.00")

    net = self._round_amount(gross - pit_due)

    # Employer costs: only gross (no additional costs)
    zus_emerytalne_er = zus_rentowe_er = zus_wypadkowe_er = Decimal("0.00")
    zus_fp = zus_fgsp = Decimal("0.00")
    total_employer_cost = gross
```

This should be an early return path in `_compute_single_payslip`, before the regular calculation.

### 3. Handle dzieło below 200 PLN threshold

If a single dzieło is ≤ 200 PLN gross, PIT is calculated as flat 12% of gross with NO KUP deduction. This is "zryczałtowany podatek dochodowy":

```python
if gross <= Decimal("200"):
    pit_advance = self._round_amount(gross * Decimal("0.12"))
    kup_amount = Decimal("0.00")
    taxable_income = gross
```

### 4. Create contract type data

In `l10n_pl_payroll/data/pl_payroll_contract_type_data.xml` (CREATE), add:

```xml
<record id="contract_type_dzielo" model="hr.contract.type">
    <field name="name">Umowa o dzieło</field>
</record>
```

Also ensure existing types exist:

```xml
<record id="contract_type_praca" model="hr.contract.type">
    <field name="name">Umowa o pracę</field>
</record>
<record id="contract_type_zlecenie" model="hr.contract.type">
    <field name="name">Umowa zlecenie</field>
</record>
```

Register in `__manifest__.py`.

### 5. Tests

Create `tests/test_dzielo.py`:

- `test_dzielo_no_zus`: ZUS employee + employer = 0
- `test_dzielo_kup_20`: standard dzieło → KUP = 20% of gross
- `test_dzielo_kup_50_autorskie`: autorskie dzieło → KUP = 50% of gross
- `test_dzielo_flat_pit`: PIT = 12% of (gross - KUP), no kwota zmniejszająca
- `test_dzielo_no_ppk`: PPK employee + employer = 0
- `test_dzielo_below_200`: gross ≤ 200 → PIT = 12% of gross, KUP = 0
- `test_dzielo_net`: net = gross - PIT (no ZUS, no health, no PPK)

### 6. Update seed script

Add 1 dzieło employee to seed data (e.g., "Bartosz Nowicki", freelance graphic designer, 3000 PLN dzieło with autorskie 50%). Generate 3-4 payslips.

## Important

- Dzieło with own employer (same company where pracę) = ZUS applies. OUT OF SCOPE for this task.
- Dzieło does NOT have cumulative PIT. Each payment is taxed independently.
- No health, no PPK, no FP, no FGŚP.
- KUP for dzieło: always calculated on gross (not on post-ZUS basis, since there's no ZUS).

## Files to create/modify

- CREATE: `l10n_pl_payroll/data/pl_payroll_contract_type_data.xml`
- CREATE: `l10n_pl_payroll/tests/test_dzielo.py`
- MODIFY: `l10n_pl_payroll/models/pl_payroll_payslip.py` (dzieło calculation path)
- MODIFY: `l10n_pl_payroll/__manifest__.py` (add contract type XML)
- MODIFY: `scripts/seed_realistic_data.py` (add dzieło employee)
