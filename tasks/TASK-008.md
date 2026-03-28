# TASK-008: Umowa zlecenie support + gross snapshot fix

**Status:** open
**Assignee:** Codex
**Branch:** task/008-zlecenie-gross-fix
**Depends on:** TASK-007 merged

## Objective

Two things in one task (they both modify pl_payroll_payslip.py):

### Part A: Umowa zlecenie (civil contract)

Add support for umowa zlecenie in the payslip computation. Currently only umowa o pracę works. Scenarios 8 and 9 from expected_results.py must pass.

Key differences from umowa o pracę:
- KUP = 20% of health_basis (standard for zlecenie), NOT 250 PLN flat
- Autorskie KUP = 50% of health_basis for creative work (same formula as o pracę)
- ZUS chorobowe is VOLUNTARY (flag on contract, default: yes for zlecenie)
- No PIT-2 reducing for zlecenie (pit2_filed should be False)
- Contract has `contract_type_id` field — check demo data for the xmlid

The contract model (hr_contract.py from TASK-004) already has `contract_type_id` and `kup_type = 'standard_20'`. The payslip model already handles `kup_type == 'standard_20'` in `_compute_kup_amount()`. So the main gap is probably small — verify by running scenarios 8 and 9 against expected_results.py.

Scenario 8 (Tomasz Zieliński): mandate, 35 PLN/h × 160h = 5600 gross, 20% KUP, PPK opt-out
Scenario 9 (Natalia Kravchuk): mandate, 40 PLN/h × 160h = 6400 gross, 100% autorskie, PPK opt-out

### Part B: Gross snapshot

Currently `gross = fields.Float(related='contract_id.wage', readonly=True)`. This means if the contract wage changes, old payslips show the new value. Fix:

1. Change `gross` from related field to a regular Float field
2. In `_compute_single_payslip()`, before calculation, set `self.gross = self.contract_id.wage`
3. This way the gross is "snapshotted" at compute time

### Tests

1. Add scenarios 8 and 9 to test_payslip.py (they're already in expected_results.py and SCENARIO_XMLIDS)
2. Add a test that gross is preserved after contract wage change:
   - Create payslip, compute, confirm
   - Change contract wage
   - Assert payslip.gross still shows the old value

## Files to modify

- `l10n_pl_payroll/models/pl_payroll_payslip.py` — gross field change + any zlecenie logic
- `l10n_pl_payroll/tests/test_payslip.py` — add scenarios 8, 9 + gross snapshot test

## Git Workflow

```
git checkout main && git pull
git checkout -b task/008-zlecenie-gross-fix
# ... implement ...
git add l10n_pl_payroll/models/pl_payroll_payslip.py l10n_pl_payroll/tests/test_payslip.py
git commit -m "[TASK-008] Add umowa zlecenie support + snapshot gross at compute time"
git push -u origin task/008-zlecenie-gross-fix
gh pr create --title "[TASK-008] Umowa zlecenie + gross snapshot" --body "Adds zlecenie support (scenarios 8,9) and snapshots gross at compute time to preserve history."
```
