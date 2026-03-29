# TASK-029: Multi-contract seed scenario for one employee

**Status:** done
**Assignee:** codex
**Branch:** task/029-multi-contract-seed
**Created:** 2026-03-29
**Depends on:** TASK-028
**Phase:** 2.0

## Контекст

- `origin/main` оновився під час старту роботи; ця задача виконується на чистій гілці `task/029-multi-contract-seed`, створеній від актуального `main`.
- У локальному `main` був незакомічений частковий патч у `scripts/seed_realistic_data.py` під бізнес-запит Асі. Його не можна переносити сліпо:
  - `build_summary` дублює Marek Jabłoński і завищує totals.
  - фінальний рядок `Contracts created` бере `len(contract_ids)` і покаже 24 замість 25.
- Чужий локальний бруд (`RUNBOOK.md`, `STATE.md`, `tasks/TASK-027.md`, `tasks/TASK-028.md`, `codex-prompts/CODEX-027.md`, `codex-prompts/CODEX-028.md`) не входить у цю задачу.

## Задача

Дороби `scripts/seed_realistic_data.py`, щоб seed створював один сценарій працівника з двома контрактами:

1. Один `hr.employee` для Marek Jabłoński.
2. Два `hr.contract` для цього employee:
   - контракт 1: `umowa zlecenie`, `wage=4200.0`, `date_start=2025-01-01`, `date_end=2025-06-30`, `state=close`
   - контракт 2: `umowa o pracę`, `wage=5200.0`, `date_start=2025-07-01`, без `date_end`, `state=open`
3. Payslips тільки в потрібних діапазонах:
   - 2025-01 .. 2025-06 для `zlecenie`
   - 2025-07 .. 2026-02 для `o_prace`
4. У сумі для Marek має бути 14 payslips.
5. Існуючі seeded employees не мають зламатися.

## Input

- `scripts/seed_realistic_data.py`
- локальний частковий diff, збережений перед `stash`
- команди перевірки:
  - `python3 -m py_compile scripts/seed_realistic_data.py`
  - `bash scripts/upgrade_module.sh` якщо локальний Odoo доступний
  - `python3 scripts/seed_realistic_data.py` якщо локальний Odoo доступний

## Expected Output

- Оновлений `scripts/seed_realistic_data.py` без дублювання employee за ключем `name`.
- `tasks/TASK-029-report.md` з точними результатами перевірки.
- `codex-prompts/CODEX-029.md` з коротким codex prompt для цієї задачі.

## Acceptance Criteria

- [x] Створюється рівно один `hr.employee` для Marek Jabłoński.
- [x] Створюються рівно два `hr.contract` для Marek Jabłoński з правильними датами, типами і `state`.
- [x] Для першого контракту є 6 payslips за 2025-01 .. 2025-06.
- [x] Для другого контракту є 8 payslips за 2025-07 .. 2026-02.
- [x] `build_summary` не дублює Marek Jabłoński.
- [x] Фінальні лічильники після seed:
  - `Employees created: 24`
  - `Contracts created: 25`
  - `Expected payslips: 296`
- [x] `python3 -m py_compile scripts/seed_realistic_data.py` проходить.
- [x] Якщо локальний Odoo доступний: upgrade, seed і перевірка сценарію проходять.

## Notes

- Зміни мають лишитися простими: без нової архітектури, без зайвих features.
- Перевір місця, де ключем виступає `employee["name"]`: `create_employees`, `create_contracts`, `expected_payslip_count`, `create_payslips`, `build_summary`, фінальний summary print і пов’язані допоміжні структури.
- Якщо доречний малий regression test без роздування репо — додай. Якщо ні — зроби надійну інтеграційну перевірку і задокументуй її в report.

## Git Workflow

```bash
cd /Users/vb/l10n-pl-payroll
git checkout main
git pull --ff-only
git checkout -b task/029-multi-contract-seed

# після завершення
git add scripts/seed_realistic_data.py tasks/TASK-029.md tasks/TASK-029-report.md codex-prompts/CODEX-029.md
git commit -m "[TASK-029] Add multi-contract seed scenario"
git push -u origin task/029-multi-contract-seed
gh pr create --title "[TASK-029] Add multi-contract seed scenario" --body "Add multi-contract Marek Jabłoński seed scenario and verification report."
```
