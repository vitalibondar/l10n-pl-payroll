# l10n_pl_payroll — Polish Payroll for Odoo

> Read this FIRST. Then LESSONS.md. Then your TASK file.

## What is this

Odoo module for calculating Polish salaries (gross-to-net) and generating pay slips. Supports umowa o pracę and umowa zlecenie. Built for Om Energy Solutions (manufacturing, Poland, 82 employees).

## Environment

- **Odoo Enterprise 17+** on **Odoo.sh**
- **Python 3.10+** (Odoo.sh standard)
- **PostgreSQL** (Odoo.sh managed)
- **Test DB available** — safe to experiment
- **Production DB** — NEVER write to production without explicit approval

## Architecture Decisions (summary)

Full details in DECISIONS.md. Key rules:

1. **Parameterized rates** — all tax/ZUS/PPK rates stored in `pl.payroll.parameter` model with `date_from`/`date_to`. Salary rules reference parameters, NEVER hardcoded literals.
2. **Autorskie koszty** — require explicit flag + percentage on employee contract. No silent 50% KUP.
3. **RBAC** — security groups: `payroll_officer`, `payroll_manager`, `employee_self`.
4. **Fictional test data only** — no real PESEL, names, or salaries in code/tests/commits.
5. **Cumulative PIT** — Polish PIT is calculated year-to-date, not per-month. Each payslip must reference all prior months.
6. **ZUS basis cap** — after annual threshold (282,600 PLN in 2026), pension + disability stop, health continues. Track cumulative gross per employee per year.

## Code Style

- Follow Odoo 17 module conventions
- Python: PEP 8, no type hints (project convention)
- XML: Odoo data/view conventions
- Comments: only where logic is non-obvious
- No docstrings for simple methods
- One model per file in `models/`
- Tests mirror model structure in `tests/`

## Salary Rules Chain (umowa o pracę)

```
GROSS (from contract)
  → minus ZUS employee (emerytalne 9.76% + rentowe 1.5% + chorobowe 2.45%)
  = BASE for health insurance
  → minus Health (9%)
  → minus KUP (250 PLN/month standard OR 50% autorskie)
  = TAXABLE INCOME
  → minus PIT (12% up to 120k/year, 32% above; minus kwota zmniejszająca 300 PLN/month if PIT-2)
  → minus PPK employee (2%)
  = NET
```

Employer-side (not deducted from employee, but calculated):
- ZUS emerytalne ER: 9.76%
- ZUS rentowe ER: 6.5%
- ZUS wypadkowe ER: 1.67% (default, varies by company)
- FP: 2.45%
- FGŚP: 0.1%
- PPK ER: 1.5%

## Git Workflow

- Main branch: `main`
- Feature branches: `task/NNN-short-desc`
- Commit format: `[TASK-NNN] Description`
- PR per task or logical group
- No force pushes
- No real data in commits

## Task Protocol

Before starting any task:
1. Read this file (CLAUDE.md)
2. Read LESSONS.md
3. Read your TASK-NNN.md file in tasks/
4. If task involves architecture → read DECISIONS.md
5. If task involves Odoo models → read ODOO_RECON.md

After completing:
1. Update TASK-NNN.md status → `done`
2. Commit with `[TASK-NNN]` prefix
3. If you discovered a new lesson → add to LESSONS.md

## Don't

- Don't hardcode rates. Use parameters.
- Don't use real employee data. Ever.
- Don't change architecture without updating DECISIONS.md.
- Don't skip reading LESSONS.md — repeated mistakes waste everyone's time.
- Don't create Enterprise-only features without checking (hr_payroll is NOT installed, we build our own).
- Don't import from `odoo.addons.hr_payroll` — it doesn't exist in this installation.
