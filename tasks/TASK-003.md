# TASK-003: Security groups and access rules

**Status:** done
**Assignee:** codex
**Depends on:** TASK-002
**Phase:** 1.6

## Контекст
Payroll-дані (зарплати, PESEL, ZUS) — найчутливіші дані в HR. GDPR вимагає обмеження доступу. DEC-004 визначає три рівні доступу.

Читай: CLAUDE.md → DECISIONS.md (DEC-004) → ODOO_RECON.md

## Задача
Створити security groups та access rules.

### Security Groups

```xml
<!-- security/pl_payroll_security.xml -->

<!-- Category -->
<record id="module_category_pl_payroll" model="ir.module.category">
    <field name="name">Polish Payroll</field>
</record>

<!-- Groups -->
1. pl_payroll.group_payroll_employee — базовий (бачить лише свій payslip)
2. pl_payroll.group_payroll_officer — повний доступ до payslips, parameters, salary rules
3. pl_payroll.group_payroll_manager — все вище + approve + modify parameters
```

### Access Rules (ir.model.access.csv)

| Model | Group | Read | Write | Create | Unlink |
|---|---|---|---|---|---|
| pl.payroll.parameter | officer | 1 | 0 | 0 | 0 |
| pl.payroll.parameter | manager | 1 | 1 | 1 | 1 |
| (payslip model, when created) | employee | 1 (own) | 0 | 0 | 0 |
| (payslip model, when created) | officer | 1 | 1 | 1 | 0 |
| (payslip model, when created) | manager | 1 | 1 | 1 | 1 |

### Record Rules (multi-company + own-payslip)

- Employee can only see own payslips (domain: `[('employee_id.user_id', '=', user.id)]`)
- Multi-company rule: users see only their company's data

## Expected Output
1. `l10n_pl_payroll/security/pl_payroll_security.xml`
2. `l10n_pl_payroll/security/ir.model.access.csv`
3. Update `__manifest__.py` — add security files to `data`

## Git Workflow

```bash
# 1. Перед початком роботи
cd ~/l10n-pl-payroll
git checkout main && git pull
git checkout -b task/003-security

# 2. Прочитай обов'язково:
# CLAUDE.md → LESSONS.md → DECISIONS.md (DEC-004) → ODOO_RECON.md → цей файл

# 3. Після виконання — коміт і PR:
git add l10n_pl_payroll/security/pl_payroll_security.xml
git add l10n_pl_payroll/security/ir.model.access.csv
git add l10n_pl_payroll/__manifest__.py
git add tasks/TASK-003.md
git commit -m "[TASK-003] Add security groups and access rules (RBAC)"
git push -u origin task/003-security
gh pr create --title "[TASK-003] Security groups and access rules" --body "Three-tier RBAC: employee (own payslips), officer (full read), manager (full CRUD). Multi-company isolation."

# 4. Оновити Status нижче → done
```

## Acceptance Criteria
- [ ] Three distinct security groups created
- [ ] Parameters model: read-only for officers, full for managers
- [ ] Employee record rule limits payslip visibility to own records
- [ ] Multi-company isolation works
- [ ] No hardcoded user IDs
