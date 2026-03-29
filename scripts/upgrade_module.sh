#!/bin/bash

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
