# TASK-037 Report

## Що було зламано

- Після `TASK-035` у `uk` і `ru` лишався змішаний payslip UI: вкладки, warning-бейджі та частина підписів усе ще світили польський текст або польські хвости в дужках.
- Простого порівняння `.po` було недостатньо: `uk.po` і `ru.po` вже містили частину потрібних перекладів, але живий `pl.payroll.payslip.get_view()` для `uk_UA` і `ru_RU` усе одно повертав польський form XML.
- Корінь проблеми був у loader для `model_terms:ir.ui.view`: він оновлював `arch_db` без `source_lang='pl_PL'`, а після `en_US` loader Odoo вже не матчило польські source-терми для `uk` / `ru` view-перекладів.

## Що виправлено

- Узагальнено loader перекладів:
  - один прохід тепер застосовує `en_US`, `uk_UA`, `ru_RU`
  - для `model_terms` оновлення йдуть із `source_lang='pl_PL'`, тому Odoo коректно накладає переклади на польський source-шар views
- У `uk.po` і `ru.po` прибрано непотрібні польські хвости з generic UI:
  - вкладки payslip
  - warning-бейджі та пов’язані ярлики
  - меню/дії типу `Konfiguracja`, `Deklaracje i raporty`, `Generuj`, `Przelicz`
  - кілька найвидиміших field labels на payslip формі
- Заповнено порожні user-facing report рядки в `uk.po` і `ru.po` для payslip explanation copy.

## Як перевірено

- `msgfmt --check-format -o /tmp/l10n_pl_payroll_en.mo l10n_pl_payroll/i18n/en_US.po`
- `msgfmt --check-format -o /tmp/l10n_pl_payroll_uk.mo l10n_pl_payroll/i18n/uk.po`
- `msgfmt --check-format -o /tmp/l10n_pl_payroll_ru.mo l10n_pl_payroll/i18n/ru.po`
- `python3 -m py_compile l10n_pl_payroll/models/pl_payroll_translation_loader.py`
- `bash scripts/upgrade_module.sh`
- XML-RPC перевірка через `pl.payroll.payslip.get_view()` для `view_pl_payroll_payslip_form`:
  - `uk_UA`: знайдено `Розрахунок працівника`, `Нижче мінімальної зарплати`, `Звіт про творчу роботу`, `Примітки`, `Зарплата брутто нижча`
  - `ru_RU`: знайдено `Расчет работника`, `Ниже минимальной зарплаты`, `Отчет о творческой работе`, `Примечания`, `Зарплата брутто ниже`
  - для обох мов у `get_view()` більше немає `Rozliczenie pracownika`, `Poniżej minimalnego wynagrodzenia`, `Raport twórczy`
- XML-RPC перевірка `fields_get()` для payslip-полів:
  - `gross`
  - `total_employer_cost`
  - `net`
  - `etat_fraction`
  - `creative_report_required`
  - `creative_report_id`
  - `notes`
  Усі повертають очікувані `uk` / `ru` підписи без польських хвостів.

## Залишковий ризик

- У `uk` / `ru` ще лишаються окремі payroll-терміни в дужках там, де вони свідомо збережені для орієнтації на польські документи. У цьому таску прибирався не весь модуль, а найвидиміший generic UI та live payslip surface.
