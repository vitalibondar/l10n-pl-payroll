# TASK-031 Report

## Reviewed

- XML views:
  - `l10n_pl_payroll/views/pl_payroll_payslip_views.xml`
  - `l10n_pl_payroll/views/pl_payroll_menus.xml`
  - `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml`
  - `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml`
  - `l10n_pl_payroll/views/pl_payroll_pit11_views.xml`
  - `l10n_pl_payroll/views/pl_payroll_zus_dra_views.xml`
  - `l10n_pl_payroll/views/pl_payroll_creative_report_views.xml`
  - `l10n_pl_payroll/report/pl_payroll_payslip_template.xml`
- Localization:
  - `l10n_pl_payroll/i18n/en_US.po`
- Live UI:
  - `http://localhost:8069`
  - payslip list
  - payslip detail forms for sample records `2511` and `2514`
  - PIT-11 wizard
  - ZUS DRA wizard
  - ZUS DRA list

## Verdict

Поточний UI став кращим для бухгалтерки на рівні структури, але гіршим на рівні візуальної ієрархії. Вкладки й польська професійна термінологія дали правильні “папки” для інформації, тому форма тепер ближча до того, як бухгалтерка мислить payroll-процесом. Але разом із цим форма втратила головний фокус: `net` більше не виглядає як головний результат, а тоне серед десятків рівновагомих полів. Для швидкої перевірки payslip list зараз корисніший, ніж payslip detail form, і це поганий сигнал: detail form має бути сильнішим екраном, а не слабшим. Для менеджера або CFO поточна форма стала гіршою, бо відповідь “скільки до виплати” більше не лежить у першому екрані як домінантна цифра. Для бухгалтерки tabs допомагають, але перша вкладка перевантажена й не підтримує швидке сканування зверху вниз. У PL-інтерфейсі термінологічний напрямок правильний. В EN-інтерфейсі локалізація зараз непослідовна: частина labels перекладена, частина лишилась польською, частина показується як `English (Polish)`, через що UI виглядає недоробленим. Wizards для PIT-11 і ZUS DRA працюють, але виглядають занадто generic і не дають достатнього контексту для неекспертного користувача. Підсумок: інформаційна архітектура покращилась, але головну payroll-specific візуальну домінанту модуль втратив.

## Problems by Priority

### P1

- **Payslip detail form ховає головний результат.**
  `net` живе внизу першої вкладки як звичайне readonly-поле, з тією ж вагою, що й інші цифри. Для менеджера це прямий regression проти старого варіанту з великим `net`. Для бухгалтерки це теж гірше, бо головну суму доводиться “вичитувати”, а не бачити.

- **Перший екран payslip не підтримує one-glance scan.**
  На одному рівні ваги стоять basic data, long warning, tab bar, gross, chorobowe, ZUS, KUP, PIT, PPK. Екран став логічнішим, але не став швидшим. Бухгалтерка може працювати, але не може миттєво звірити ключі: employee, period, state, gross, net, warning.

- **Поточна payslip form виглядає як generic Odoo form, а не як payroll cockpit.**
  Модуль уже має сильніший візуальний патерн у PDF payslip: там є hero-блок із великою сумою. У form view цього немає, хоча саме form потрібен для щоденної перевірки.

### P2

- **EN localization непослідовна й місцями недоперекладена.**
  У live UI видно змішання:
  - `Employee`, `Period start`, `Period end`
  - поруч із цим `Nazwa`, `Wydział`, `Firma`, `Umowa`
  - tabs/buttons як `Employer charges (składki pracodawcy)`, `Cancel (anuluj)`
  У `l10n_pl_payroll/i18n/en_US.po` для багатьох ключових msgid `msgstr` порожній, тому інтерфейс виглядає напівготовим.

- **Locale formatting виправлено не всюди.**
  У wizard-ах `PIT-11` і `ZUS DRA` роки показуються правильно як `2025` / `2026`, але в live `ZUS DRA` list view рік досі видно як `2,026`. Це підриває довіру до акуратності локалізації.

- **Фінансові значення у form view не мають сильної валюти/форматної підказки.**
  У payslip detail form цифри виглядають як plain floats. Для бухгалтера це ще терпимо, але для менеджера або випадкового користувача не завжди очевидно, що це PLN і що це гроші, а не технічні значення.

- **Меню модуля добре розкладене логічно, але важливі пункти ховаються в overflow.**
  У live top menu одразу видно лише:
  - payslips
  - batch generation
  - creative reports
  А `PIT-11`, `ZUS DRA` і configuration сховані за `+ / More`. Для бухгалтерки це зайвий клік. Для нечастого користувача це ще й discoverability problem.

- **Wizards PIT-11 / ZUS DRA занадто “німі”.**
  Вони просять лише year/month і дають кнопку generate. Не видно:
  - за яку компанію це піде
  - що беруться лише confirmed payslips
  - чи це create, refresh, regenerate
  - який результат відкриється після запуску

### P3

- **Перша вкладка payslip перевантажена другорядними полями.**
  `chorobowe`, `vacation`, `working_days`, `ytd_sick_days` корисні, але вони починають конкурувати за увагу з gross/net/tax/ZUS.

- **Warning banners працюють, але не дають короткої decision cue.**
  Вони довгі й текстові. Для scanability краще мати короткий payroll-style маркер поруч із summary, а вже нижче повний warning text.

- **Список payslips читається добре, але KUP column місцями занадто довгий.**
  Текст типу `KUP 20% for civil-law contracts` забирає ширину й відбирає увагу від gross/net.

## What Should Stay Unchanged

- Залишити tabs як макрорівень структури. Повертатися до одного довгого вертикального полотна не треба.
- Залишити поділ на employee settlement vs employer charges.
- Залишити warning banners зверху форми. Сам факт top-level warning правильний.
- Залишити list view payslips з gross, net, state, employee і period. Це зараз найсильніший scanable екран модуля.
- Залишити польську професійну базову термінологію як source language.
- Залишити creative report як окрему сутність і окрему вкладку.
- Залишити state/statusbar у header. Він добре показує процесний стан.
- Залишити numeric formatting fix у wizard-ах PIT-11 і ZUS DRA.

## Concrete Recommendations by File or Zone

### `l10n_pl_payroll/views/pl_payroll_payslip_views.xml`

- Додай компактний summary strip над notebook:
  - employee
  - period
  - state
  - gross
  - `net` як найбільшу цифру
  - короткі warning badges
- Поверни `net` в сильну візуальну домінанту на першому екрані.
- Не прибирай tabs. Перерозклади вагу всередині першої вкладки:
  - зверху `gross` + `net`
  - нижче ZUS / health / PIT / KUP / PPK
  - ще нижче chorobowe, urlop, working days
- Зменш роль `name`, `company`, частини secondary metadata в first scan area.
- Якщо warning є, прив’яжи його до summary, а не тільки до довгого банера.

### `l10n_pl_payroll/views/pl_payroll_menus.xml`

- Зроби так, щоб frequent accountant actions не ховалися в overflow на типовій ширині.
- `PIT-11` і `ZUS DRA` мають бути discoverable без додаткового “полювання” за `+`.
- Configuration тримай останньою і менш помітною, ніж operational actions.

### `l10n_pl_payroll/wizard/pl_payroll_pit11_wizard_views.xml`

- Додай 1 короткий explanatory line:
  - що беруться лише confirmed payslips
  - що після generate відкриється список створених/оновлених PIT-11
- Кнопку варто назвати дієсловом результату, а не лише `Generate`.

### `l10n_pl_payroll/wizard/pl_payroll_zus_dra_wizard_views.xml`

- Та сама рекомендація: короткий context line про confirmed payslips, компанію й те, що wizard створює або оновлює декларацію.
- Місяць/рік зараз формально ок у wizard, але сам wizard виглядає надто generic для юридично важливого документа.

### `l10n_pl_payroll/views/pl_payroll_zus_dra_views.xml`

- Прибери locale grouping для року в list/form surfaces, не лише у wizard.
- Перевір формат місяця й рокового поля в усіх list/form відображеннях цієї моделі.

### `l10n_pl_payroll/views/pl_payroll_pit11_views.xml`

- Залиш поточну секційну структуру.
- Якщо чіпати UI, то не редизайнити форму, а лише додати stronger summary/header context.

### `l10n_pl_payroll/i18n/en_US.po`

- Доповни порожні `msgstr` для ключових payroll labels.
- Прийми одне правило для EN:
  - або повноцінний англомовний label + польський термін у дужках
  - або чиста польська база тільки в PL locale
- Поточний half-translated hybrid треба прибрати.

### `l10n_pl_payroll/report/pl_payroll_payslip_template.xml`

- Використай цей PDF як референс для form view summary.
- Саме тут уже є правильна payroll hierarchy:
  - hero amount
  - clear document context
  - secondary numbers нижче

## What to Restore from the Old Screenshot

- Велике `net` у верхній частині payslip form.
- Прямий gross-vs-net контраст в одному viewport.
- Відчуття, що form відповідає на головне питання одразу, а не після читання секцій.
- Просту візуальну логіку: спочатку результат, потім пояснення з чого він склався.

## What Not to Do

- Не роби редизайн з нуля.
- Не викидай tabs повністю.
- Не змішуй employer charges назад у головний робочий екран бухгалтерки.
- Не спрощуй професійну польську термінологію до “попсових” слів.
- Не лікуй UX зміною payroll logic або назв полів у моделі.
- Не перетворюй backoffice form на яскравий dashboard із картками, градієнтами й маркетинговими метриками.
- Не ховай warnings глибше, ніж зараз.

## Short List for the Next Codex

1. У `pl_payroll_payslip_views.xml` повернути hero-style `net` у верхню частину форми.
2. Додати компактний summary row: employee, period, state, gross, net, warnings.
3. Перегрупувати першу вкладку так, щоб chorobowe/urlop були нижче основних payroll numbers.
4. Залишити tabs, але зменшити перевантаження першої вкладки.
5. У `pl_payroll_menus.xml` вивести `PIT-11` і `ZUS DRA` в більш видиму навігацію.
6. У `pl_payroll_zus_dra_views.xml` прибрати `2,026`-style grouping у list/form view.
7. У `en_US.po` закрити порожні переклади для `Firma`, `Nazwa`, `Wydział`, `Umowa` та інших базових labels.
8. Зробити EN UI послідовним: один translation pattern на весь модуль.
9. У wizard view для `PIT-11` додати короткий текст про confirmed payslips і результат після generate.
10. У wizard view для `ZUS DRA` додати такий самий context line.
11. Не чіпати payroll logic, моделі розрахунку й workflow states.
12. Використати `report/pl_payroll_payslip_template.xml` як референс для form hierarchy, а не вигадувати нову мову інтерфейсу.
