# TASK-035 Report

## Що було зламано

- Після `TASK-034` у `uk` і `ru` ще лишалися дірки не в самих `msgstr`, а в покритті `occurrence` для `model_terms:ir.ui.view`.
- Через це Odoo міг мати переклад для field label, але не мати перекладу для такого самого видимого рядка у form view.
- Окремо лишилися кілька short-label перекладів із зайвими польськими хвостами, через що інтерфейс виглядав напівперекладеним.

## Що виправлено

- Добито відсутні `view`-входження для `uk` і `ru` у payslip form:
  - `Brakuje raportu twórczego`
  - `Chorobowe`
  - `Poniżej minimalnego wynagrodzenia`
- Додано пропущені user-facing рядки для `uk` і `ru`:
  - `Czas pracy i absencje`
  - `Podsumowanie wypłaty`
  - `Składka zdrowotna i PIT`
  - `Generuj i otwórz PIT-11`
  - `Generuj i otwórz DRA`
  - обидва wizard info-alert речення для PIT-11 і ZUS DRA
- Прибрано непотрібні польські хвости з коротких видимих ярликів у `uk` / `ru`:
  - кнопки
  - статуси
  - warning badges
  - частина section headers на payslip form

## Як перевірено

- `msgfmt --check-format l10n_pl_payroll/i18n/en_US.po`
- `msgfmt --check-format l10n_pl_payroll/i18n/uk.po`
- `msgfmt --check-format l10n_pl_payroll/i18n/ru.po`
- Python-скриптом порівняно `en_US.po` проти `uk.po` і `ru.po` по `msgid` + `occurrence` для user-facing view/model entries.
- До патчу різниця для `uk` і `ru` становила 10 user-facing gap-ів у payslip/wizard coverage.
- Після патчу різниця для цього набору перевірок = 0.

## Залишковий ризик

- Щоб ці зміни стали видимими в живому Odoo-інтерфейсі, локальна база має підтягнути оновлені переклади під час module upgrade / translation import.
- Live-UI перевірку в цьому репозиторії не виконано, бо локальної Odoo-сесії для автоматичного проходу тут не було.
