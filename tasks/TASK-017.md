# TASK-017: Module upgrade after TASK-014 and TASK-016

**Status:** done
**Branch:** task/017-upgrade-module
**Created:** 2026-03-29

## Goal

After TASK-014 (bonuses/deductions) and TASK-016 (UI polish) are merged to main, write a shell script that upgrades the module on the local Docker Odoo instance so the changes take effect.

Write your completion report to `tasks/TASK-017-report.md`.

## Context

The local Odoo runs via docker-compose at `~/odoo-docker-compose.yml`. The module source is mounted from `~/l10n-pl-payroll/l10n_pl_payroll` into the container at `/mnt/extra-addons/l10n_pl_payroll`.

Since the source is a volume mount, code changes on the host are immediately visible in the container. But Odoo needs a module upgrade (`-u`) to pick up:
- New model files (pl.payroll.payslip.line from TASK-014)
- New security files
- Changed XML views
- New/changed fields on existing models

## Script: `scripts/upgrade_module.sh`

```bash
#!/bin/bash
# Upgrade l10n_pl_payroll on local Docker Odoo
# Run from the repo root

set -e

COMPOSE_FILE="$HOME/odoo-docker-compose.yml"

echo "Stopping Odoo..."
docker compose -f "$COMPOSE_FILE" stop odoo

echo "Running upgrade..."
docker compose -f "$COMPOSE_FILE" run --rm odoo \
  odoo -d omdev -u l10n_pl_payroll --stop-after-init

echo "Starting Odoo..."
docker compose -f "$COMPOSE_FILE" start odoo

echo "Done! Module upgraded. Open http://localhost:8069"
```

## Script: `scripts/seed_and_verify.sh`

A wrapper that:
1. Runs `scripts/upgrade_module.sh`
2. Waits 5 seconds for Odoo to start
3. Runs `scripts/seed_realistic_data.py` (from TASK-015)
4. Prints "All done!"

```bash
#!/bin/bash
set -e

echo "=== Step 1: Upgrade module ==="
bash scripts/upgrade_module.sh

echo "=== Step 2: Wait for Odoo to start ==="
sleep 5

echo "=== Step 3: Seed test data ==="
python3 scripts/seed_realistic_data.py

echo "=== All done! ==="
echo "Open http://localhost:8069 and go to Payroll > Payslips"
```

## Files to create

- `scripts/upgrade_module.sh`
- `scripts/seed_and_verify.sh`
- Both should be executable (`chmod +x`)

## Important

- These are simple shell scripts, not Python
- They depend on docker-compose being installed and configured
- They are helpers for local development, not production tools
- Add a brief `scripts/README.md` explaining what each script does
