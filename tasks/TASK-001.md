# TASK-001: Research Odoo payroll localizations (l10n_be, l10n_in)

**Status:** done
**Assignee:** codex
**Depends on:** —
**Phase:** 1.1

## Контекст
Ми будуємо Polish payroll module для Odoo 17 Enterprise. Odoo не має офіційної Polish localization. Нам потрібно зрозуміти патерни, які використовують існуючі localizations, щоб побудувати свою за тим самим шаблоном.

Важливо: в нашій Odoo-інсталяції `hr_payroll` (Enterprise) **НЕ встановлений**. Ми будуємо standalone модуль, але хочемо бути сумісними з Odoo payroll architecture, щоб у майбутньому можна було інтегруватися.

## Задача
Проаналізуй вихідний код 2—3 існуючих Odoo payroll localizations на GitHub:
- `l10n_be_hr_payroll` (Belgium — найповніший)
- `l10n_in_hr_payroll` (India)
- За бажанням: будь-яку іншу

## Expected Output
Файл `tasks/TASK-001-research.md` із:

1. **Список моделей**, які використовує кожна localization (models/*.py). Для кожної: назва, призначення, ключові поля.
2. **Salary rules structure**: як організовані rules (categories, sequences, conditions). Скільки rules у Belgium? Як вони посилаються одна на одну?
3. **Parameterization**: як зберігаються ставки (hardcoded? parameters? company fields?). Як оновлюються при зміні законодавства?
4. **Pay slip template**: яку технологію використовують для PDF (QWeb? Report action?). Що є на листку?
5. **Testing**: як тестують salary calculations? Які test patterns?
6. **Рекомендація**: яку архітектуру адаптувати для нашого модуля. Що взяти, що змінити, чого уникати.

## Git Workflow

```bash
# 1. Перед початком роботи
cd ~/l10n-pl-payroll
git checkout main && git pull
git checkout -b task/001-research-localizations

# 2. Прочитай обов'язково:
# CLAUDE.md → LESSONS.md → цей файл

# 3. Після виконання — коміт і PR:
git add tasks/TASK-001-research.md
git add tasks/TASK-001.md   # бо оновив Status → done
git commit -m "[TASK-001] Research Odoo payroll localizations (l10n_be, l10n_in)"
git push -u origin task/001-research-localizations
gh pr create --title "[TASK-001] Payroll localization research" --body "Research of l10n_be and l10n_in payroll modules. See tasks/TASK-001-research.md"

# 4. Оновити Status нижче → done
```

## Acceptance Criteria
- [ ] Покриті мінімум 2 localizations
- [ ] Є конкретні приклади (назви файлів, моделей, полів)
- [ ] Є рекомендація з обґрунтуванням
- [ ] Файл < 2000 слів (стисло, без води)
