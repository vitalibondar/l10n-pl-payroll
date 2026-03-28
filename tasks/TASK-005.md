# TASK-005: Payslip model + salary rules for umowa o pracę

**Status:** open
**Assignee:** codex
**Depends on:** TASK-002 (parameters), TASK-003 (security), TASK-004 (contract extension)
**Phase:** 2.1

## Контекст
Це головна задача модуля — модель payslip і повний ланцюг розрахунку gross-to-net для umowa o pracę.

Читай: CLAUDE.md → LESSONS.md → DECISIONS.md → ODOO_RECON.md → tasks/TASK-001-research.md (architecture recommendations)

**КРИТИЧНО (з LESSONS.md):** Формула авторських KUP = 50% × creative_share% × health_basis. Поле `kup_autorskie_pct` = відсоток творчої роботи, НЕ ставка KUP. Ставка завжди 50%.

## Задача

### 1. Модель `pl.payroll.payslip`

```python
# models/pl_payroll_payslip.py
class PlPayrollPayslip(models.Model):
    _name = 'pl.payroll.payslip'
    _description = 'Polish Payroll Payslip'
    _order = 'date_from desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    contract_id = fields.Many2one('hr.contract', required=True)
    company_id = fields.Many2one('res.company', related='contract_id.company_id', store=True)
    date_from = fields.Date(required=True)  # перший день місяця
    date_to = fields.Date(required=True)    # останній день місяця
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='draft')

    # Inputs
    gross = fields.Float(related='contract_id.wage', readonly=True)

    # ZUS employee
    zus_emerytalne_ee = fields.Float()
    zus_rentowe_ee = fields.Float()
    zus_chorobowe_ee = fields.Float()
    zus_total_ee = fields.Float()

    # Health
    health_basis = fields.Float()
    health = fields.Float()

    # KUP
    kup_amount = fields.Float()

    # PIT
    taxable_income = fields.Float()
    pit_advance = fields.Float()
    pit_reducing = fields.Float()
    pit_due = fields.Float()

    # PPK
    ppk_ee = fields.Float()

    # NET
    net = fields.Float()

    # Employer-side (not deducted from employee, informational)
    zus_emerytalne_er = fields.Float()
    zus_rentowe_er = fields.Float()
    zus_wypadkowe_er = fields.Float()
    zus_fp = fields.Float()
    zus_fgsp = fields.Float()
    ppk_er = fields.Float()
    total_employer_cost = fields.Float()  # gross + all employer contributions

    # Audit trail
    notes = fields.Text()
```

### 2. Метод `compute_payslip()`

Основний метод розрахунку. Ланцюг для umowa o pracę (single month, без cumulative — це TASK-006):

```
1. GROSS = contract.wage
2. ZUS EE:
   - emerytalne = GROSS × get_value('ZUS_EMERY_EE') / 100
   - rentowe = GROSS × get_value('ZUS_RENT_EE') / 100
   - chorobowe = GROSS × get_value('ZUS_CHOR_EE') / 100
   - total_ee = sum of above
3. HEALTH_BASIS = GROSS - ZUS_TOTAL_EE
4. HEALTH = HEALTH_BASIS × get_value('HEALTH') / 100
5. KUP:
   if contract.kup_type == 'standard':
       kup = get_value('KUP_STANDARD')
   elif contract.kup_type == 'autorskie':
       kup = HEALTH_BASIS × contract.kup_autorskie_pct / 100 × 0.5
   elif contract.kup_type == 'standard_20':
       kup = HEALTH_BASIS × 0.20
6. TAXABLE_INCOME = HEALTH_BASIS - KUP → round down to integer
7. PIT:
   if contract.ulga_type in ('mlodzi', 'na_powrot', 'rodzina_4_plus', 'senior'):
       pit_due = 0  # (спрощено для Phase 2, cumulative limits — TASK-006)
   else:
       pit_advance = TAXABLE_INCOME × get_value('PIT_RATE_1') / 100
       pit_reducing = get_value('PIT_REDUCING') if contract.pit2_filed else 0
       pit_due = max(0, pit_advance - pit_reducing) → round down to integer
8. PPK EE:
   if contract.ppk_participation == 'opt_out':
       ppk_ee = 0
   elif contract.ppk_participation == 'reduced':
       ppk_ee = GROSS × get_value('PPK_EE_REDUCED') / 100
   else:
       ppk_ee = GROSS × contract.ppk_ee_rate / 100
   # additional voluntary:
   ppk_ee += GROSS × contract.ppk_additional / 100
9. NET = GROSS - ZUS_TOTAL_EE - HEALTH - PIT_DUE - PPK_EE
10. EMPLOYER-SIDE:
    - emerytalne_er = GROSS × get_value('ZUS_EMERY_ER') / 100
    - rentowe_er = GROSS × get_value('ZUS_RENT_ER') / 100
    - wypadkowe_er = GROSS × get_value('ZUS_WYPAD_ER', company_id=company) / 100
    - fp = GROSS × get_value('ZUS_FP') / 100
    - fgsp = GROSS × get_value('ZUS_FGSP') / 100
    - ppk_er = GROSS × get_value('PPK_ER') / 100 (if PPK participant)
    - total_employer_cost = GROSS + sum of employer contributions
```

### 3. Rounding rules

Polish payroll має специфічні правила округлення:
- ZUS складки: округлення до копійок (2 decimal places, standard rounding)
- Taxable income: округлення ВНИЗ до цілих злотих (floor to integer)
- PIT advance: округлення ВНИЗ до цілих злотих (floor to integer)
- Health: округлення до копійок (standard rounding)
- NET: результат без додаткового округлення (2 decimal places)

### 4. Тести

Unit tests, які використовують expected_results.py для валідації:

```python
# tests/test_payslip.py
# Для кожного зі сценаріїв 1-7 і 11 (umowa o pracę):
# 1. Створи payslip для відповідного contract
# 2. Виклич compute_payslip()
# 3. Порівняй кожне поле з expected_results[N]
```

Сценарій 10 (Dąbrowski, PIT bracket transition) пропустити — це cumulative PIT (TASK-006).
Сценарії 8, 9 (zlecenie) пропустити — це TASK окремий.

## Expected Output
1. `l10n_pl_payroll/models/pl_payroll_payslip.py`
2. `l10n_pl_payroll/tests/test_payslip.py`
3. Update `models/__init__.py`
4. Update `security/ir.model.access.csv` — add access for payslip model
5. Update `security/pl_payroll_security.xml` — add own-payslip record rule
6. Update `__manifest__.py`

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main && git pull
git checkout -b task/005-payslip-model

# Прочитай: CLAUDE.md → LESSONS.md → DECISIONS.md → tasks/TASK-001-research.md → цей файл

git add l10n_pl_payroll/models/pl_payroll_payslip.py
git add l10n_pl_payroll/models/__init__.py
git add l10n_pl_payroll/tests/test_payslip.py
git add l10n_pl_payroll/security/ir.model.access.csv
git add l10n_pl_payroll/security/pl_payroll_security.xml
git add l10n_pl_payroll/__manifest__.py
git add tasks/TASK-005.md
git commit -m "[TASK-005] Add payslip model with gross-to-net salary rules for umowa o pracę"
git push -u origin task/005-payslip-model
gh pr create --title "[TASK-005] Payslip model and salary rules" --body "Complete gross-to-net calculation chain for umowa o pracę. Payslip model with ZUS/Health/KUP/PIT/PPK computation. Unit tests against 8 scenarios from expected_results.py."
```

## Acceptance Criteria
- [ ] Payslip model created with all fields
- [ ] compute_payslip() implements full chain
- [ ] All rates fetched via pl.payroll.parameter.get_value() — no hardcoded values
- [ ] Autorskie KUP = 50% × creative_share × health_basis (see LESSONS.md!)
- [ ] Rounding: taxable income → floor to int, PIT due → floor to int, ZUS → 2 decimal standard
- [ ] Tests pass for scenarios 1, 2, 3, 4, 5, 6, 7, 11
- [ ] Security: own-payslip record rule added
- [ ] Access CSV updated for payslip model

## Notes
- Scenario 10 (PIT bracket transition) is TASK-006 — skip in tests
- Scenarios 8, 9 (zlecenie) are a separate task — skip
- Scenario 12 (ulga na powrót) — ulga logic is simplified (pit_due=0); cumulative limit checking is TASK-006
- PPK employer contribution is taxable income for employee (see LESSONS.md) — implement this in TASK-006
- This is single-month calculation. Cumulative PIT and ZUS cap are in TASK-006
