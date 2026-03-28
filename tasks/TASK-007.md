# TASK-007: Payslip views (form, tree, search) + batch computation

**Status:** done
**Assignee:** codex
**Depends on:** TASK-005 (payslip model)
**Phase:** 2.3

## Контекст
Payslip model з TASK-005 працює, але не має UI. Потрібні views для Odoo backend і action для batch-розрахунку всіх payslips за місяць.

Читай: CLAUDE.md → LESSONS.md

## Задача

### 1. Form view (`views/pl_payroll_payslip_views.xml`)

```xml
<!-- Form: повна інформація про один payslip -->
- Header: кнопки [Compute] [Confirm] [Cancel] (залежно від state)
- Statusbar: draft → computed → confirmed / cancelled
- Group 1 (top): employee, contract, period (date_from, date_to), state
- Group 2: Gross
- Group 3 (Employee deductions):
  - ZUS (emerytalne, rentowe, chorobowe, total)
  - Health (basis, amount)
  - KUP (type from contract, amount)
  - PIT (taxable income, advance, reducing, due)
  - PPK employee
- Group 4: NET (великим шрифтом)
- Group 5 (Employer costs, readonly):
  - ZUS employer (emerytalne, rentowe, wypadkowe, FP, FGŚP)
  - PPK employer
  - Total employer cost
- Tab: Notes
```

### 2. Tree view

```xml
<!-- Tree: список payslips -->
Columns: employee, date_from, date_to, gross, net, state
Декорація: state == 'confirmed' → зелений, state == 'cancelled' → сірий
```

### 3. Search view

```xml
<!-- Search: фільтри й групування -->
Filters: Draft, Computed, Confirmed, Cancelled
Filters: This Month, Last Month, This Year
Group By: Employee, Department, Month, State
```

### 4. Action + Menu

```xml
<!-- Меню під HR або окреме top-level menu -->
action: ir.actions.act_window для pl.payroll.payslip
menu: Polish Payroll → Payslips
menu: Polish Payroll → Configuration → Parameters (view for pl.payroll.parameter)
```

### 5. Parameter views

Додати tree + form views для `pl.payroll.parameter`, щоб managers могли бачити й редагувати ставки через UI.

### 6. Batch compute wizard (простий)

```python
# wizard/pl_payroll_batch_compute.py
class PlPayrollBatchCompute(models.TransientModel):
    _name = 'pl.payroll.batch.compute'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_compute(self):
        # Знайти всі active contracts
        # Створити payslip для кожного (якщо ще немає)
        # Викликати compute_payslip() на кожному
```

## Expected Output
1. `l10n_pl_payroll/views/pl_payroll_payslip_views.xml`
2. `l10n_pl_payroll/views/pl_payroll_parameter_views.xml`
3. `l10n_pl_payroll/views/pl_payroll_menus.xml`
4. `l10n_pl_payroll/wizard/pl_payroll_batch_compute.py`
5. `l10n_pl_payroll/wizard/__init__.py`
6. `l10n_pl_payroll/views/pl_payroll_compute_wizard_views.xml`
7. Update `__init__.py` (root + wizard)
8. Update `__manifest__.py` (views + wizard)
9. Update `security/ir.model.access.csv` (wizard model)
10. `l10n_pl_payroll/tests/test_batch_compute_wizard.py`

## Git Workflow

```bash
cd ~/l10n-pl-payroll
git checkout main && git pull
git checkout -b task/007-views-wizard

git add l10n_pl_payroll/views/pl_payroll_payslip_views.xml
git add l10n_pl_payroll/views/pl_payroll_parameter_views.xml
git add l10n_pl_payroll/views/pl_payroll_menus.xml
git add l10n_pl_payroll/wizard/pl_payroll_batch_compute.py
git add l10n_pl_payroll/wizard/__init__.py
git add l10n_pl_payroll/views/pl_payroll_compute_wizard_views.xml
git add l10n_pl_payroll/__init__.py
git add l10n_pl_payroll/__manifest__.py
git add l10n_pl_payroll/security/ir.model.access.csv
git add l10n_pl_payroll/tests/test_batch_compute_wizard.py
git add tasks/TASK-007.md
git commit -m "[TASK-007] Add payslip and parameter views, menus, batch compute wizard"
git push -u origin task/007-views-wizard
gh pr create --title "[TASK-007] Payslip views and batch wizard" --body "Form/tree/search views for payslips, parameter management UI, menus, and batch compute wizard."
```

## Acceptance Criteria
- [x] Form view shows full payslip with all computed fields
- [x] Tree view lists payslips with key columns
- [x] Search view has filters and group-by options
- [x] Menu: Payroll → Payslips, Payroll → Configuration → Parameters
- [x] Batch wizard creates and computes payslips for all active contracts
- [x] Parameter tree+form views work for managers
- [x] No hardcoded strings where translations are possible
