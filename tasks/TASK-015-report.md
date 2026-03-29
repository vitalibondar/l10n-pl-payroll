# TASK-015 Report

## Що зроблено

- Додано `scripts/seed_realistic_data.py` — standalone XML-RPC seed-скрипт на stdlib.
- Скрипт чистить старі `pl.payroll.payslip`, `pl.payroll.creative.report`, `hr.contract`, `hr.employee` (крім admin id=1) і цільові департаменти.
- Скрипт створює 5 департаментів, 20 фіктивних працівників, 20 контрактів і 264 payslip-и за період від старту контракту до `2026-02-01`.
- Для працівників з `kup_type=autorskie` скрипт також створює accepted creative reports, щоб дані були реалістичні й звʼязувалися з payslip-ами.
- Якщо модель `pl.payroll.payslip.line` існує, скрипт додає 5 bonus/deduction line items і повторно compute + confirm для відповідних payslip-ів.

## Як перевіряв

```bash
bash scripts/upgrade_module.sh
python3 scripts/seed_realistic_data.py
```

## Результат запуску

- Employees created: `20`
- Contracts created: `20`
- Payslips created: `264`
- Creative reports created: `42`
- Payslip line adjustments applied: `5`
- Payslip failures: `0`

## Summary table output

```text
Employee                 | Months | Total Gross | Total Net | Avg Net/Month
-------------------------+--------+-------------+-----------+--------------
Tomasz Kowalski          |     14 |   67,284.00 | 49,021.22 |     3,501.52
Anna Wiśniewska          |     14 |   67,284.00 | 49,021.22 |     3,501.52
Piotr Mazur              |     14 |   67,084.00 | 48,889.17 |     3,492.08
Katarzyna Nowak          |     14 |   67,284.00 | 49,021.22 |     3,501.52
Wojciech Zieliński       |     14 |   67,284.00 | 49,021.22 |     3,501.52
Ewa Krawczyk             |     14 |   67,284.00 | 49,021.22 |     3,501.52
Oleksandr Kovalenko      |     12 |   57,672.00 | 42,018.76 |     3,501.56
Nataliia Shevchenko      |     12 |   57,672.00 | 42,018.76 |     3,501.56
Dmytro Melnyk            |     12 |   57,672.00 | 42,018.76 |     3,501.56
Yuliia Kravchuk          |     12 |   57,672.00 | 42,018.76 |     3,501.56
Mikołaj Szymański        |     14 |  107,000.00 | 75,229.54 |     5,373.54
Paulina Dąbrowska        |      9 |   58,500.00 | 41,574.45 |     4,619.38
Kacper Wójcik            |     14 |   84,000.00 | 60,052.02 |     4,289.43
Michał Adamski           |     14 |  113,000.00 | 81,694.98 |     5,835.36
Natalia Ivanchuk         |     11 |   52,866.00 | 38,517.03 |     3,501.55
Monika Brzeska           |     14 |   77,000.00 | 57,113.34 |     4,079.52
Liudmyla Savchenko       |     14 |   98,000.00 | 69,291.38 |     4,949.38
Szymon Jankowski         |     14 |  119,000.00 | 85,809.42 |     6,129.24
Aleksander Volkov        |     14 |  215,000.00 | 139,494.32 |     9,963.88
Marta Lewandowska        |     14 |  171,000.00 | 121,468.89 |     8,676.35
-------------------------+--------+-------------+-----------+--------------
TOTAL                    |    264 | 1,729,558.00 | 1,232,315.68 |            -
```

## Verification snapshots

- `Aleksander Volkov`, payslip `2026-01-01`: `gross=15000.00`, `pit_advance=1550.16`, `pit_due=1250.00`, `state=confirmed`
- `Michał Adamski`, payslip `2025-01-01`: `health_basis=6903.20`, `kup_amount=1725.80`, `pit_due=335.00`, `creative_report_id` linked
- `Monika Brzeska`, payslip `2025-01-01`: `ppk_ee=0.00`, `net=4079.81`, `state=confirmed`
- `Oleksandr Kovalenko`: `12` payslips total, тобто пізній старт з `2025-03-01` працює
- Bonus/deduction lines created: `5`

## Idempotency check

- Seed прогнано двічі поспіль.
- На другому прогоні cleanup прибрав рівно попередній набір даних: `5` payslip lines, `264` payslips, `42` creative reports, `20` contracts, `20` employees, `5` departments.
- Після повторного створення фінальний стан лишився тим самим: `20` employees, `20` contracts, `264` payslips, `42` creative reports, `5` payslip lines.

## Важлива фактична нотатка

- У тексті задачі було припущення, що `Aleksander Volkov` перетне верхній PIT bracket „around August 2025”.
- Після реального прогону з цим модулем перехід стається пізніше: перші підвищені значення видно з payslip `2025-10-01`.
- Причина: модуль рахує PIT від `taxable_income`, а не від gross. Для Volkov це `12918.00` на місяць у звичайні місяці, тому поріг `120000` перетинається не в серпні.
