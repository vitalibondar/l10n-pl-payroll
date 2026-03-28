# TASK-001 Research: Odoo payroll localizations

Публічний код enterprise-репозиторію напряму недоступний з цього середовища, тому дослідження зібране з публічних документів Odoo і mergebot PR-ів, пов'язаних із GitHub. Для архітектури цього модуля цього достатньо: видно основні моделі, структуру правил нарахування (salary rules), параметризацію й патерн звітів.

## 1) Belgium: `l10n_be_hr_payroll`

### Моделі й точки розширення
- `hr.payslip` — основна точка логіки. У мердж-лозі видно `l10n_be_hr_payroll/models/hr_payslip.py`; модуль перевизначає `action_payslip_done()` і дотягує інтеграцію payroll/account.
- `hr.employee` — дані для payslip і декларацій: цивільний статус (civil status), утриманці (dependents), адреса роботи (work address).
- `hr.contract` — контракт є джерелом стажу, типу зайнятості й бази для розрахунків звільнення та повідомлення (termination/notice calculations).
- `hr.leave.type` / `hr.leave` — відпустки (vacation), неоплачувана відпустка (unpaid leave), attests для відпустки при звільненні (holiday attests).
- `hr.work.entry.type` — потрібен DmfA code для кожного типу work entry.
- моделі майстрів звітів (wizard models) — повідомлення про звільнення (departure notice), holiday attests, потоки DmfA/Dimona; це не окремий core payroll model, а набір майстрів поверх стандартних моделей.

### Salary rules
- Після встановлення локалізації (localization) додається структура, що покриває повний бельгійський зарплатний цикл (payroll flow).
- Rule-патерн побудований навколо:
  - gross salary
  - утримання працівника на соцстрах (social security employee deduction) 13.07%
  - внески роботодавця (employer contributions) ~25%
  - оподатковувані натуральні виплати (taxable benefits in kind)
  - службовий автомобіль / ATN
  - річна премія (year-end bonus) / тринадцята зарплата (thirteenth month)
  - відпускні (vacation pay)
  - виплати при звільненні та за період повідомлення (termination / notice period payslips)
- Правила не виглядають як набір жорстко закодованих формул (hardcoded formulas) у UI; вони прив’язані до параметрів і вхідних даних payslip / work entries.

### Parameterization
- Odoo прямо показує шлях `Payroll app ‣ Configuration ‣ Salary ‣ Rule Parameters`.
- У Belgian docs є приклад `CP200: Representation Fees Threshold`.
- Також явно описані річні/прогресивні таблиці та обмежені розрахунки (capped calculations), тобто локалізація тримає ставки й пороги як дані, а не як літерали в правилах.

### Payslip / PDF
- Базовий payslip плюс окремі процеси PDF-виводу (PDF):
  - `Departure: Holiday Attests`
  - `Departure: Notice Period and payslip`
- Для holiday attests Odoo генерує 2 PDF-документи на кожен період N і N-1.

### Testing
- Публічні PR-и в mergebot проходять `ci/runbot`, `ci/upgrade_enterprise`, `ci/l10n`, `ci/style`.
- Це означає, що локалізація тримає розрахунки й завантаження даних (data load) під регресійним покриттям Odoo test suite.
- Практичний патерн: зміни в payroll logic завжди валідять через перекинуті вперед PR-и (merge-forward PRs) і виправлення за traceback (traceback-driven fixes).

## 2) India: `l10n_in_hr_payroll`

### Моделі й точки розширення
- `hr.employee` — payroll-поля в особистих даних (personal info): `UAN`, `ESIC Number`, `PAN`.
- `hr.contract` — salary package живе в контракті; docs прямо кажуть, що contract є основою для payroll calculations.
- `hr.contract.template` — шаблон контракту (contract template) для автозавантаження salary package.
- `hr.payslip` — стандартний payslip, який рахує надбавки (allowances), утримання (deductions), нормативну відповідність (statutory compliance).
- `hr.payroll.structure` / `hr.payroll.structure.type` — нова структура `India: Regular Pay` під `India: Employee Pay`.
- моделі/майстри звітів (report models/wizards) — `Salary Register`, `EPF Report`, `ESI Report`, `Labour Welfare Fund Report`, `Salary Statement`, `Yearly Salary by Employee`.

### Salary rules
- Структура `India: Regular Pay` містить усі правила для:
  - надбавок (allowances)
  - утримань (deductions)
  - нормативної відповідності (statutory compliances)
  - пільг і страхових виплат (benefits / insurance benefits)
- Docs підкреслюють пакетний потік payroll (batch payroll flow): payslips групують по wage type, schedule, department тощо.
- Патерн правил простіший, ніж у Belgium: менше спецвиплат, більше нормативних утримань (statutory deductions) і звітів.

### Parameterization
- `Payroll app ‣ Configuration ‣ Rule Parameters` використовується для ставок і лімітів зарплати (wage caps).
- Налаштування компанії (Company settings) відкривають нормативні поля (statutory input fields): EPF, PT, ESIC, LWF.
- Отже, India-localization комбінує rule parameters + поля налаштувань компанії (company config fields) + шаблон контракту (contract template).

### Payslip / PDF / exports
- Публічні docs показують стандартний payslip view і великий набір звітів у XLSX (XLSX).
- Ключовий патерн тут не окремий PDF-магістр (wizard), а шар нормативної звітності (statutory reporting layer) поверх payroll.

### Testing
- Документація наголошує на `Compute Sheet`, `Validate`, `Worked Days & Inputs`, тобто валідація йде через типовий payroll lifecycle.
- У mergebot видно окремі fixes для `l10n_in_hr_payroll` report data, тобто звітність має окремий регресійний хвіст.

## 3) Що брати в наш модуль

- Брати бельгійський підхід до параметризації: усе, що змінюється по роках, зберігати як data records з датами дії, а не в літералах правил нарахування (salary rule literals).
- Брати індійський підхід до onboarding: контракт як центр payroll-конфігурації, contract template для стартового заповнення, окремі нормативні звіти (statutory reports).
- Не копіювати бельгійську складність в одну купу wizard-ів на старті. Для Польщі краще: один параметричний шар + базова структура правил нарахування (salary rules) + окремі звіти пізніше.
- Не hardcode-ити ставки ZUS/PIT/PPK/мінімалку в Python/XML rules.
- Не змішувати payroll logic і reporting logic в одному моделі; звіти краще виносити окремо, коли з’явиться PIT-11 / PIT-4R.

## Джерела

- [Belgium payroll docs](https://www.odoo.com/documentation/19.0/applications/hr/payroll/payroll_localizations/belgium.html)
- [India payroll docs](https://www.odoo.com/documentation/19.0/applications/hr/payroll/payroll_localizations/india.html)
- [Belgium mergebot PR #71189](https://mergebot.odoo.com/odoo/enterprise/pull/71189)
- [Belgium mergebot PR #70712](https://mergebot.odoo.com/odoo/enterprise/pull/70712)
