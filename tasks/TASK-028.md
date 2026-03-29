# TASK-028: Full integration test — upgrade, seed, verify

**Status:** done
**Branch:** task/028-integration-test
**Created:** 2026-03-29
**Depends on:** TASK-027

## Goal

After all features are implemented and UI polished, do a full integration test:
1. Upgrade module on local Odoo
2. Run seed script with all employee types
3. Verify every calculation for every employee type
4. Fix any bugs found
5. Document results

Write your completion report to `tasks/TASK-028-report.md`.

## Steps

### 1. Upgrade module

```bash
cd /Users/vb/l10n-pl-payroll
bash scripts/upgrade_module.sh
```

If upgrade fails — fix the error and retry.

### 2. Run seed script

```bash
python3 scripts/seed_realistic_data.py
```

Verify output: should create 22+ employees (20 original + 2 students + 1 dzieło) with 280+ payslips.

### 3. Verify calculations via XML-RPC

Write a verification script `scripts/verify_calculations.py` that:
- Connects to local Odoo
- For each employee, reads the latest payslip
- Recalculates gross→net independently (using the same rates from pl.payroll.parameter)
- Compares: ZUS, health, KUP, PIT, PPK, net
- Flags any discrepancy > 0.01 PLN
- Prints a summary table

### 4. Specific scenarios to verify

- Standard employee (Tomasz Kowalski, 4806 PLN): full chain
- Autorskie KUP (Michał Adamski, 8000 PLN, 50%): lower PIT due to creative KUP
- PPK opt-out (Monika Brzeska): PPK = 0
- High earner (Aleksander Volkov, 15000 PLN): PIT bracket crossing in ~October
- Student on zlecenie (Jakub Wiśniewski): ZUS = 0, health = 0
- Dzieło (if seeded): no ZUS, flat 12% PIT
- Part-time (if seeded): proportional KUP
- Sick leave (if any payslip has sick_days > 0): verify 80% calculation

### 5. Verify PIT-11 generation

- Call PIT-11 wizard for year 2025
- Check that PIT-11 records are created for all employees
- Verify totals match sum of payslips

### 6. Verify ZUS DRA

- Call ZUS DRA wizard for January 2026
- Check that DRA lines match individual payslips

### 7. Verify batch wizard

- Delete one month's payslips
- Run batch wizard for that month
- Verify payslips recreated and computed correctly

## Files to create

- CREATE: `scripts/verify_calculations.py`

## Files to modify

- MODIFY: `scripts/seed_realistic_data.py` (if bugs found in seed data)
