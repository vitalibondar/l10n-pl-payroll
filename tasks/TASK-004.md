# TASK-004: Generate fictional test contracts covering all payroll scenarios

**Status:** open
**Assignee:** codex
**Depends on:** TASK-002 (parameter model)
**Phase:** 0.6 / 3.1

## Контекст
Розробка йде повністю на фіктивних даних. Жодних реальних імен, PESEL, зарплат. Тестові контракти покривають ВСІ можливі комбінації, які модуль має підтримувати. Кожен fixture = окремий сценарій для тестування salary rules.

Читай: CLAUDE.md → DECISIONS.md (DEC-005, DEC-007) → LESSONS.md

## Задача

### 1. PESEL generator
Скрипт `tools/test_data_gen.py`, який генерує:
- Фіктивні PESEL-номери (правильний формат 11 цифр, дата народження валідна, але **контрольна цифра НЕВАЛІДНА** — щоб точно не збігся з реальною людиною)
- Фіктивні імена (польські + українські, обидві статі)
- Фіктивні адреси
- NIP компанії (теж фіктивний)

### 2. Тестові контракти (fixtures)
Створити набір XML/Python fixtures, які створюють hr.employee + hr.contract записи в Odoo.

**Мінімальний набір сценаріїв:**

| # | Імʼя (фіктивне) | Тип контракту | Brutto | KUP | PPK | Ulga | Примітки |
|---|---|---|---|---|---|---|---|
| 1 | Jan Kowalski | o pracę, повний етат | 6 000 PLN | standard (250) | 2% default | — | Базовий випадок |
| 2 | Anna Nowak | o pracę, повний етат | 15 000 PLN | autorskie 50% | 2% default | — | Авторські koszty |
| 3 | Piotr Wiśniewski | o pracę, повний етат | 12 000 PLN | standard | opt-out | — | PPK відмова |
| 4 | Maria Wójcik | o pracę, повний етат | 4 806 PLN | standard | 2% | — | Мінімалка 2026 |
| 5 | Jakub Kamiński | o pracę, 0.5 етату | 3 000 PLN | standard | 2% | — | Частковий етат |
| 6 | Oleg Shevchenko | o pracę, повний етат | 8 000 PLN | standard | 2% | dla młodych | Вік < 26 |
| 7 | Katarzyna Lewandowska | o pracę, повний етат | 25 000 PLN | standard | 2% + 2% dodatkowa | — | PPK з доп. внесками |
| 8 | Tomasz Zieliński | zlecenie, годинна | 35 PLN/год | 20% standard | — | — | Zlecenie базовий |
| 9 | Natalia Kravchuk | zlecenie, годинна | 40 PLN/год | autorskie 50% | — | — | Zlecenie + авторські |
| 10 | Andrzej Dąbrowski | o pracę, повний етат | 30 000 PLN | standard | 2% | — | Висока зарплата (PIT 32% перехід) |
| 11 | Ewa Majewska | o pracę, повний етат | 9 000 PLN | standard | 0.5% reduced | — | PPK зменшена ставка |
| 12 | Olena Bondarenko | o pracę, повний етат | 7 500 PLN | autorskie 80% | 2% | na powrót | Повертач + високі авторські |

**Кожен контракт має включати:**
- employee: name, PESEL (фіктивний!), birthday, gender, country_id
- contract: type, wage, date_start, resource_calendar_id
- Наші кастомні поля: kup_type, kup_autorskie_pct, ppk_participation, ppk_ee_rate, ppk_additional, pit2_filed, ulga_type, zus_code

### 3. Очікувані результати розрахунку
Для кожного з 12 сценаріїв — **ручний розрахунок** gross-to-net із проміжними кроками. Формат:

```
# Сценарій 1: Jan Kowalski — базовий o pracę
Gross: 6 000.00
ZUS emerytalne EE (9.76%): -585.60
ZUS rentowe EE (1.50%): -90.00
ZUS chorobowe EE (2.45%): -147.00
= Basis for health: 5 177.40
Health (9%): -465.97
KUP standard: 250.00
Taxable income: 4 927.40 → rounded: 4 927.00
PIT advance (12%): 591.24
minus kwota zmniejszająca: -300.00
PIT due: 291.24 → rounded: 291.00
PPK EE (2% of gross): -120.00
NET: 6000 - 585.60 - 90.00 - 147.00 - 465.97 - 291.00 - 120.00 = 4 300.43
```

Зберегти як `tools/expected_results.py` (dict із номером сценарію → очікувані значення) — це буде використано в unit tests.

### 4. Disclaimer
Кожен файл з тестовими даними має містити коментар на початку:
```python
# ⚠️ FICTIONAL TEST DATA — nie są to dane prawdziwych osób.
# Generated for testing purposes only. PESEL numbers have invalid checksums.
```

## Expected Output
1. `tools/test_data_gen.py` — генератор фіктивних даних
2. `l10n_pl_payroll/tests/test_fixtures.py` — fixtures для Odoo test framework
3. `tools/expected_results.py` — ручні розрахунки для 12 сценаріїв
4. `l10n_pl_payroll/data/demo/pl_payroll_demo.xml` — demo data для Odoo (встановлюється з `demo` в manifest)

## Acceptance Criteria
- [ ] 12 сценаріїв покривають: o pracę, zlecenie, standard KUP, autorskie KUP, PPK (default, opt-out, reduced, additional), ulga dla młodych, ulga na powrót, мінімалка, частковий етат, високий дохід
- [ ] PESEL-номери — правильний формат, невалідна контрольна цифра
- [ ] Ручні розрахунки перевірені (хоча б для сценаріїв 1, 2, 4, 8, 10)
- [ ] Disclaimer в кожному файлі
- [ ] Fixtures сумісні з Odoo 17 test framework

## Notes
- Віталік покаже свій реальний анекс до умови (авторські koszty) як reference — це додатковий сценарій, але пізніше
- Авторські koszty передбачають щомісячний звіт про творчу діяльність — це не частина salary calculation, але модуль має знати про це (поле для зберігання звітів? пізніша фаза)
- Verify manual calculations with web search for current Polish payroll calculators
