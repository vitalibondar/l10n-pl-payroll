# TASK-036: Make local upgrade and seed flow wait for Odoo readiness

**Status:** done
**Assignee:** codex
**Branch:** main
**Created:** 2026-03-30

## Context

The local upgrade flow restarted Odoo successfully, but the next seed step sometimes hit XML-RPC too early and failed with:

- `http.client.RemoteDisconnected: Remote end closed connection without response`

This is a startup race after `scripts/upgrade_module.sh`, not a data bug in the seed payload.

## Goal

Make the local `upgrade -> seed` workflow reliable for a non-technical user:

- no blind `sleep 5`
- no manual retry needed
- seed script itself waits until Odoo is truly ready for XML-RPC

## Scope

- `scripts/seed_realistic_data.py`
- `scripts/verify_calculations.py`
- `scripts/seed_and_verify.sh`
- `scripts/README.md`
- `tasks/TASK-036-report.md`
- `codex-prompts/CODEX-036.md`

## Acceptance Criteria

- [x] `scripts/seed_realistic_data.py` retries XML-RPC connect/auth until Odoo is ready or timeout is reached
- [x] `scripts/verify_calculations.py` reuses the same robust connect path
- [x] `scripts/seed_and_verify.sh` waits for real XML-RPC readiness instead of fixed sleep
- [x] README reflects the new behavior
- [x] `python3 -m py_compile scripts/seed_realistic_data.py scripts/verify_calculations.py` passes
- [x] `bash scripts/seed_and_verify.sh` finishes successfully

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main
git pull

git add scripts/seed_realistic_data.py
git add scripts/verify_calculations.py
git add scripts/seed_and_verify.sh
git add scripts/README.md
git add tasks/TASK-036.md
git add tasks/TASK-036-report.md
git add codex-prompts/CODEX-036.md

git commit -m "[TASK-036] Make seed flow wait for Odoo readiness"
git push origin main
```
