#!/usr/bin/env python3

import calendar
import sys
import unicodedata
import xmlrpc.client
from datetime import date


URL = "http://localhost:8069"
DB = "omdev"
USER = "admin@omenergysolutions.pl"
PASSWORD = "omdev2026"

ADMIN_EMPLOYEE_ID = 1
END_MONTH = date(2026, 2, 1)
DEPARTMENTS = [
    "Produkcja",
    "Laboratorium",
    "Magazyn",
    "Biuro",
    "Zarząd",
]
CALENDAR_SPECS = {
    "full_time": {"name": "TASK-019 Full Time", "hour_to": 16.0},
    "half_time": {"name": "TASK-019 Half Time", "hour_to": 12.0},
    "three_quarter_time": {"name": "TASK-019 Three Quarter Time", "hour_to": 14.0},
}

EMPLOYEES = [
    {"index": 1, "name": "Tomasz Kowalski", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "PL", "birthday": "1989-01-17", "gender": "male", "wage": 4806.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 2, "name": "Anna Wiśniewska", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "PL", "birthday": "1992-03-05", "gender": "female", "wage": 4806.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 3, "name": "Piotr Mazur", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "PL", "birthday": "1987-07-22", "gender": "male", "wage": 4806.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 4, "name": "Katarzyna Nowak", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "PL", "birthday": "1991-11-09", "gender": "female", "wage": 4806.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 5, "name": "Wojciech Zieliński", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "PL", "birthday": "1985-05-14", "gender": "male", "wage": 4806.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 6, "name": "Ewa Krawczyk", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "PL", "birthday": "1994-02-28", "gender": "female", "wage": 4806.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 7, "name": "Oleksandr Kovalenko", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "UA", "birthday": "1990-06-19", "gender": "male", "wage": 4806.0, "date_start": "2025-03-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 8, "name": "Nataliia Shevchenko", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "UA", "birthday": "1996-09-03", "gender": "female", "wage": 4806.0, "date_start": "2025-03-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 9, "name": "Dmytro Melnyk", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "UA", "birthday": "1988-12-11", "gender": "male", "wage": 4806.0, "date_start": "2025-03-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 10, "name": "Yuliia Kravchuk", "job_title": "Pracownik produkcji", "department": "Produkcja", "nationality": "UA", "birthday": "1993-04-24", "gender": "female", "wage": 4806.0, "date_start": "2025-03-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0, "calendar": "three_quarter_time"},
    {"index": 11, "name": "Mikołaj Szymański", "job_title": "Kierownik zmiany", "department": "Produkcja", "nationality": "PL", "birthday": "1984-08-16", "gender": "male", "wage": 7500.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 12, "name": "Paulina Dąbrowska", "job_title": "Kierownik zmiany", "department": "Produkcja", "nationality": "PL", "birthday": "1989-10-07", "gender": "female", "wage": 6500.0, "date_start": "2025-06-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 13, "name": "Kacper Wójcik", "job_title": "Laborant", "department": "Laboratorium", "nationality": "PL", "birthday": "1995-01-12", "gender": "male", "wage": 6000.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 14, "name": "Michał Adamski", "job_title": "Inżynier procesu", "department": "Laboratorium", "nationality": "PL", "birthday": "1986-05-27", "gender": "male", "wage": 8000.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "autorskie", "kup_autorskie_pct": 50.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 15, "name": "Natalia Ivanchuk", "job_title": "Magazynierka", "department": "Magazyn", "nationality": "UA", "birthday": "1998-02-18", "gender": "female", "wage": 4806.0, "date_start": "2025-04-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0, "calendar": "half_time"},
    {"index": 16, "name": "Monika Brzeska", "job_title": "Administrator materiałowy", "department": "Magazyn", "nationality": "PL", "birthday": "1990-07-30", "gender": "female", "wage": 5500.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "opt_out", "ppk_ee_rate": 0.0},
    {"index": 17, "name": "Liudmyla Savchenko", "job_title": "Specjalistka ds. księgowości", "department": "Biuro", "nationality": "UA", "birthday": "1987-03-13", "gender": "female", "wage": 7000.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 18, "name": "Szymon Jankowski", "job_title": "Inżynier mechanik", "department": "Biuro", "nationality": "PL", "birthday": "1988-11-26", "gender": "male", "wage": 8500.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "autorskie", "kup_autorskie_pct": 50.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 19, "name": "Aleksander Volkov", "job_title": "Dyrektor ds. Operacji", "department": "Zarząd", "nationality": "UA", "birthday": "1983-09-04", "gender": "male", "wage": 15000.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 20, "name": "Marta Lewandowska", "job_title": "CKO (Dyrektor ds. Wiedzy i IT)", "department": "Zarząd", "nationality": "PL", "birthday": "1986-12-02", "gender": "female", "wage": 12000.0, "date_start": "2025-01-01", "contract_type": "o_prace", "is_student": False, "kup_type": "autorskie", "kup_autorskie_pct": 50.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 21, "name": "Jakub Wiśniewski", "job_title": "Student magazynu", "department": "Magazyn", "nationality": "PL", "birthday": "2003-05-11", "gender": "male", "wage": 4200.0, "date_start": "2025-07-01", "contract_type": "zlecenie", "is_student": True, "kup_type": "standard_20", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 22, "name": "Oliwia Kowalska", "job_title": "Studentka biura", "department": "Biuro", "nationality": "PL", "birthday": "2001-09-18", "gender": "female", "wage": 4300.0, "date_start": "2025-09-01", "contract_type": "zlecenie", "is_student": True, "kup_type": "standard_20", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 23, "name": "Bartosz Nowicki", "job_title": "Freelance graphic designer", "department": "Biuro", "nationality": "PL", "birthday": "1994-04-08", "gender": "male", "wage": 3000.0, "date_start": "2025-11-01", "contract_type": "dzielo", "is_student": False, "kup_type": "autorskie", "kup_autorskie_pct": 50.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 24, "name": "Marek Jabłoński", "job_title": "Pracownik magazynu", "department": "Magazyn", "nationality": "PL", "birthday": "1991-06-15", "gender": "male", "wage": 4200.0, "date_start": "2025-01-01", "date_end": "2025-06-30", "contract_type": "zlecenie", "is_student": False, "kup_type": "standard_20", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
    {"index": 25, "name": "Marek Jabłoński", "job_title": "Pracownik magazynu", "department": "Magazyn", "nationality": "PL", "birthday": "1991-06-15", "gender": "male", "wage": 5200.0, "date_start": "2025-07-01", "contract_type": "o_prace", "is_student": False, "kup_type": "standard", "kup_autorskie_pct": 0.0, "ppk_participation": "default", "ppk_ee_rate": 2.0},
]

PAYSLIP_ADJUSTMENTS = [
    {"name": "Mikołaj Szymański", "month": "2025-12", "category": "bonus_gross", "amount": 2000.0, "label": "Premia roczna"},
    {"name": "Aleksander Volkov", "month": "2025-06", "category": "bonus_gross", "amount": 5000.0, "label": "Premia za wyniki"},
    {"name": "Piotr Mazur", "month": "2025-09", "category": "deduction_gross", "amount": 200.0, "label": "Kara porządkowa"},
    {"name": "Marta Lewandowska", "month": "2026-01", "category": "bonus_gross", "amount": 3000.0, "label": "Premia projektowa"},
    {"name": "Michał Adamski", "month": "2025-11", "category": "bonus_gross", "amount": 1000.0, "label": "Dodatek funkcyjny"},
]
SICK_LEAVE_ENTRIES = [
    {"name": "Tomasz Kowalski", "month": "2025-10", "sick_days": 5, "sick_days_100": 0},
    {"name": "Anna Wiśniewska", "month": "2025-03", "sick_days": 10, "sick_days_100": 0},
    {"name": "Ewa Krawczyk", "month": "2025-07", "sick_days": 10, "sick_days_100": 5},
]
VACATION_ENTRIES = [
    {"name": "Tomasz Kowalski", "month": "2025-08", "vacation_days": 3.0},
    {"name": "Mikołaj Szymański", "month": "2026-02", "vacation_days": 4.0},
    {"name": "Marta Lewandowska", "month": "2026-02", "vacation_days": 2.0},
]


def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if not uid:
        raise RuntimeError("Authentication failed.")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
    return uid, models


def execute(models, uid, model, method, args=None, kwargs=None):
    return models.execute_kw(DB, uid, PASSWORD, model, method, args or [], kwargs or {})


def model_exists(models, uid, model_name):
    return bool(
        execute(
            models,
            uid,
            "ir.model",
            "search_count",
            [[("model", "=", model_name)]],
        )
    )


def slug_email(name):
    first_name, surname = name.split(" ", 1)
    raw = (first_name[0] + surname).lower()
    replacements = {
        "ł": "l",
        "Ł": "L",
        "ß": "ss",
    }
    for source, target in replacements.items():
        raw = raw.replace(source, target)
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_only = "".join(char for char in normalized if ord(char) < 128 and char.isalnum())
    return ascii_only + "@omtest.net"


def fake_pesel(birthday_text, serial):
    born = parse_date(birthday_text)
    year = born.year % 100
    month = born.month
    if 2000 <= born.year <= 2099:
        month += 20
    base = f"{year:02d}{month:02d}{born.day:02d}{serial:04d}"
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = sum(int(base[idx]) * weights[idx] for idx in range(10))
    valid_digit = (10 - (checksum % 10)) % 10
    invalid_digit = (valid_digit + 1) % 10
    return base + str(invalid_digit)


def parse_date(value):
    return date.fromisoformat(value)


def month_range(start_text, end_month):
    current = parse_date(start_text).replace(day=1)
    while current <= end_month:
        yield current
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def month_bounds(month_start):
    last_day = calendar.monthrange(month_start.year, month_start.month)[1]
    return month_start.isoformat(), date(month_start.year, month_start.month, last_day).isoformat()


def count_weekdays_in_month(month_text):
    month_start = parse_date(month_text + "-01")
    last_day = calendar.monthrange(month_start.year, month_start.month)[1]
    total = 0
    for day in range(1, last_day + 1):
        if date(month_start.year, month_start.month, day).weekday() < 5:
            total += 1
    return total


def unlink_one_by_one(models, uid, model, domain, label):
    ids = execute(models, uid, model, "search", [domain], {"order": "id asc"})
    removed = 0
    failures = []
    for record_id in ids:
        try:
            execute(models, uid, model, "unlink", [[record_id]])
            removed += 1
        except Exception as exc:
            failures.append((record_id, str(exc)))
    print(f"Cleanup {label}: removed {removed}, failed {len(failures)}")
    for record_id, message in failures:
        print(f"  ! {label} {record_id}: {message}")
    return removed, failures


def ensure_named_record(models, uid, model, name, extra_vals=None):
    found = execute(models, uid, model, "search", [[("name", "=", name)]], {"limit": 1})
    if found:
        return found[0]
    values = {"name": name}
    if extra_vals:
        values.update(extra_vals)
    return execute(models, uid, model, "create", [values])


def ensure_calendar(models, uid, company_id, key):
    spec = CALENDAR_SPECS[key]
    calendar_id = ensure_named_record(
        models,
        uid,
        "resource.calendar",
        spec["name"],
        {
            "tz": "Europe/Warsaw",
            "company_id": company_id,
        },
    )
    attendance_ids = execute(
        models,
        uid,
        "resource.calendar.attendance",
        "search",
        [[("calendar_id", "=", calendar_id)]],
    )
    if attendance_ids:
        execute(models, uid, "resource.calendar.attendance", "unlink", [attendance_ids])
    for dayofweek in range(5):
        execute(
            models,
            uid,
            "resource.calendar.attendance",
            "create",
            [{
                "name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][dayofweek],
                "calendar_id": calendar_id,
                "dayofweek": str(dayofweek),
                "hour_from": 8.0,
                "hour_to": spec["hour_to"],
                "day_period": "morning",
            }],
        )
    return calendar_id


def ensure_reference_data(models, uid):
    user_data = execute(models, uid, "res.users", "read", [[uid]], {"fields": ["company_id"]})[0]
    company_id = user_data["company_id"][0]
    contract_type_ids = {
        "o_prace": ensure_named_record(models, uid, "hr.contract.type", "Umowa o pracę"),
        "zlecenie": ensure_named_record(models, uid, "hr.contract.type", "Umowa zlecenie"),
        "dzielo": ensure_named_record(models, uid, "hr.contract.type", "Umowa o dzieło"),
    }

    country_rows = execute(
        models,
        uid,
        "res.country",
        "search_read",
        [[("code", "in", ["PL", "UA"])]],
        {"fields": ["code"], "limit": 10},
    )
    country_ids = {row["code"]: row["id"] for row in country_rows}
    missing = [code for code in ("PL", "UA") if code not in country_ids]
    if missing:
        raise RuntimeError(f"Missing countries: {', '.join(missing)}")

    department_ids = {}
    for department_name in DEPARTMENTS:
        department_ids[department_name] = ensure_named_record(models, uid, "hr.department", department_name)

    calendar_ids = {
        key: ensure_calendar(models, uid, company_id, key)
        for key in CALENDAR_SPECS
    }
    execute(
        models,
        uid,
        "res.company",
        "write",
        [[company_id], {"resource_calendar_id": calendar_ids["full_time"]}],
    )

    return {
        "company_id": company_id,
        "calendar_ids": calendar_ids,
        "contract_type_ids": contract_type_ids,
        "country_ids": country_ids,
        "department_ids": department_ids,
    }


def cleanup_demo_data(models, uid):
    if model_exists(models, uid, "pl.payroll.pit11"):
        unlink_one_by_one(models, uid, "pl.payroll.pit11", [], "pit11")
    if model_exists(models, uid, "pl.payroll.zus.dra.line"):
        unlink_one_by_one(models, uid, "pl.payroll.zus.dra.line", [], "zus dra lines")
    if model_exists(models, uid, "pl.payroll.zus.dra"):
        unlink_one_by_one(models, uid, "pl.payroll.zus.dra", [], "zus dra")
    if model_exists(models, uid, "pl.payroll.payslip.line"):
        unlink_one_by_one(models, uid, "pl.payroll.payslip.line", [], "payslip lines")
    unlink_one_by_one(models, uid, "pl.payroll.payslip", [], "payslips")
    if model_exists(models, uid, "pl.payroll.creative.report"):
        unlink_one_by_one(models, uid, "pl.payroll.creative.report", [], "creative reports")
    unlink_one_by_one(models, uid, "hr.contract", [], "contracts")
    unlink_one_by_one(models, uid, "hr.employee", [("id", "!=", ADMIN_EMPLOYEE_ID)], "employees")
    unlink_one_by_one(models, uid, "hr.department", [("name", "in", DEPARTMENTS)], "departments")


def create_employees(models, uid, refs):
    employee_ids = {}
    for employee in EMPLOYEES:
        if employee["name"] in employee_ids:
            continue
        record_id = execute(
            models,
            uid,
            "hr.employee",
            "create",
            [{
                "name": employee["name"],
                "job_title": employee["job_title"],
                "department_id": refs["department_ids"][employee["department"]],
                "work_email": slug_email(employee["name"]),
                "country_id": refs["country_ids"][employee["nationality"]],
                "birthday": employee["birthday"],
                "gender": employee["gender"],
                "ssnid": fake_pesel(employee["birthday"], employee["index"]),
                "company_id": refs["company_id"],
                "is_student": employee["is_student"],
            }],
        )
        employee_ids[employee["name"]] = record_id
        print(f"Created employee {employee['name']}")
    return employee_ids


def create_contracts(models, uid, refs, employee_ids):
    contract_ids = {}
    all_contract_ids = []
    for employee in EMPLOYEES:
        calendar_key = employee.get("calendar", "full_time")
        date_end = employee.get("date_end")
        state = "close" if date_end else "open"
        values = {
            "name": f"TASK-015/{employee['index']:02d} {employee['name']}",
            "employee_id": employee_ids[employee["name"]],
            "company_id": refs["company_id"],
            "resource_calendar_id": refs["calendar_ids"][calendar_key],
            "contract_type_id": refs["contract_type_ids"][employee["contract_type"]],
            "wage": employee["wage"],
            "date_start": employee["date_start"],
            "state": state,
            "kup_type": employee["kup_type"],
            "kup_autorskie_pct": employee["kup_autorskie_pct"],
            "ppk_participation": employee["ppk_participation"],
            "ppk_ee_rate": employee["ppk_ee_rate"],
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        }
        if date_end:
            values["date_end"] = date_end
        contract_id = execute(
            models,
            uid,
            "hr.contract",
            "create",
            [values],
        )
        contract_ids[employee["index"]] = contract_id
        all_contract_ids.append(contract_id)
        print(f"Created contract for {employee['name']} ({employee['contract_type']}, {state})")
    return contract_ids, all_contract_ids


def create_creative_report(models, uid, company_id, employee_id, month_start, name):
    if not model_exists(models, uid, "pl.payroll.creative.report"):
        return
    report_date = date(month_start.year, month_start.month, min(15, calendar.monthrange(month_start.year, month_start.month)[1]))
    execute(
        models,
        uid,
        "pl.payroll.creative.report",
        "create",
        [{
            "employee_id": employee_id,
            "company_id": company_id,
            "date": report_date.isoformat(),
            "description": f"Raport pracy twórczej za {month_start.strftime('%Y-%m')} — {name}",
            "state": "accepted",
            "accepted_by": uid,
            "accepted_date": report_date.isoformat(),
        }],
    )


def employee_end_month(employee):
    date_end = employee.get("date_end")
    if not date_end:
        return END_MONTH
    end_date = parse_date(date_end)
    return date(end_date.year, end_date.month, 1)


def expected_payslip_count():
    total = 0
    for employee in EMPLOYEES:
        total += sum(1 for _ in month_range(employee["date_start"], employee_end_month(employee)))
    return total


def create_payslips(models, uid, refs, employee_ids, contract_ids):
    total_expected = expected_payslip_count()
    progress = 0
    created_ids = {}
    failures = []
    for employee in EMPLOYEES:
        employee_id = employee_ids[employee["name"]]
        contract_id = contract_ids[employee["index"]]
        if employee["name"] not in created_ids:
            created_ids[employee["name"]] = []
        for month_start in month_range(employee["date_start"], employee_end_month(employee)):
            progress += 1
            period = month_start.strftime("%Y-%m")
            print(f"[{progress:03d}/{total_expected}] Creating payslip for {employee['name']} {period} ({employee['contract_type']})")
            try:
                if employee["kup_type"] == "autorskie":
                    create_creative_report(models, uid, refs["company_id"], employee_id, month_start, employee["name"])
                date_from, date_to = month_bounds(month_start)
                payslip_id = execute(
                    models,
                    uid,
                    "pl.payroll.payslip",
                    "create",
                    [{
                        "employee_id": employee_id,
                        "contract_id": contract_id,
                        "date_from": date_from,
                        "date_to": date_to,
                    }],
                )
                execute(models, uid, "pl.payroll.payslip", "action_compute", [[payslip_id]])
                execute(models, uid, "pl.payroll.payslip", "action_confirm", [[payslip_id]])
                created_ids[employee["name"]].append(payslip_id)
            except Exception as exc:
                failures.append({"name": employee["name"], "period": period, "error": str(exc)})
                print(f"  ! Failed for {employee['name']} {period}: {exc}")
    return created_ids, failures


def recompute_employee_from_month(models, uid, employee_name, month_text):
    payslip_ids = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search",
        [[
            ("employee_id.name", "=", employee_name),
            ("date_from", ">=", month_text + "-01"),
        ]],
        {"order": "date_from asc, id asc"},
    )
    for payslip_id in payslip_ids:
        execute(models, uid, "pl.payroll.payslip", "action_compute", [[payslip_id]])
        execute(models, uid, "pl.payroll.payslip", "action_confirm", [[payslip_id]])


def add_adjustments(models, uid):
    if not model_exists(models, uid, "pl.payroll.payslip.line"):
        print("Payslip line model missing, skipping bonus/deduction seed.")
        return []

    applied = []
    for adjustment in PAYSLIP_ADJUSTMENTS:
        payslip_ids = execute(
            models,
            uid,
            "pl.payroll.payslip",
            "search",
            [[
                ("employee_id.name", "=", adjustment["name"]),
                ("date_from", "=", adjustment["month"] + "-01"),
            ]],
            {"limit": 1},
        )
        if not payslip_ids:
            print(f"  ! Adjustment target not found: {adjustment['name']} {adjustment['month']}")
            continue
        payslip_id = payslip_ids[0]
        try:
            execute(
                models,
                uid,
                "pl.payroll.payslip.line",
                "create",
                [{
                    "payslip_id": payslip_id,
                    "name": adjustment["label"],
                    "category": adjustment["category"],
                    "amount": adjustment["amount"],
                }],
            )
            recompute_employee_from_month(models, uid, adjustment["name"], adjustment["month"])
            applied.append(adjustment)
            print(f"Applied {adjustment['label']} to {adjustment['name']} {adjustment['month']}")
        except Exception as exc:
            print(f"  ! Failed adjustment for {adjustment['name']} {adjustment['month']}: {exc}")
    return applied


def add_sick_leave_entries(models, uid):
    applied = []
    for entry in SICK_LEAVE_ENTRIES:
        payslip_ids = execute(
            models,
            uid,
            "pl.payroll.payslip",
            "search",
            [[
                ("employee_id.name", "=", entry["name"]),
                ("date_from", "=", entry["month"] + "-01"),
            ]],
            {"limit": 1},
        )
        if not payslip_ids:
            print(f"  ! Sick leave target not found: {entry['name']} {entry['month']}")
            continue
        payslip_id = payslip_ids[0]
        try:
            execute(
                models,
                uid,
                "pl.payroll.payslip",
                "write",
                [[payslip_id], {
                    "sick_days": entry["sick_days"],
                    "sick_days_100": entry["sick_days_100"],
                    "working_days_in_month": count_weekdays_in_month(entry["month"]),
                }],
            )
            recompute_employee_from_month(models, uid, entry["name"], entry["month"])
            applied.append(entry)
            print(f"Applied sick leave to {entry['name']} {entry['month']}")
        except Exception as exc:
            print(f"  ! Failed sick leave for {entry['name']} {entry['month']}: {exc}")
    return applied


def add_vacation_entries(models, uid):
    applied = []
    for entry in VACATION_ENTRIES:
        payslip_ids = execute(
            models,
            uid,
            "pl.payroll.payslip",
            "search",
            [[
                ("employee_id.name", "=", entry["name"]),
                ("date_from", "=", entry["month"] + "-01"),
            ]],
            {"limit": 1},
        )
        if not payslip_ids:
            print(f"  ! Vacation target not found: {entry['name']} {entry['month']}")
            continue
        payslip_id = payslip_ids[0]
        try:
            execute(
                models,
                uid,
                "pl.payroll.payslip",
                "write",
                [[payslip_id], {"vacation_days": entry["vacation_days"]}],
            )
            recompute_employee_from_month(models, uid, entry["name"], entry["month"])
            applied.append(entry)
            print(f"Applied vacation days to {entry['name']} {entry['month']}")
        except Exception as exc:
            print(f"  ! Failed vacation entry for {entry['name']} {entry['month']}: {exc}")
    return applied


def format_money(value):
    return f"{value:,.2f}"


def build_summary(models, uid, employee_ids):
    lines = []
    totals = {"months": 0, "gross": 0.0, "net": 0.0}
    header = "Employee                 | Months | Total Gross | Total Net | Avg Net/Month"
    separator = "-------------------------+--------+-------------+-----------+--------------"
    lines.append(header)
    lines.append(separator)
    for employee_name, employee_id in employee_ids.items():
        payslips = execute(
            models,
            uid,
            "pl.payroll.payslip",
            "search_read",
            [[("employee_id", "=", employee_id)]],
            {"fields": ["gross", "net"], "order": "date_from asc, id asc", "limit": 200},
        )
        months = len(payslips)
        total_gross = sum(row["gross"] for row in payslips)
        total_net = sum(row["net"] for row in payslips)
        avg_net = total_net / months if months else 0.0
        totals["months"] += months
        totals["gross"] += total_gross
        totals["net"] += total_net
        lines.append(
            f"{employee_name[:24]:24} | {months:>6} | {format_money(total_gross):>11} | {format_money(total_net):>9} | {format_money(avg_net):>12}"
        )
    lines.append(separator)
    lines.append(
        f"{'TOTAL':24} | {totals['months']:>6} | {format_money(totals['gross']):>11} | {format_money(totals['net']):>9} | {'-':>12}"
    )
    return lines


def verification_snapshot(models, uid):
    checks = []

    employee_19 = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search_read",
        [[("employee_id.name", "=", "Aleksander Volkov"), ("date_from", "=", "2026-01-01")]],
        {"fields": ["taxable_income", "pit_advance", "pit_due", "gross", "net"], "limit": 1},
    )
    if employee_19:
        checks.append(f"Aleksander Volkov 2026-01: gross={employee_19[0]['gross']:.2f}, pit_advance={employee_19[0]['pit_advance']:.2f}, pit_due={employee_19[0]['pit_due']:.2f}")

    employee_14 = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search_read",
        [[("employee_id.name", "=", "Michał Adamski"), ("date_from", "=", "2025-01-01")]],
        {"fields": ["health_basis", "kup_amount", "pit_due"], "limit": 1},
    )
    if employee_14:
        checks.append(f"Michał Adamski 2025-01: health_basis={employee_14[0]['health_basis']:.2f}, kup_amount={employee_14[0]['kup_amount']:.2f}, pit_due={employee_14[0]['pit_due']:.2f}")

    employee_16 = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search_read",
        [[("employee_id.name", "=", "Monika Brzeska"), ("date_from", "=", "2025-01-01")]],
        {"fields": ["ppk_ee", "net"], "limit": 1},
    )
    if employee_16:
        checks.append(f"Monika Brzeska 2025-01: ppk_ee={employee_16[0]['ppk_ee']:.2f}, net={employee_16[0]['net']:.2f}")

    for student_name in ("Jakub Wiśniewski", "Oliwia Kowalska"):
        student_row = execute(
            models,
            uid,
            "pl.payroll.payslip",
            "search_read",
            [[("employee_id.name", "=", student_name)]],
            {"fields": ["date_from", "zus_total_ee", "health", "net"], "order": "date_from asc", "limit": 1},
        )
        if student_row:
            checks.append(
                f"{student_name} {student_row[0]['date_from']}: zus_total_ee={student_row[0]['zus_total_ee']:.2f}, health={student_row[0]['health']:.2f}, net={student_row[0]['net']:.2f}"
            )

    count = execute(models, uid, "pl.payroll.payslip", "search_count", [[]])
    checks.append(f"Total payslips in DB: {count}")
    return checks


def main():
    uid, models = connect()

    print("Connected to Odoo.")
    cleanup_demo_data(models, uid)
    refs = ensure_reference_data(models, uid)
    employee_ids = create_employees(models, uid, refs)
    contract_ids, all_contract_ids = create_contracts(models, uid, refs, employee_ids)
    _, failures = create_payslips(models, uid, refs, employee_ids, contract_ids)
    sick_leave_entries = add_sick_leave_entries(models, uid)
    adjustments = add_adjustments(models, uid)
    vacation_entries = add_vacation_entries(models, uid)

    print("")
    print("Summary")
    print("=======")
    summary_lines = build_summary(models, uid, employee_ids)
    for line in summary_lines:
        print(line)

    print("")
    print("Verification")
    print("============")
    for line in verification_snapshot(models, uid):
        print(line)

    print("")
    print(f"Employees created: {len(employee_ids)}")
    print(f"Contracts created: {len(all_contract_ids)}")
    print(f"Expected payslips: {expected_payslip_count()}")
    print(f"Sick leave entries applied: {len(sick_leave_entries)}")
    print(f"Adjustments applied: {len(adjustments)}")
    print(f"Vacation entries applied: {len(vacation_entries)}")
    print(f"Payslip failures: {len(failures)}")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"  - {failure['name']} {failure['period']}: {failure['error']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
