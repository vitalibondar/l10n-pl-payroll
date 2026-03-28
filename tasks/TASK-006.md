# TASK-006: Cumulative YTD tracking — PIT brackets + ZUS basis cap

**Status:** open
**Assignee:** codex
**Depends on:** TASK-005 (payslip model must exist)
**Phase:** 2.2

## Контекст
Польський PIT рахується кумулятивно за рік, а не помісячно. Аналогічно, ZUS має річний ліміт бази (282 600 PLN в 2026). Обидва механізми вимагають, щоб кожен payslip знав підсумки всіх попередніх місяців того самого року.

Читай: CLAUDE.md → LESSONS.md (перші два записи — саме про це) → DECISIONS.md

## Задача

### 1. Helper: `_get_ytd_totals(employee_id, year, before_date)`

Метод, який збирає суми з усіх confirmed payslips працівника за рік **до** поточного місяця:

```python
def _get_ytd_totals(self, employee_id, year, before_date):
    """Returns dict with YTD totals from confirmed payslips."""
    payslips = self.search([
        ('employee_id', '=', employee_id),
        ('state', '=', 'confirmed'),
        ('date_from', '>=', date(year, 1, 1)),
        ('date_from', '<', before_date),
    ])
    return {
        'gross': sum(payslips.mapped('gross')),
        'zus_basis': sum(payslips.mapped('gross')),  # = cumulative gross for ZUS cap
        'taxable_income': sum(payslips.mapped('taxable_income')),
        'pit_paid': sum(payslips.mapped('pit_due')),
    }
```

### 2. Cumulative PIT у compute_payslip()

Модифікувати PIT-логіку в TASK-005:

```
ytd = _get_ytd_totals(employee, year, date_from)
cumulative_taxable = ytd['taxable_income'] + current_month_taxable

threshold = get_value('PIT_THRESHOLD')  # 120 000

# PIT on cumulative
if cumulative_taxable <= threshold:
    pit_cumulative = cumulative_taxable × PIT_RATE_1 / 100
else:
    pit_cumulative = threshold × PIT_RATE_1 / 100 + (cumulative_taxable - threshold) × PIT_RATE_2 / 100

# Minus reducing (cumulative)
months_count = number_of_payslips_in_year_including_current
reducing_cumulative = PIT_REDUCING × months_count (if pit2_filed)

# Minus already paid
pit_due_this_month = pit_cumulative - reducing_cumulative - ytd['pit_paid']
pit_due_this_month = max(0, round_down_to_int(pit_due_this_month))
```

### 3. ZUS basis cap

Модифікувати ZUS-логіку:

```
ytd = _get_ytd_totals(...)
zus_cap = get_value('ZUS_BASIS_CAP')  # 282 600
cumulative_gross_before = ytd['gross']
cumulative_gross_after = cumulative_gross_before + current_gross

if cumulative_gross_before >= zus_cap:
    # Повністю перевищено — emerytalne і rentowe = 0
    zus_emery_ee = 0
    zus_rent_ee = 0
elif cumulative_gross_after > zus_cap:
    # Частковий місяць — рахуємо лише від залишку
    remaining = zus_cap - cumulative_gross_before
    zus_emery_ee = remaining × rate / 100
    zus_rent_ee = remaining × rate / 100
else:
    # Нормальний розрахунок
    zus_emery_ee = gross × rate / 100

# CHOROBOWE завжди нараховується (не має cap)
# HEALTH завжди нараховується
# Employer-side emerytalne і rentowe — аналогічний cap
```

### 4. Ulga limits (спрощена реалізація)

Ulga dla młodych та інші мають річний ліміт доходу (зазвичай = PIT_THRESHOLD). Якщо cumulative gross перевищує ліміт, ulga зникає і PIT починає нараховуватися.

```
ulga_limit = get_value('PIT_THRESHOLD')  # 120 000 (used as ulga limit too)
if contract.ulga_type != 'none':
    if ytd['gross'] + current_gross > ulga_limit:
        # Ulga вичерпана — рахувати PIT нормально
```

### 5. Тести

Сценарій 10 (Andrzej Dąbrowski) — тепер можна тестувати:
- Попередні місяці мали cumulative taxable = 100 000
- Поточний місяць: taxable = 25 637
- Перехід через threshold: 20 000 × 12% + 5 637 × 32%

Додатковий тест: employee з 12 payslips (January-December), перевірити що cumulative PIT за рік = річний PIT.

Тест на ZUS cap: employee з gross 25 000/month, у грудні (місяць 12) cumulative = 275 000 → залишок до cap = 7 600 → ZUS лише від 7 600.

## Expected Output
1. Modified `l10n_pl_payroll/models/pl_payroll_payslip.py` — cumulative logic
2. `l10n_pl_payroll/tests/test_cumulative.py` — YTD tests
3. Update `tasks/TASK-006.md` status

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main && git pull
git checkout -b task/006-cumulative-ytd

git add l10n_pl_payroll/models/pl_payroll_payslip.py
git add l10n_pl_payroll/tests/test_cumulative.py
git add tasks/TASK-006.md
git commit -m "[TASK-006] Add cumulative YTD PIT and ZUS basis cap tracking"
git push -u origin task/006-cumulative-ytd
gh pr create --title "[TASK-006] Cumulative PIT and ZUS cap" --body "Year-to-date PIT bracket tracking and ZUS annual basis cap. Tests for PIT threshold transition and partial ZUS month."
```

## Acceptance Criteria
- [ ] Cumulative PIT: monthly PIT considers all prior months' taxable income
- [ ] PIT bracket transition: month where cumulative crosses 120k pays split rate
- [ ] ZUS basis cap: pension+disability stop after annual cap, health continues
- [ ] Partial month ZUS: when cap is reached mid-month, only remaining base is taxed
- [ ] Ulga limits: when cumulative income exceeds limit, ulga stops
- [ ] Scenario 10 test passes
- [ ] Full-year (12 month) cumulative test passes
- [ ] ZUS cap test passes

## Notes
- PPK employer contribution is taxable income for employee — це додає до taxable_income для PIT purposes. Реалізувати тут якщо не зроблено в TASK-005.
- Chorobowe не має cap — завжди нараховується від gross
- Employer-side ZUS (emerytalne, rentowe) теж має cap — аналогічна логіка
