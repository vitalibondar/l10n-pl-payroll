# TASK-036 prompt

```text
Read CLAUDE.md, then LESSONS.md, then tasks/TASK-036.md.

The local upgrade+seed flow is flaky.
After module upgrade, Odoo sometimes closes XML-RPC connections before it is fully ready, and scripts/seed_realistic_data.py crashes with http.client.RemoteDisconnected.

Fix the workflow end-to-end.

Do the work in this order:

1. Make scripts/seed_realistic_data.py resilient to Odoo startup timing by adding readiness/retry logic around XML-RPC connection/authentication.
2. Reuse that logic from scripts/verify_calculations.py instead of duplicating another fragile connect() implementation.
3. Replace the blind sleep in scripts/seed_and_verify.sh with an actual readiness check for Odoo XML-RPC.
4. Update scripts/README.md so it matches the real behavior.
5. Run the full local workflow and confirm it finishes without the startup race.

Hard rules:

- Keep it stdlib-only.
- Fix the root cause, not just the shell script.
- Do not add unnecessary abstractions.

Verification:

- python3 -m py_compile scripts/seed_realistic_data.py scripts/verify_calculations.py
- bash scripts/seed_and_verify.sh

Commit with prefix [TASK-036].
Work on main.
```
