# Codex Task: TASK-017 — Helper shell scripts

Read `CLAUDE.md`, then `tasks/TASK-017.md` for full requirements.

## Summary

Create two shell scripts in `scripts/`:

1. `scripts/upgrade_module.sh` — stops Odoo, runs `-u l10n_pl_payroll`, restarts
2. `scripts/seed_and_verify.sh` — runs upgrade, waits, then runs the seed script
3. `scripts/README.md` — brief docs for both scripts

## Key details

- Docker compose file: `$HOME/odoo-docker-compose.yml`
- Database: `omdev`
- Module: `l10n_pl_payroll`
- Seed script path: `scripts/seed_realistic_data.py` (from TASK-015, may not exist yet — that's OK, script just calls it)

## Branch

Create branch `task/017-upgrade-module` from `main`. Commit with prefix `[TASK-017]`.

## Report

Write your completion report to `tasks/TASK-017-report.md`.
