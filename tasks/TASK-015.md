# TASK-015: Realistic test data seed script

**Status:** done
**Branch:** task/015-realistic-seed-data
**Created:** 2026-03-29

## Goal

Create a standalone Python script `scripts/seed_realistic_data.py` that connects to a running local Odoo via XML-RPC and populates it with ~20 fictional employees, contracts, and 14 months of payslip history (Jan 2025 → Feb 2026). The data must reflect real patterns of OM Energy Solutions (manufacturing company in Lublin, Poland, ~80 employees).

Write your completion report to `tasks/TASK-015-report.md`.

## Connection details

```python
URL = "http://localhost:8069"
DB = "omdev"
USER = "admin@omenergysolutions.pl"
PASSWORD = "omdev2026"
```

Use `xmlrpc.client` (stdlib). Connect to `/xmlrpc/2/common` and `/xmlrpc/2/object`.

## What the script must do

### Step 1: Clean existing demo data

Delete all existing `pl.payroll.payslip`, `hr.contract`, `hr.employee` records (except employee id=1, the admin). This ensures idempotent re-runs.

### Step 2: Create departments

Create these departments (model `hr.department`):
- Produkcja (Production)
- Laboratorium (Laboratory)
- Magazyn (Warehouse)
- Biuro (Office)
- Zarząd (Management)

### Step 3: Create 20 fictional employees

ALL names, PESEL, addresses are FICTIONAL. Never use real data.

Use this distribution (mirrors real OM Energy):

| # | Name | Job title | Dept | Nationality |
|---|------|-----------|------|-------------|
| 1 | Tomasz Kowalski | Pracownik produkcji | Produkcja | PL |
| 2 | Anna Wiśniewska | Pracownik produkcji | Produkcja | PL |
| 3 | Piotr Mazur | Pracownik produkcji | Produkcja | PL |
| 4 | Katarzyna Nowak | Pracownik produkcji | Produkcja | PL |
| 5 | Wojciech Zieliński | Pracownik produkcji | Produkcja | PL |
| 6 | Ewa Krawczyk | Pracownik produkcji | Produkcja | PL |
| 7 | Oleksandr Kovalenko | Pracownik produkcji | Produkcja | UA |
| 8 | Nataliia Shevchenko | Pracownik produkcji | Produkcja | UA |
| 9 | Dmytro Melnyk | Pracownik produkcji | Produkcja | UA |
| 10 | Yuliia Kravchuk | Pracownik produkcji | Produkcja | UA |
| 11 | Mikołaj Szymański | Kierownik zmiany | Produkcja | PL |
| 12 | Paulina Dąbrowska | Kierownik zmiany | Produkcja | PL |
| 13 | Kacper Wójcik | Laborant | Laboratorium | PL |
| 14 | Michał Adamski | Inżynier procesu | Laboratorium | PL |
| 15 | Natalia Ivanchuk | Magazynierka | Magazyn | UA |
| 16 | Monika Brzeska | Administrator materiałowy | Magazyn | PL |
| 17 | Liudmyla Savchenko | Specjalistka ds. księgowości | Biuro | UA |
| 18 | Szymon Jankowski | Inżynier mechanik | Biuro | PL |
| 19 | Aleksander Volkov | Dyrektor ds. Operacji | Zarząd | UA |
| 20 | Marta Lewandowska | CKO (Dyrektor ds. Wiedzy i IT) | Zarząd | PL |

Model: `hr.employee`. Fields: `name`, `job_title`, `department_id`, `work_email` (generate as first letter + surname @omtest.net, e.g. tkowalski@omtest.net).

### Step 4: Create contracts

Model: `hr.contract`. One per employee.

Fields: `name`, `employee_id`, `wage`, `date_start`, `state` ('open'), plus our custom payroll fields on hr.contract: `kup_type`, `kup_autorskie_pct`, `ppk_enabled`, `ppk_rate_type`.

**Contract details:**

| Employee | Contract type | Wage (PLN) | Start date | KUP type | KUP autorskie % | PPK |
|----------|--------------|------------|------------|----------|-----------------|-----|
| 1-6 (PL production) | UoP | 4806 (minimum) | 2025-01-01 | standard | — | enabled, default |
| 7-10 (UA production) | UoP | 4806 | 2025-03-01 | standard | — | enabled, default |
| 11 (shift mgr) | UoP | 7500 | 2025-01-01 | standard | — | enabled, default |
| 12 (shift mgr) | UoP | 6500 | 2025-06-01 | standard | — | enabled, default |
| 13 (lab) | UoP | 6000 | 2025-01-01 | standard | — | enabled, default |
| 14 (engineer) | UoP | 8000 | 2025-01-01 | autorskie | 50 | enabled, default |
| 15 (warehouse UA) | UoP | 4806 | 2025-04-01 | standard | — | enabled, default |
| 16 (mat admin) | UoP | 5500 | 2025-01-01 | standard | — | ppk_enabled=False |
| 17 (accounting) | UoP | 7000 | 2025-01-01 | standard | — | enabled, default |
| 18 (mech engineer) | UoP | 8500 | 2025-01-01 | autorskie | 50 | enabled, default |
| 19 (operations dir) | UoP | 15000 | 2025-01-01 | standard | — | enabled, default |
| 20 (CKO) | UoP | 12000 | 2025-01-01 | autorskie | 50 | enabled, default |

Note: `ppk_rate_type` values: 'default' (2%), 'reduced' (0.5%), or empty. Use 'default' unless specified.

For `kup_type`: 'standard' (250 PLN/month) or 'autorskie' (50% of post-ZUS income). Only employees 14, 18, 20 use autorskie.

### Step 5: Generate payslips for each month

For each employee, for each month from their `date_start` through February 2026:

1. Create payslip: `pl.payroll.payslip` with `employee_id`, `contract_id`, `date_from` (1st of month), `date_to` (last of month)
2. Call `action_compute` on the payslip (method on the model, call via `execute_kw`)
3. Call `action_confirm` to set state to 'done'

This means:
- Employees starting Jan 2025 → 14 payslips each
- Employees starting Mar 2025 → 12 payslips each
- Employees starting Apr 2025 → 11 payslips each
- Employee starting Jun 2025 → 9 payslips each

**Total: ~240 payslips.**

### Step 6: Add some bonuses/deductions (if TASK-014 model exists)

After creating payslips, try to add some `pl.payroll.payslip.line` entries to demonstrate bonuses/deductions. Wrap in try/except — if model doesn't exist, skip silently.

Add to ~5 random payslips:
- Employee 11 (shift mgr), December 2025: bonus_gross "Premia roczna" 2000 PLN
- Employee 19 (operations dir), June 2025: bonus_gross "Premia za wyniki" 5000 PLN
- Employee 3, September 2025: deduction_gross "Kara porządkowa" 200 PLN
- Employee 20 (CKO), January 2026: bonus_gross "Premia projektowa" 3000 PLN
- Employee 14 (engineer), November 2025: bonus_gross "Dodatek funkcyjny" 1000 PLN

After adding lines, recompute those payslips: call `action_compute` again.

## Edge cases the data must demonstrate

1. **Cumulative PIT bracket crossing**: Employee 19 (15,000/month) → annual income crosses 120k PLN around month 8 (August). PIT should jump from 12% to 32% on the excess.
2. **ZUS basis cap**: Employee 19 → cumulative gross reaches 282,600 PLN cap. After that, pension + disability contributions stop. This happens around month 19, so won't trigger in 14 months — but employee 20 (12,000) + employee 19 (15,000) together show high earners approaching it.
3. **KUP autorskie vs standard**: Compare employees 13 (6000 standard) vs 14 (8000 autorskie) — autorskie saves significant PIT.
4. **PPK opt-out**: Employee 16 has ppk_enabled=False — net is slightly higher.
5. **Late starters**: UA employees (7-10) start in March, so they have fewer payslips and lower cumulative PIT.

## Script structure

```python
#!/usr/bin/env python3
"""Seed realistic test data into local Odoo for l10n_pl_payroll module."""

import xmlrpc.client
from datetime import date, timedelta
import calendar

# Connection
URL = "http://localhost:8069"
DB = "omdev"
USER = "admin@omenergysolutions.pl"
PASSWORD = "omdev2026"

def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    return uid, models

def execute(models, uid, model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

def main():
    uid, models = connect()
    # Step 1: clean
    # Step 2: departments
    # Step 3: employees
    # Step 4: contracts
    # Step 5: payslips (month by month, with progress logging)
    # Step 6: bonuses (try/except)
    print("Done! Created X employees, Y contracts, Z payslips.")

if __name__ == "__main__":
    main()
```

## Important rules

- ALL names/PESEL/addresses are FICTIONAL
- Use print() for progress (e.g. "Creating payslip for Tomasz Kowalski 2025-03...")
- Handle errors gracefully — if one payslip fails, log and continue
- Script must be idempotent (can be re-run safely due to Step 1 cleanup)
- Do NOT import any Odoo modules — this is a standalone XML-RPC script
- Use only Python stdlib (xmlrpc.client, datetime, calendar)
- Put the script in `scripts/seed_realistic_data.py`

## Verification

After running, query payslips and verify:
1. Employee 19 January 2026 payslip: PIT rate should be 32% (income > 120k)
2. Employee 14 payslip: KUP amount should be ~50% of post-ZUS income, not 250 PLN
3. Employee 16 payslip: ppk_ee should be 0
4. Total payslips ≈ 240

Print a summary table at the end:
```
Employee          | Months | Total Gross | Total Net | Avg Net/Month
Tomasz Kowalski   |   14   |   67,284    |  48,XXX   |    3,XXX
...
```
