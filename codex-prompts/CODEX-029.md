# Codex Task: TASK-029 — Multi-contract seed scenario

Read `CLAUDE.md`, then `LESSONS.md`, then `DECISIONS.md`, then `ODOO_RECON.md`, then `tasks/TASK-029.md`.

## Summary

Fix and finish the local draft patch in `scripts/seed_realistic_data.py` so one fictional employee, Marek Jabłoński, is seeded once with two contracts and 14 payslips split across those contracts without breaking existing seeded employees.

## Required behavior

1. Create exactly one `hr.employee` for Marek Jabłoński.
2. Create exactly two `hr.contract` records for Marek:
   - `zlecenie`, `4200.0`, `2025-01-01` to `2025-06-30`, `state=close`
   - `o_prace`, `5200.0`, `2025-07-01`, no end date, `state=open`
3. Create 6 payslips on the first contract and 8 payslips on the second contract.
4. Keep global totals at:
   - `Employees created: 24`
   - `Contracts created: 25`
   - `Expected payslips: 296`
5. Fix summary logic so Marek is not duplicated.

## Scope

- Modify `scripts/seed_realistic_data.py`
- Create `tasks/TASK-029-report.md`
- Update `tasks/TASK-029.md` status to `done` before commit

## Verification

1. `python3 -m py_compile scripts/seed_realistic_data.py`
2. If local Odoo is available:
   - `bash scripts/upgrade_module.sh`
   - `python3 scripts/seed_realistic_data.py`
   - verify via XML-RPC or existing repo mechanism:
     - one `hr.employee` for Marek
     - two contracts with correct dates and states
     - 6 payslips linked to `zlecenie`
     - 8 payslips linked to `o_prace`
     - correct total counters

## Git

- Branch: `task/029-multi-contract-seed`
- Commit: `[TASK-029] Add multi-contract seed scenario`
