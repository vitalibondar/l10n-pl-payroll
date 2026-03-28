# Polish Payroll Module — Atomized Work Plan

> Кожне завдання — самодостатнє, з чітким input/output і вказівкою, хто виконує.
> Залежності позначені стрілками (→).

## Phase 0: Передумови

| # | Завдання | Хто | Status | Output |
|---|---|---|---|---|
| 0.1 | ~~З'ясувати версію Odoo~~ | Recon | ✅ Done | Enterprise 17+ on Odoo.sh |
| 0.2 | ~~З'ясувати, чи є payroll module~~ | Recon | ✅ Done | Ні, будуємо з нуля |
| 0.3 | ~~Data export від агенції~~ | — | ❌ Скасовано | Працюємо на фіктивних даних |
| 0.4 | Отримати credentials тестової бази Odoo | Віталік | ⏳ Waiting | DB name, URL |
| 0.5 | Створити Odoo test plugin (клон odoo-connector) | Cowork (інший) | ⏳ Blocked by 0.4 | Plugin для тестової бази |
| 0.6 | Згенерувати фіктивні тестові контракти (всі варіанти) | Codex | ⏳ Open → TASK-004 | XML fixtures + Python generator |
| 0.7 | Бухгалтер починає працювати (валідація) | Ася | ⏳ May 2026 | Sign-off salary rules |

## Phase 1: Module Skeleton

| # | Завдання | Хто | Input | Output |
|---|---|---|---|---|
| 1.1 | Дослідити структуру існуючих payroll localizations (l10n_be, l10n_in) | **Codex** | Odoo source / GitHub | Звіт: які моделі, поля, salary rules використовуються |
| 1.2 | Спроєктувати архітектуру моделей | **Cowork** (цей чат) | Звіт 1.1 + вимоги Асі | Діаграма моделей, список моделей і полів |
| 1.3 | Створити skeleton модуля | **Codex** | Архітектура 1.2 + версія Odoo (0.1) | `__manifest__.py`, models/, views/, security/, data/ |
| 1.4 | Створити модель параметрів (ставки, пороги) з date-effective versioning | **Codex** | DEC-002, список параметрів | `models/pl_payroll_parameter.py` + initial data XML |
| 1.5 | Заповнити початкові дані параметрів (2025 + 2026 ставки) | **Codex** | Дослідження ставок (вже є) | `data/pl_payroll_parameters_2025.xml`, `..._2026.xml` |
| 1.6 | Security groups + access rules | **Codex** | DEC-004 | `security/ir.model.access.csv`, `security/pl_payroll_security.xml` |

## Phase 2: Salary Rules — Core (umowa o pracę)

> Кожне правило — окреме завдання. Codex пише код + unit test. Cowork рев'юїть.

| # | Завдання | Хто | Salary Rule | Залежить від |
|---|---|---|---|---|
| 2.1 | Salary structure для umowa o pracę | **Codex** | Structure definition | 1.3 |
| 2.2 | Rule: Gross salary (base) | **Codex** | BASIC | 2.1 |
| 2.3 | Rule: ZUS emerytalne (працівник, 9.76%) | **Codex** | ZUS_EMERY_EE | 2.2 |
| 2.4 | Rule: ZUS rentowe (працівник, 1.5%) | **Codex** | ZUS_RENT_EE | 2.2 |
| 2.5 | Rule: ZUS chorobowe (працівник, 2.45%) | **Codex** | ZUS_CHOR_EE | 2.2 |
| 2.6 | Rule: ZUS basis cap tracking (cumulative yearly) | **Codex** | ZUS_CAP | 2.3, 2.4 |
| 2.7 | Rule: Health insurance (9%) | **Codex** | HEALTH | 2.3—2.5 |
| 2.8 | Rule: KUP standard (250 PLN/місяць) | **Codex** | KUP_STD | 2.7 |
| 2.9 | Rule: KUP autorskie (50%, з contract flag) | **Codex** | KUP_AUTH | 2.7, DEC-003 |
| 2.10 | Rule: PIT advance (12%/32%, cumulative, kwota wolna) | **Codex** | PIT | 2.7, 2.8/2.9 |
| 2.11 | Rule: PPK employee (2%) | **Codex** | PPK_EE | 2.2 |
| 2.12 | Rule: PPK employer (1.5%, as taxable income) | **Codex** | PPK_ER | 2.2 |
| 2.13 | Rule: Net salary | **Codex** | NET | All above |
| 2.14 | Employer-side rules (ZUS ER: emerytalne 9.76%, rentowe 6.5%, wypadkowe 1.67%, FP 2.45%, FGŚP 0.1%) | **Codex** | ZUS_ER_* | 2.2 |

## Phase 2b: Salary Rules — Extensions (product-grade)

| # | Завдання | Хто | Input |
|---|---|---|---|
| 2b.1 | Overtime rules (150%/200% per Kodeks pracy art. 151¹) | **Codex** | Attendance data, work schedule |
| 2b.2 | Bonus input (gross/net) | **Codex** | Bonus fields on payslip |
| 2b.3 | Penalty/deduction input | **Codex** | Penalty fields on payslip |
| 2b.4 | PIT-2 handling (kwota zmniejszająca 300 PLN/month — only if PIT-2 filed) | **Codex** | Employee flag |
| 2b.5 | Ulga dla młodych (PIT exemption <26, up to 85,528 PLN/year) | **Codex** | Employee birthdate |
| 2b.6 | Ulga na powrót (PIT exemption for returning expats, up to 85,528 PLN/year) | **Codex** | Employee flag + date range |
| 2b.7 | Ulga dla rodzin 4+ (PIT exemption for parents of 4+ kids) | **Codex** | Employee flag |
| 2b.8 | Ulga dla seniorów / pracujących emerytów (PIT exemption for working retirees) | **Codex** | Employee flag |
| 2b.9 | PPK full support: opt-in/opt-out, reduced rate (0.5%), additional voluntary (up to 4%) | **Codex** | Contract fields |
| 2b.10 | Partial month calculation (start/end mid-month) | **Codex** | Contract dates |
| 2b.11 | Sick leave integration (zasiłek chorobowy — 80%/100% of base) | **Codex** | Leave data |

## Phase 2c: Salary Rules — Umowa zlecenie

| # | Завдання | Хто | Input |
|---|---|---|---|
| 2c.1 | Salary structure для umowa zlecenie | **Codex** | Different ZUS rules |
| 2c.2 | Rules: ZUS zlecenie (different basis, optional chorobowe) | **Codex** | Parameter data |
| 2c.3 | Rules: KUP zlecenie (20% standard, 50% autorskie) | **Codex** | Different KUP rates |
| 2c.4 | Rule: PIT zlecenie (with different threshold logic) | **Codex** | — |

## Phase 3: Verification & Testing

| # | Завдання | Хто | Input | Output |
|---|---|---|---|---|
| 3.1 | Створити test data generator (fictional employees) | **Codex** | DEC-005 | Script + fixtures |
| 3.2 | Створити Excel-таблицю верифікації (10 сценаріїв × ручний розрахунок) | **Cowork** або **Codex** | Salary rules | Excel з формулами для Асі |
| 3.3 | Unit tests для кожного salary rule | **Codex** | Rules 2.* | test_salary_rules.py |
| 3.4 | Integration test: full payslip generation | **Codex** | All rules | test_payslip_integration.py |
| 3.5 | Валідація бухгалтером | **Ася + бухгалтер** | Excel 3.2 + payslip output | Sign-off або список помилок |
| 3.6 | Edge cases: first/last month, partial month, mid-year hire, ZUS cap crossing | **Codex** | — | Additional tests |

## Phase 4: Pay Slip Template

| # | Завдання | Хто | Input | Output |
|---|---|---|---|---|
| 4.1 | Дизайн макету pasek wynagrodzeń (які поля, порядок) | **Cowork** + Ася | Polish pay slip examples | Wireframe/mockup |
| 4.2 | QWeb template для PDF | **Codex** | Mockup 4.1 | `report/pl_payslip_report.xml` |
| 4.3 | Report action + menu item | **Codex** | 4.2 | views + report config |

## Phase 5: Integrations

| # | Завдання | Хто | Input | Output |
|---|---|---|---|---|
| 5.1 | Public holidays calendar (Polish holidays 2026—2027) | **Codex** | Holiday list | `data/pl_public_holidays.xml` |
| 5.2 | Integration з Time Off module (перевірка наявності заявлення на відпустку) | **Codex** | Odoo Time Off API | Validation logic |
| 5.3 | Integration з Attendance module (overtime hours) | **Codex** | Odoo Attendance API | Hours data for overtime rules |

## Phase 6: Scheduled Reminder

| # | Завдання | Хто | Input | Output |
|---|---|---|---|---|
| 6.1 | Створити scheduled task "Перевір зміни в польському трудовому законодавстві" | **Cowork** | Vitalik's spec | Monthly reminder |

## Phase 7: Documentation & Release

| # | Завдання | Хто | Input | Output |
|---|---|---|---|---|
| 7.1 | README з інструкцією встановлення та налаштування | **Codex** | All above | README.md |
| 7.2 | Інструкція для бухгалтера (як перевіряти, як змінювати параметри) | **Cowork** | Parameters model | User guide (MD or DOCX) |
| 7.3 | CHANGELOG | **Codex** | — | CHANGELOG.md |

---

## Приблизний розподіл зусиль

| Агент | Завдань | Тип роботи |
|---|---|---|
| **Codex** | ~30 | Код, тести, boilerplate, дослідження чужих модулів |
| **Cowork** (цей чат) | ~8 | Архітектура, рев'ю, compliance, документація, планування |
| **Claude Code CLI** | ad hoc | Git, linting, Odoo shell, file ops |
| **Ася + бухгалтер** | ~3 | Валідація, sign-off, відповіді на питання |
| **Віталік** | ~4 | Комунікація з Асею, відповіді на Open Questions, фінальне рішення |

## Критичний шлях

```
0.1 (Odoo version) → 1.1—1.3 (skeleton) → 2.1—2.13 (rules) → 3.1—3.5 (testing) → 3.5 (accountant sign-off)
                                                                                           ↓
                                                                              4.1—4.3 (pay slip template)
                                                                                           ↓
                                                                              5.1—5.3 (integrations)
```

**Найдовший відрізок:** від старту до sign-off бухгалтера. Все інше можна паралелити.
