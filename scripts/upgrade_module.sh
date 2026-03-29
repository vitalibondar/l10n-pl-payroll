#!/bin/bash

set -euo pipefail

BASE_COMPOSE_FILE="$HOME/odoo-docker-compose.yml"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-vb}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_COMPOSE_FILE="$(mktemp /tmp/l10n-pl-payroll-compose.XXXXXX.yml)"

trap 'rm -f "$TMP_COMPOSE_FILE"' EXIT

python3 - <<'PY' "$BASE_COMPOSE_FILE" "$REPO_ROOT" "$TMP_COMPOSE_FILE"
from pathlib import Path
import sys

base_compose = Path(sys.argv[1]).read_text(encoding="utf-8")
repo_root = Path(sys.argv[2]).as_posix()
target = "~/l10n-pl-payroll/l10n_pl_payroll"

if target not in base_compose:
    raise SystemExit(f"Expected mount path not found in compose file: {target}")

patched = base_compose.replace(target, f"{repo_root}/l10n_pl_payroll")
Path(sys.argv[3]).write_text(patched, encoding="utf-8")
PY

echo "Using repo root: $REPO_ROOT"
echo "Stopping Odoo..."
docker compose -p "$PROJECT_NAME" -f "$TMP_COMPOSE_FILE" stop odoo

echo "Running upgrade..."
docker compose -p "$PROJECT_NAME" -f "$TMP_COMPOSE_FILE" run --rm odoo \
  odoo -d omdev -u l10n_pl_payroll --stop-after-init

echo "Starting Odoo..."
docker compose -p "$PROJECT_NAME" -f "$TMP_COMPOSE_FILE" start odoo

echo "Done! Module upgraded. Open http://localhost:8069"
