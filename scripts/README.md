# Scripts

## `upgrade_module.sh`

Stops the local Odoo container, runs `-u l10n_pl_payroll` on database `omdev`, then starts Odoo again.

Run from the repo root:

```bash
bash scripts/upgrade_module.sh
```

## `seed_and_verify.sh`

Runs the module upgrade, waits 5 seconds, then runs `scripts/seed_realistic_data.py`.

Run from the repo root:

```bash
bash scripts/seed_and_verify.sh
```

If `scripts/seed_realistic_data.py` does not exist yet, the second script will fail at the seed step.
