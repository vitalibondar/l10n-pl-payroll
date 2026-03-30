#!/bin/bash

set -e

echo "=== Step 1: Upgrade module ==="
bash scripts/upgrade_module.sh

echo "=== Step 2: Wait for Odoo XML-RPC ==="
python3 - <<'PY'
import http.client
import socket
import sys
import time
import xmlrpc.client

url = "http://localhost:8069/xmlrpc/2/common"
deadline = time.monotonic() + 120
attempt = 1
last_error = None

while time.monotonic() < deadline:
    try:
        xmlrpc.client.ServerProxy(url, allow_none=True).version()
        print("Odoo XML-RPC is ready.")
        sys.exit(0)
    except (
        OSError,
        socket.timeout,
        http.client.RemoteDisconnected,
        xmlrpc.client.ProtocolError,
        xmlrpc.client.Fault,
    ) as exc:
        last_error = exc
        print(f"Waiting for Odoo XML-RPC ({attempt})... {exc}", flush=True)
        attempt += 1
        time.sleep(2)

print(f"Odoo XML-RPC did not become ready in time. Last error: {last_error}", file=sys.stderr)
sys.exit(1)
PY

echo "=== Step 3: Seed test data ==="
python3 scripts/seed_realistic_data.py

echo "=== All done! ==="
echo "Open http://localhost:8069 and go to Payroll > Payslips"
