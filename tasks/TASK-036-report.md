# TASK-036 Report

## Що було зламано

- `scripts/seed_and_verify.sh` чекав рівно 5 секунд після рестарту Odoo.
- Якщо Odoo ще не був готовий до XML-RPC, `scripts/seed_realistic_data.py` падав на `common.authenticate(...)` з `RemoteDisconnected`.
- `scripts/verify_calculations.py` мав окремий крихкий `connect()` без retry.

## Що виправлено

- У `scripts/seed_realistic_data.py` додано retry/readiness на XML-RPC `version()` + `authenticate()`.
- У `scripts/verify_calculations.py` прибрано дубльований connect; тепер він використовує надійний connect із seed-скрипта.
- У `scripts/seed_and_verify.sh` замінено `sleep 5` на реальне очікування готовності XML-RPC.
- У `scripts/README.md` оновлено опис поведінки.

## Як перевірено

- `python3 -m py_compile scripts/seed_realistic_data.py scripts/verify_calculations.py`
- `bash scripts/seed_and_verify.sh`
- `python3 scripts/verify_calculations.py`

## Результат

- Локальний сценарій `upgrade -> seed` більше не вимагає ручного перезапуску через race condition на старті Odoo.
- Перевірка розрахунків після seed завершилась з `TOTAL_FAILURES=0`.
