# TASK-029 Report

## Що зроблено

- Дороблено `scripts/seed_realistic_data.py` для сценарію одного працівника `Marek Jabłoński` з двома контрактами.
- Створення `hr.employee` тепер пропускає повторне створення працівника з тим самим `name`.
- Створення `hr.contract` тепер прив’язується до запису `EMPLOYEES` через `index`, а не через `name`, тому два контракти Марека не перетирають один одного.
- Для контракту з `date_end` seed ставить `state=close`, записує `date_end` і обмежує генерацію payslips місяцем завершення.
- `build_summary` більше не ітерується по дубльованому списку `EMPLOYEES`, тому Marek Jabłoński не дублюється в summary.
- Фінальний print більше не рахує контракти через `len(contract_ids)`; тепер показує фактичну кількість створених контрактів і додає `Expected payslips`.

## Перевірка

### 1. Синтаксис

Команда:

```bash
python3 -m py_compile scripts/seed_realistic_data.py
```

Результат: пройшла без помилок.

### 2. Upgrade локального Odoo

Команда:

```bash
bash scripts/upgrade_module.sh
```

Результат: upgrade завершився успішно 2026-03-29; контейнер `vb-odoo-1` перезапущено, модуль `l10n_pl_payroll` завантажився без помилок.

### 3. Seed

Команда:

```bash
python3 scripts/seed_realistic_data.py
```

Ключові результати:

- `Employees created: 24`
- `Contracts created: 25`
- `Expected payslips: 296`
- `Payslip failures: 0`

У summary є рівно один рядок для `Marek Jabłoński`:

```text
Marek Jabłoński          |     14 |   66,800.00 | 47,026.78 |     3,359.06
```

### 4. Точкова XML-RPC перевірка сценарію Марека

Запущено тимчасову перевірку через XML-RPC з кореня репо:

```bash
PYTHONPATH=/Users/vb/l10n-pl-payroll python3 /tmp/l10n-pl-payroll-task029/verify_marek_seed.py
```

Результат:

- `marek_employee_count = 1`
- `marek_contract_count = 2`
- `seeded_employee_count = 24`
- `contract_count = 25`
- `payslip_count = 296`
- `expected_payslip_count = 296`
- `marek_summary_line_count = 1`

Контракти Марека:

1. `TASK-015/24 Marek Jabłoński`
   - тип: `Umowa zlecenie`
   - `wage = 4200.0`
   - `date_start = 2025-01-01`
   - `date_end = 2025-06-30`
   - `state = close`
   - payslips: 6
   - місяці: `2025-01`, `2025-02`, `2025-03`, `2025-04`, `2025-05`, `2025-06`

2. `TASK-015/25 Marek Jabłoński`
   - тип: `Umowa o pracę`
   - `wage = 5200.0`
   - `date_start = 2025-07-01`
   - `date_end = False`
   - `state = open`
   - payslips: 8
   - місяці: `2025-07`, `2025-08`, `2025-09`, `2025-10`, `2025-11`, `2025-12`, `2026-01`, `2026-02`

### 5. Інтеграційна регресійна перевірка

Команда:

```bash
python3 scripts/verify_calculations.py
```

Результат:

- `TOTAL_FAILURES=0`
- `Marek Jabłoński | 14 | 0 | 0.00`
- PIT-11 check: `Records: 24 / expected 24`, `Differences: 0`
- ZUS DRA check: `Records: 1 / expected 1`, `Differences: 0`
- Batch wizard check: `Deleted payslips: 24`, `Recreated payslips: 24`, `Differences: 0`

## Висновок

- Асин сценарій з одним працівником і двома контрактами працює.
- Існуючі seeded employees не зламалися.
- Окремий regression test у `tests/` не додавався: наявна інтеграційна перевірка `scripts/verify_calculations.py` уже покрила загальний регресійний ризик без роздування репо.
