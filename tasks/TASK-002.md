# TASK-002: Design and implement pl.payroll.parameter model

**Status:** open
**Assignee:** codex
**Depends on:** TASK-001 (for architectural context, but can start in parallel)
**Phase:** 1.4

## Контекст
Всі ставки й пороги (ZUS, PIT, PPK, мінімалка) змінюються щорічно, іноді серед року. Hardcoded values зламають історичні розрахунки при оновленні. Тому всі параметри зберігаються в окремій моделі з date-effective versioning (DEC-002).

Читай: CLAUDE.md → DECISIONS.md (DEC-002) → LESSONS.md

## Задача
Створити модель `pl.payroll.parameter` та заповнити початковими даними.

### Модель

```python
# models/pl_payroll_parameter.py
class PlPayrollParameter(models.Model):
    _name = 'pl.payroll.parameter'
    _description = 'Polish Payroll Parameter'
    _order = 'code, date_from desc'

    name = fields.Char(required=True)         # "ZUS emerytalne employee"
    code = fields.Char(required=True, index=True)  # "ZUS_EMERY_EE"
    value = fields.Float(required=True)        # 9.76 (відсоток) або 282600 (сума)
    date_from = fields.Date(required=True)     # Початок дії
    date_to = fields.Date()                    # Кінець дії (None = безстроково)
    value_type = fields.Selection([
        ('percent', 'Відсоток'),
        ('amount', 'Сума'),
    ], required=True)
    company_id = fields.Many2one('res.company')  # Якщо per-company (wypadkowe)
    note = fields.Text()                       # Пояснення, посилання на закон
```

### Helper method
```python
@api.model
def get_value(self, code, date=None, company_id=None):
    """Get parameter value effective on given date."""
    # Returns the value of parameter with given code
    # that is effective on the given date (or today)
```

### Початкові дані (2025 + 2026)

Створити XML-файли `data/pl_payroll_parameters_2025.xml` та `data/pl_payroll_parameters_2026.xml`.

Параметри (мінімальний набір):

| Code | Name | 2025 value | 2026 value | Type |
|---|---|---|---|---|
| ZUS_EMERY_EE | ZUS emerytalne employee | 9.76 | 9.76 | percent |
| ZUS_RENT_EE | ZUS rentowe employee | 1.50 | 1.50 | percent |
| ZUS_CHOR_EE | ZUS chorobowe employee | 2.45 | 2.45 | percent |
| ZUS_EMERY_ER | ZUS emerytalne employer | 9.76 | 9.76 | percent |
| ZUS_RENT_ER | ZUS rentowe employer | 6.50 | 6.50 | percent |
| ZUS_WYPAD_ER | ZUS wypadkowe employer (default) | 1.67 | 1.67 | percent |
| ZUS_FP | Fundusz Pracy | 2.45 | 2.45 | percent |
| ZUS_FGSP | FGŚP | 0.10 | 0.10 | percent |
| ZUS_BASIS_CAP | Roczna podstawa wymiaru składek | 260190 | 282600 | amount |
| HEALTH | Health insurance | 9.00 | 9.00 | percent |
| PIT_RATE_1 | PIT first bracket | 12.00 | 12.00 | percent |
| PIT_RATE_2 | PIT second bracket | 32.00 | 32.00 | percent |
| PIT_THRESHOLD | PIT threshold | 120000 | 120000 | amount |
| PIT_FREE | Kwota wolna od podatku (annual) | 30000 | 30000 | amount |
| PIT_REDUCING | Kwota zmniejszająca podatek (monthly) | 300 | 300 | amount |
| KUP_STANDARD | KUP standard (monthly) | 250 | 250 | amount |
| PPK_EE | PPK employee default | 2.00 | 2.00 | percent |
| PPK_EE_REDUCED | PPK employee reduced | 0.50 | 0.50 | percent |
| PPK_ER | PPK employer default | 1.50 | 1.50 | percent |
| MIN_WAGE | Minimalne wynagrodzenie | 4666 | 4806 | amount |
| MIN_HOURLY | Minimalna stawka godzinowa | 30.50 | 31.40 | amount |

## Expected Output
1. `l10n_pl_payroll/models/pl_payroll_parameter.py`
2. `l10n_pl_payroll/data/pl_payroll_parameters_2025.xml`
3. `l10n_pl_payroll/data/pl_payroll_parameters_2026.xml`
4. Update `__manifest__.py` → add data files to `data` list
5. Update `models/__init__.py`
6. `l10n_pl_payroll/tests/test_parameter.py` — unit tests

## Acceptance Criteria
- [ ] `get_value('ZUS_EMERY_EE', date(2025, 6, 1))` returns 9.76
- [ ] `get_value('MIN_WAGE', date(2026, 1, 1))` returns 4806
- [ ] `get_value('ZUS_BASIS_CAP', date(2025, 12, 31))` returns 260190
- [ ] Date ranges don't overlap for same code
- [ ] Tests pass
- [ ] No hardcoded values in model code

## Notes
- Verify 2025 and 2026 values via web search before committing (see LESSONS.md)
- MIN_HOURLY for 2025 was 30.50 PLN, verify 2026 value
- ZUS wypadkowe varies by company (1.67% is default) — company_id field handles this
