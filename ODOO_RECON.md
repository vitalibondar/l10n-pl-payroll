# Odoo Environment Reconnaissance — 2026-03-28

## System

| Parameter | Value | Source |
|---|---|---|
| **Edition** | Enterprise | `sign.request` model exists |
| **Version** | 17+ (likely 17.0) | `employee_properties` field (properties type = Odoo 17+) |
| **Hosting** | Odoo.sh | Traceback path: `/home/odoo/src/odoo/odoo/` |
| **Currency** | PLN | `res.company` data |
| **Timezone** | Europe/Berlin | `resource.calendar` tz (= UTC+1/+2, same as Poland) |

## Companies

| ID | Name | Employees |
|---|---|---|
| 4 | **OM Poland (Energy Solutions)** | ~78 (main company) |
| 11 | OM Motors | ~4 |
| 1 | WoodenShark LLC | — |
| 7 | OM Energy Solutions Sp. z o.o. | — |
| 12 | OM AERO SOLUTIONS SP Z O O | — |
| others | OM Ukraine, OMD systems, OM Batteries | — |

**Target for payroll module:** OM Poland (Energy Solutions) + OM Motors.

## HR Data Quality

### Employees (82 total)

- Більшість = виробничі працівники (job_title: "Produkcja" / "Production")
- Ключові ролі: Kierownik Produkcji, Kierownik Zmiany, Shift Manager, Koordynator Obiektu, Dyrektor ds. Operacji, Inżynier Procesu, Laboratorium, Magazyn, specjalista ds. zakupów, Specjalistka ds. księgowości i kadr
- **Vitalii Bondar** (ID 23) = Operations Director, OM Poland

### ⚠️ Критичні прогалини в даних

| Поле | Стан | Потрібно для payroll? |
|---|---|---|
| **hr.contract** | **0 записів** — жоден контракт не заповнений | 🔴 ТАК — це основа payroll |
| ssnid (PESEL) | Порожнє у Віталіка, ймовірно у всіх | 🔴 ТАК — ZUS декларації |
| birthday | Порожнє | 🟡 Для ulga dla młodych |
| country_id (Nationality) | Порожнє | 🟡 Для work permit tracking |
| identification_id | Порожнє | 🟡 Ідентифікація |
| department_id | Лише 2 з 82 мають department | ⚪ Не критично для payroll |

## Installed Modules (relevant to payroll)

| Module | Status | Evidence |
|---|---|---|
| hr (base) | ✅ Installed | 82 employees exist |
| hr_contract | ✅ Installed | Model exists, fields visible, but **0 records** |
| hr_attendance | ✅ Installed, **actively used** | **10,980 records**, latest 2026-03-27 |
| hr_timesheet | ✅ Installed | `has_timesheet` field on hr.employee |
| sign | ✅ Installed (Enterprise) | `sign_request_ids` on hr.employee |
| hr_expense | ✅ Installed | `expense_manager_id` field exists |
| **hr_payroll** | ❌ **NOT installed** | `hr.payroll.structure` model doesn't exist |
| **hr_holidays (Time Off)** | ❌ **NOT installed** | `hr.leave.type` model doesn't exist |
| **hr_work_entry** | ❌ **NOT installed** | `hr.work.entry.type` model doesn't exist |

## Existing Payroll-Adjacent Config

### Salary Structure Types (hr.payroll.structure.type)
- ID 1: "Employee"
- ID 2: "Worker"
(Default data from hr_contract module, not from payroll)

### Contract Types (hr.contract.type)
Permanent, Temporary, Seasonal, Full-Time, Part-Time, Student, Apprenticeship, Thesis, Statutory, Employee
→ **Немає польських типів (umowa o pracę, umowa zlecenie)**

### Resource Calendars
- Standard 40 hours/week (per company)
- "Working Hours of OM Poland (Energy Solutions)" (ID 10, custom, 5 attendance lines)

## Implications for Polish Payroll Module

### What we can use as-is:
1. **hr.attendance** — 10,980+ записів. Overtime calculation має реальні дані.
2. **hr.employee** — базові дані працівників є (імена, job titles, emails).
3. **hr.contract** model — існує, поля є, треба лише заповнити.
4. **resource.calendar** — робочий розклад налаштований.

### What needs to be installed BEFORE payroll:
1. **hr_holidays (Time Off)** — Ася хоче перевірку заявлень на відпустку. Без цього модуля нема де їх зберігати.
2. **hr_work_entry** — якщо Enterprise payroll потребує work entries (перевірити).

### What needs to be FILLED IN (data entry):
1. **Контракти для всіх 82 працівників** — тип (o pracę / zlecenie), ставка, дата початку. Це найбільший блокер.
2. **PESEL (ssnid)** — для ZUS декларацій.
3. **Birthday** — для ulga dla młodych.
4. **Польські типи контрактів** — додати "Umowa o pracę" та "Umowa zlecenie" до hr.contract.type.

## Questions That STILL Need Asya

Розвідка вирішила більшість Open Questions. Залишилися:

1. ~~Яка версія Odoo?~~ → **Enterprise 17+ на Odoo.sh** ✅
2. ~~Де хоститься?~~ → **Odoo.sh** ✅
3. ~~Чи є base payroll module?~~ → **Ні** ✅
4. **Коли прийде бухгалтер?** — для валідації salary rules
5. **Чи можна встановити hr_holidays (Time Off)?** — потрібно для перевірки відпусток
6. **Хто заповнюватиме контракти для 82 працівників?** — без контрактів payroll не працює
7. **Alena Hrytsanchuk** (Specjalistka ds. księgowości i kadr) — чи це та бухгалтерка, яку Ася згадувала?
