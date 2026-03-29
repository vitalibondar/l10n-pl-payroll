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
