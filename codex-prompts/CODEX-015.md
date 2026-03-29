# Codex Task: TASK-015 — Realistic test data seed script

Read `CLAUDE.md`, then `LESSONS.md`, then `tasks/TASK-015.md` for full requirements — they are very detailed.

## Summary

Create `scripts/seed_realistic_data.py` — a standalone Python script that:

1. Connects to local Odoo via XML-RPC (`localhost:8069`, db `omdev`, user `admin@omenergysolutions.pl`, password `omdev2026`)
2. Cleans existing demo data (payslips, contracts, employees except admin)
3. Creates 5 departments, 20 fictional employees, 20 contracts
4. Generates payslips month-by-month from each employee's start date through February 2026
5. Calls `action_compute` and `action_confirm` on each payslip
6. Adds a few bonus/deduction lines (try/except if model missing)
7. Prints a summary table

## Key constraints

- Use ONLY Python stdlib (xmlrpc.client, datetime, calendar) — no pip installs
- ALL employee data is FICTIONAL — no real names/PESEL
- Script must be idempotent (cleanup first, then create)
- Print progress for each payslip (there will be ~240)
- Handle errors gracefully — if one payslip fails, log and continue
- The full employee/contract table is in `tasks/TASK-015.md`

## Edge cases to demonstrate

- Employee 19 (15,000/mo): PIT bracket crossing (12% → 32%) around August 2025
- Employees 14, 18, 20: autorskie KUP 50% (much lower PIT than standard)
- Employee 16: PPK opt-out (ppk_enabled=False)
- Employees 7-10: later start dates (March 2025), fewer payslips

## Branch

Create branch `task/015-realistic-seed-data` from `main`. Commit with prefix `[TASK-015]`.

## Report

Write your completion report to `tasks/TASK-015-report.md` including the summary table output.
