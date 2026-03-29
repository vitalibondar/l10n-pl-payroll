#!/usr/bin/env python3

import calendar
import sys
import xmlrpc.client
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

import seed_realistic_data as seed


TWOPLACES = Decimal("0.01")
WHOLE_ZLOTY = Decimal("1")
TOLERANCE = Decimal("0.01")
TARGET_YEAR = 2025
TARGET_DRA_YEAR = 2026
TARGET_DRA_MONTH = 1
BATCH_MONTH = date(2026, 2, 1)


def connect():
    common = xmlrpc.client.ServerProxy(f"{seed.URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(seed.DB, seed.USER, seed.PASSWORD, {})
    if not uid:
        raise RuntimeError("Authentication failed.")
    models = xmlrpc.client.ServerProxy(f"{seed.URL}/xmlrpc/2/object", allow_none=True)
    return uid, models


def execute(models, uid, model, method, args=None, kwargs=None):
    return models.execute_kw(seed.DB, uid, seed.PASSWORD, model, method, args or [], kwargs or {})


def to_decimal(value):
    return Decimal(str(value or 0.0))


def round_amount(value):
    return to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def floor_amount(value):
    return to_decimal(value).quantize(WHOLE_ZLOTY, rounding=ROUND_DOWN)


def parse_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def format_money(value):
    return f"{round_amount(value):,.2f}"


def read_context(models, uid):
    payslips = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search_read",
        [[("state", "=", "confirmed")]],
        {
            "fields": [
                "id",
                "name",
                "employee_id",
                "contract_id",
                "company_id",
                "date_from",
                "date_to",
                "gross",
                "sick_days",
                "sick_days_100",
                "vacation_days",
                "vacation_pay",
                "sick_leave_amount",
                "sick_leave_basis",
                "working_days_in_month",
                "overtime_hours_150",
                "overtime_hours_200",
                "overtime_amount",
                "zus_emerytalne_ee",
                "zus_rentowe_ee",
                "zus_chorobowe_ee",
                "zus_total_ee",
                "health_basis",
                "health",
                "kup_amount",
                "taxable_income",
                "pit_advance",
                "pit_reducing",
                "pit_due",
                "ppk_ee",
                "net",
                "zus_emerytalne_er",
                "zus_rentowe_er",
                "zus_wypadkowe_er",
                "zus_fp",
                "zus_fgsp",
                "ppk_er",
                "total_employer_cost",
                "payslip_line_ids",
            ],
            "order": "employee_id, date_from asc, id asc",
            "limit": 2000,
        },
    )

    payslip_ids = [row["id"] for row in payslips]
    line_ids = sorted({line_id for row in payslips for line_id in row["payslip_line_ids"]})
    contract_ids = sorted({row["contract_id"][0] for row in payslips if row["contract_id"]})
    employee_ids = sorted({row["employee_id"][0] for row in payslips if row["employee_id"]})
    company_ids = sorted({row["company_id"][0] for row in payslips if row["company_id"]})

    lines = execute(
        models,
        uid,
        "pl.payroll.payslip.line",
        "read",
        [line_ids],
        {"fields": ["id", "payslip_id", "category", "amount"]},
    ) if line_ids else []

    contracts = execute(
        models,
        uid,
        "hr.contract",
        "read",
        [contract_ids],
        {
            "fields": [
                "id",
                "name",
                "employee_id",
                "company_id",
                "contract_type_id",
                "resource_calendar_id",
                "wage",
                "kup_type",
                "kup_autorskie_pct",
                "ppk_participation",
                "ppk_ee_rate",
                "ppk_additional",
                "pit2_filed",
                "ulga_type",
            ]
        },
    )

    employees = execute(
        models,
        uid,
        "hr.employee",
        "read",
        [employee_ids],
        {"fields": ["id", "name", "birthday", "is_student"]},
    )

    companies = execute(
        models,
        uid,
        "res.company",
        "read",
        [company_ids],
        {"fields": ["id", "name", "resource_calendar_id"]},
    )

    calendar_ids = set()
    for contract in contracts:
        if contract["resource_calendar_id"]:
            calendar_ids.add(contract["resource_calendar_id"][0])
    for company in companies:
        if company["resource_calendar_id"]:
            calendar_ids.add(company["resource_calendar_id"][0])

    attendances = execute(
        models,
        uid,
        "resource.calendar.attendance",
        "search_read",
        [[("calendar_id", "in", list(calendar_ids))]],
        {"fields": ["calendar_id", "hour_from", "hour_to"], "limit": 500},
    ) if calendar_ids else []

    line_map = defaultdict(list)
    for line in lines:
        if line["payslip_id"]:
            line_map[line["payslip_id"][0]].append(line)

    attendance_map = defaultdict(list)
    for row in attendances:
        if row["calendar_id"]:
            attendance_map[row["calendar_id"][0]].append(row)

    return {
        "payslips": payslips,
        "payslip_ids": payslip_ids,
        "line_map": line_map,
        "contracts": {row["id"]: row for row in contracts},
        "employees": {row["id"]: row for row in employees},
        "companies": {row["id"]: row for row in companies},
        "attendance_map": attendance_map,
    }


def get_parameter(models, uid, cache, code, target_date, company_id=False):
    key = (code, str(target_date), int(company_id or 0))
    if key not in cache:
        value = execute(
            models,
            uid,
            "pl.payroll.parameter",
            "get_value",
            [code, str(target_date), company_id or False],
        )
        if value is False:
            raise RuntimeError(f"Missing payroll parameter: {code} on {target_date}")
        cache[key] = to_decimal(value)
    return cache[key]


def get_line_totals(line_map, payslip_id):
    totals = {
        "bonus_gross_total": Decimal("0.00"),
        "deduction_gross_total": Decimal("0.00"),
        "deduction_net_total": Decimal("0.00"),
    }
    for line in line_map.get(payslip_id, []):
        amount = to_decimal(line["amount"])
        if line["category"] == "bonus_gross":
            totals["bonus_gross_total"] += amount
        elif line["category"] == "deduction_gross":
            totals["deduction_gross_total"] += amount
        elif line["category"] == "deduction_net":
            totals["deduction_net_total"] += amount
    for key in totals:
        totals[key] = round_amount(totals[key])
    return totals


def get_calendar_hours_per_week(attendance_map, calendar_id):
    if not calendar_id:
        return Decimal("0.00")
    total = Decimal("0.00")
    for row in attendance_map.get(calendar_id, []):
        hours = to_decimal(row["hour_to"]) - to_decimal(row["hour_from"])
        if hours > Decimal("0.00"):
            total += hours
    return total


def get_etat_fraction(contract, company, attendance_map):
    contract_calendar_id = contract["resource_calendar_id"] and contract["resource_calendar_id"][0]
    company_calendar_id = company["resource_calendar_id"] and company["resource_calendar_id"][0]
    contract_hours = get_calendar_hours_per_week(attendance_map, contract_calendar_id)
    company_hours = get_calendar_hours_per_week(attendance_map, company_calendar_id)
    if contract_hours <= Decimal("0.00") or company_hours <= Decimal("0.00"):
        return Decimal("1.00")
    fraction = contract_hours / company_hours
    return min(fraction, Decimal("1.00"))


def is_mandate_contract(contract):
    contract_type_name = (contract["contract_type_id"] and contract["contract_type_id"][1] or "").strip().lower()
    return contract_type_name == "umowa zlecenie"


def is_dzielo_contract(contract):
    contract_type_name = (contract["contract_type_id"] and contract["contract_type_id"][1] or "").strip().lower()
    return contract_type_name == "umowa o dzieło"


def is_student_zlecenie_exempt(employee, contract, payslip_date):
    if not is_mandate_contract(contract):
        return False
    if not employee["is_student"] or not employee["birthday"]:
        return False
    birthday = parse_date(employee["birthday"])
    age = payslip_date.year - birthday.year
    if (payslip_date.month, payslip_date.day) < (birthday.month, birthday.day):
        age -= 1
    return age < 26


def compute_overtime_amount(models, uid, cache, contract, payslip):
    base_gross = to_decimal(contract["wage"])
    overtime_150 = to_decimal(payslip["overtime_hours_150"])
    overtime_200 = to_decimal(payslip["overtime_hours_200"])
    if overtime_150 <= Decimal("0.00") and overtime_200 <= Decimal("0.00"):
        return Decimal("0.00")
    standard_hours = get_parameter(models, uid, cache, "STANDARD_MONTHLY_HOURS", payslip["date_to"])
    hourly_rate = base_gross / standard_hours
    return round_amount(overtime_150 * hourly_rate * Decimal("1.5") + overtime_200 * hourly_rate * Decimal("2.0"))


def compute_vacation_pay(models, uid, cache, contract, company, attendance_map, payslip, prior_expected):
    if is_mandate_contract(contract) or is_dzielo_contract(contract):
        return Decimal("0.00")
    vacation_days = to_decimal(payslip["vacation_days"])
    if vacation_days <= Decimal("0.00"):
        return Decimal("0.00")
    prior_three = prior_expected[-3:]
    if not prior_three:
        return Decimal("0.00")

    standard_hours = get_parameter(models, uid, cache, "STANDARD_MONTHLY_HOURS", payslip["date_to"])
    total_variable = sum((row["overtime_amount"] + row["bonus_gross_total"] for row in prior_three), Decimal("0.00"))
    total_hours_worked = sum((standard_hours * row["etat_fraction"] for row in prior_three), Decimal("0.00"))
    if total_variable <= Decimal("0.00") or total_hours_worked <= Decimal("0.00"):
        return Decimal("0.00")

    etat_fraction = get_etat_fraction(contract, company, attendance_map)
    vacation_hours = vacation_days * Decimal("8.00") * etat_fraction
    return round_amount(total_variable / total_hours_worked * vacation_hours)


def compute_sick_leave_basis(models, uid, cache, contract, prior_expected, target_date):
    prior_twelve = prior_expected[-12:]
    if not prior_twelve:
        wage = to_decimal(contract["wage"])
        zus_rate = (
            get_parameter(models, uid, cache, "ZUS_EMERY_EE", target_date)
            + get_parameter(models, uid, cache, "ZUS_RENT_EE", target_date)
            + get_parameter(models, uid, cache, "ZUS_CHOR_EE", target_date)
        ) / Decimal("100")
        return round_amount(wage * (Decimal("1.00") - zus_rate))

    total = sum((row["gross"] - row["zus_total_ee"] for row in prior_twelve), Decimal("0.00"))
    return round_amount(total / Decimal(str(len(prior_twelve))))


def get_adjusted_gross_for_sick(gross, working_days_in_month, sick_days, sick_days_100):
    total_sick = sick_days + sick_days_100
    if total_sick <= 0:
        return gross
    working_days = working_days_in_month or 30
    gross_reduction = round_amount(gross / Decimal(str(working_days)) * Decimal(str(total_sick)))
    return max(Decimal("0.00"), gross - gross_reduction)


def compute_tax_on_base(models, uid, cache, taxable_income, target_date):
    threshold = get_parameter(models, uid, cache, "PIT_THRESHOLD", target_date)
    rate_1 = get_parameter(models, uid, cache, "PIT_RATE_1", target_date)
    rate_2 = get_parameter(models, uid, cache, "PIT_RATE_2", target_date)
    if taxable_income <= threshold:
        return round_amount(taxable_income * rate_1 / Decimal("100"))
    return round_amount(
        threshold * rate_1 / Decimal("100")
        + (taxable_income - threshold) * rate_2 / Decimal("100")
    )


def compute_single_payslip(models, uid, cache, context, payslip, prior_expected):
    contract = context["contracts"][payslip["contract_id"][0]]
    employee = context["employees"][payslip["employee_id"][0]]
    company = context["companies"][payslip["company_id"][0]]
    line_totals = get_line_totals(context["line_map"], payslip["id"])
    date_from = parse_date(payslip["date_from"])
    date_to = parse_date(payslip["date_to"])
    etat_fraction = get_etat_fraction(contract, company, context["attendance_map"])
    base_gross = to_decimal(contract["wage"])
    overtime_amount = compute_overtime_amount(models, uid, cache, contract, payslip)
    vacation_pay = compute_vacation_pay(
        models,
        uid,
        cache,
        contract,
        company,
        context["attendance_map"],
        payslip,
        prior_expected,
    )
    gross = round_amount(
        base_gross
        + overtime_amount
        + vacation_pay
        + line_totals["bonus_gross_total"]
        - line_totals["deduction_gross_total"]
    )

    if is_dzielo_contract(contract):
        if gross <= Decimal("200.00"):
            kup_amount = Decimal("0.00")
            taxable_income = gross
            pit_advance = round_amount(gross * Decimal("0.12"))
        else:
            if contract["kup_type"] == "autorskie":
                kup_amount = round_amount(gross * Decimal("0.50"))
            else:
                kup_amount = round_amount(gross * Decimal("0.20"))
            taxable_income = floor_amount(gross - kup_amount)
            pit_advance = round_amount(taxable_income * Decimal("0.12"))

        pit_due = floor_amount(pit_advance)
        net = round_amount(gross - pit_due - line_totals["deduction_net_total"])
        return {
            "gross": gross,
            "bonus_gross_total": line_totals["bonus_gross_total"],
            "deduction_gross_total": line_totals["deduction_gross_total"],
            "deduction_net_total": line_totals["deduction_net_total"],
            "overtime_amount": overtime_amount,
            "vacation_pay": Decimal("0.00"),
            "sick_leave_basis": Decimal("0.00"),
            "sick_leave_amount": Decimal("0.00"),
            "adjusted_gross": gross,
            "effective_gross": gross,
            "etat_fraction": etat_fraction,
            "zus_emerytalne_ee": Decimal("0.00"),
            "zus_rentowe_ee": Decimal("0.00"),
            "zus_chorobowe_ee": Decimal("0.00"),
            "zus_total_ee": Decimal("0.00"),
            "health_basis": Decimal("0.00"),
            "health_basis_raw": Decimal("0.00"),
            "health": Decimal("0.00"),
            "kup_amount": kup_amount,
            "taxable_income": taxable_income,
            "pit_advance": pit_advance,
            "pit_reducing": Decimal("0.00"),
            "pit_due": pit_due,
            "ppk_ee": Decimal("0.00"),
            "net": net,
            "zus_emerytalne_er": Decimal("0.00"),
            "zus_rentowe_er": Decimal("0.00"),
            "zus_wypadkowe_er": Decimal("0.00"),
            "zus_fp": Decimal("0.00"),
            "zus_fgsp": Decimal("0.00"),
            "ppk_er": Decimal("0.00"),
            "total_employer_cost": gross,
            "sick_days_total": 0,
            "date_from": date_from,
            "date_to": date_to,
        }

    sick_days = payslip["sick_days"] or 0
    sick_days_100 = payslip["sick_days_100"] or 0
    sick_days_total = sick_days + sick_days_100
    sick_leave_basis = Decimal("0.00")
    sick_leave_amount = Decimal("0.00")
    adjusted_gross = gross
    if sick_days_total > 0:
        sick_leave_basis = compute_sick_leave_basis(models, uid, cache, contract, prior_expected, date_to)
        daily_rate = sick_leave_basis / Decimal("30")
        sick_leave_amount = round_amount(
            daily_rate * Decimal(str(sick_days)) * Decimal("0.80")
            + daily_rate * Decimal(str(sick_days_100)) * Decimal("1.00")
        )
        adjusted_gross = get_adjusted_gross_for_sick(
            gross,
            payslip["working_days_in_month"] or 30,
            sick_days,
            sick_days_100,
        )
    effective_gross = round_amount(adjusted_gross + sick_leave_amount)

    ytd_expected = [
        row
        for row in prior_expected
        if row["date_from"].year == date_from.year and row["date_from"] < date_from
    ]
    ytd_gross = sum((row["effective_gross"] for row in ytd_expected), Decimal("0.00"))
    ytd_zus_basis = sum((row["adjusted_gross"] for row in ytd_expected), Decimal("0.00"))
    ytd_pit_reducing = sum((row["pit_reducing"] for row in ytd_expected), Decimal("0.00"))
    ytd_pit_paid = sum((row["pit_due"] for row in ytd_expected), Decimal("0.00"))
    ytd_pit_taxable = sum(
        (row["taxable_income"] for row in ytd_expected if row["pit_advance"] > Decimal("0.00")),
        Decimal("0.00"),
    )

    zus_cap = get_parameter(models, uid, cache, "ZUS_BASIS_CAP", date_to)
    if ytd_zus_basis >= zus_cap:
        zus_cap_basis = Decimal("0.00")
    else:
        zus_cap_basis = min(adjusted_gross, zus_cap - ytd_zus_basis)

    exempt = is_student_zlecenie_exempt(employee, contract, date_from)
    if exempt:
        zus_emerytalne_ee = Decimal("0.00")
        zus_rentowe_ee = Decimal("0.00")
        zus_chorobowe_ee = Decimal("0.00")
        zus_total_ee = Decimal("0.00")
    else:
        zus_emerytalne_ee = round_amount(
            zus_cap_basis * get_parameter(models, uid, cache, "ZUS_EMERY_EE", date_to) / Decimal("100")
        )
        zus_rentowe_ee = round_amount(
            zus_cap_basis * get_parameter(models, uid, cache, "ZUS_RENT_EE", date_to) / Decimal("100")
        )
        zus_chorobowe_ee = round_amount(
            adjusted_gross * get_parameter(models, uid, cache, "ZUS_CHOR_EE", date_to) / Decimal("100")
        )
        zus_total_ee = round_amount(zus_emerytalne_ee + zus_rentowe_ee + zus_chorobowe_ee)

    health_basis_raw = round_amount(adjusted_gross - zus_total_ee + sick_leave_amount)
    if exempt:
        health_basis = health_basis_raw
        health = Decimal("0.00")
        ppk_er = Decimal("0.00")
    else:
        minimum_wage = get_parameter(models, uid, cache, "MINIMUM_WAGE", date_to)
        minimum_gross = round_amount(minimum_wage * etat_fraction)
        zus_rate = (
            get_parameter(models, uid, cache, "ZUS_EMERY_EE", date_to)
            + get_parameter(models, uid, cache, "ZUS_RENT_EE", date_to)
            + get_parameter(models, uid, cache, "ZUS_CHOR_EE", date_to)
        ) / Decimal("100")
        minimum_health_basis = round_amount(minimum_gross * (Decimal("1.00") - zus_rate))
        health_basis = max(health_basis_raw, minimum_health_basis)
        health = round_amount(
            health_basis * get_parameter(models, uid, cache, "HEALTH", date_to) / Decimal("100")
        )
        if contract["ppk_participation"] == "opt_out":
            ppk_er = Decimal("0.00")
        else:
            ppk_er = round_amount(
                adjusted_gross * get_parameter(models, uid, cache, "PPK_ER", date_to) / Decimal("100")
            )

    if contract["kup_type"] == "autorskie":
        kup_amount = round_amount(health_basis_raw * to_decimal(contract["kup_autorskie_pct"]) / Decimal("100") * Decimal("0.50"))
    elif contract["kup_type"] == "standard_20":
        kup_amount = round_amount(health_basis_raw * Decimal("0.20"))
    else:
        kup_amount = round_amount(get_parameter(models, uid, cache, "KUP_STANDARD", date_to) * etat_fraction)

    taxable_income = floor_amount(health_basis_raw - kup_amount + ppk_er)
    pit_advance = Decimal("0.00")
    pit_reducing = Decimal("0.00")
    pit_due = Decimal("0.00")
    threshold = get_parameter(models, uid, cache, "PIT_THRESHOLD", date_to)

    if contract["ulga_type"] in ("mlodzi", "na_powrot", "rodzina_4_plus", "senior") and ytd_gross + effective_gross <= threshold:
        pit_advance = Decimal("0.00")
        pit_reducing = Decimal("0.00")
        pit_due = Decimal("0.00")
    else:
        pit_before = compute_tax_on_base(models, uid, cache, ytd_pit_taxable, date_to)
        pit_cumulative = compute_tax_on_base(models, uid, cache, ytd_pit_taxable + taxable_income, date_to)
        pit_advance = round_amount(pit_cumulative - pit_before)
        if contract["pit2_filed"] and not is_mandate_contract(contract):
            pit_reducing = round_amount(get_parameter(models, uid, cache, "PIT_REDUCING", date_to))
        pit_due = floor_amount(max(Decimal("0.00"), pit_cumulative - (ytd_pit_reducing + pit_reducing) - ytd_pit_paid))

    if exempt or contract["ppk_participation"] == "opt_out":
        ppk_ee = Decimal("0.00")
    else:
        if contract["ppk_participation"] == "reduced":
            base_ppk_rate = get_parameter(models, uid, cache, "PPK_EE_REDUCED", date_to)
        else:
            base_ppk_rate = to_decimal(contract["ppk_ee_rate"])
        ppk_ee = round_amount(adjusted_gross * (base_ppk_rate + to_decimal(contract["ppk_additional"])) / Decimal("100"))

    net = round_amount(effective_gross - zus_total_ee - health - pit_due - ppk_ee - line_totals["deduction_net_total"])

    if exempt:
        zus_emerytalne_er = Decimal("0.00")
        zus_rentowe_er = Decimal("0.00")
        zus_wypadkowe_er = Decimal("0.00")
        zus_fp = Decimal("0.00")
        zus_fgsp = Decimal("0.00")
    else:
        zus_emerytalne_er = round_amount(
            zus_cap_basis * get_parameter(models, uid, cache, "ZUS_EMERY_ER", date_to) / Decimal("100")
        )
        zus_rentowe_er = round_amount(
            zus_cap_basis * get_parameter(models, uid, cache, "ZUS_RENT_ER", date_to) / Decimal("100")
        )
        zus_wypadkowe_er = round_amount(
            adjusted_gross * get_parameter(models, uid, cache, "ZUS_WYPAD_ER", date_to, company["id"]) / Decimal("100")
        )
        zus_fp = round_amount(adjusted_gross * get_parameter(models, uid, cache, "ZUS_FP", date_to) / Decimal("100"))
        zus_fgsp = round_amount(adjusted_gross * get_parameter(models, uid, cache, "ZUS_FGSP", date_to) / Decimal("100"))

    total_employer_cost = round_amount(
        effective_gross
        + zus_emerytalne_er
        + zus_rentowe_er
        + zus_wypadkowe_er
        + zus_fp
        + zus_fgsp
        + ppk_er
    )

    return {
        "gross": gross,
        "bonus_gross_total": line_totals["bonus_gross_total"],
        "deduction_gross_total": line_totals["deduction_gross_total"],
        "deduction_net_total": line_totals["deduction_net_total"],
        "overtime_amount": overtime_amount,
        "vacation_pay": vacation_pay,
        "sick_leave_basis": sick_leave_basis,
        "sick_leave_amount": sick_leave_amount,
        "adjusted_gross": adjusted_gross,
        "effective_gross": effective_gross,
        "etat_fraction": etat_fraction,
        "zus_emerytalne_ee": zus_emerytalne_ee,
        "zus_rentowe_ee": zus_rentowe_ee,
        "zus_chorobowe_ee": zus_chorobowe_ee,
        "zus_total_ee": zus_total_ee,
        "health_basis": health_basis,
        "health_basis_raw": health_basis_raw,
        "health": health,
        "kup_amount": kup_amount,
        "taxable_income": taxable_income,
        "pit_advance": pit_advance,
        "pit_reducing": pit_reducing,
        "pit_due": pit_due,
        "ppk_ee": ppk_ee,
        "net": net,
        "zus_emerytalne_er": zus_emerytalne_er,
        "zus_rentowe_er": zus_rentowe_er,
        "zus_wypadkowe_er": zus_wypadkowe_er,
        "zus_fp": zus_fp,
        "zus_fgsp": zus_fgsp,
        "ppk_er": ppk_er,
        "total_employer_cost": total_employer_cost,
        "sick_days_total": sick_days_total,
        "date_from": date_from,
        "date_to": date_to,
    }


def compare_payslip(actual, expected):
    comparisons = [
        "gross",
        "overtime_amount",
        "vacation_pay",
        "sick_leave_basis",
        "sick_leave_amount",
        "zus_emerytalne_ee",
        "zus_rentowe_ee",
        "zus_chorobowe_ee",
        "zus_total_ee",
        "health_basis",
        "health",
        "kup_amount",
        "taxable_income",
        "pit_advance",
        "pit_reducing",
        "pit_due",
        "ppk_ee",
        "net",
        "zus_emerytalne_er",
        "zus_rentowe_er",
        "zus_wypadkowe_er",
        "zus_fp",
        "zus_fgsp",
        "ppk_er",
        "total_employer_cost",
    ]
    diffs = []
    for field_name in comparisons:
        actual_value = round_amount(actual[field_name])
        expected_value = round_amount(expected[field_name])
        delta = abs(actual_value - expected_value)
        if delta > TOLERANCE:
            diffs.append((field_name, actual_value, expected_value, delta))
    return diffs


def verify_confirmed_payslips(models, uid, context):
    cache = {}
    by_employee = defaultdict(list)
    for payslip in context["payslips"]:
        by_employee[payslip["employee_id"][0]].append(payslip)

    employee_rows = []
    all_diffs = []
    expected_history = {}

    for employee_id, payslips in sorted(by_employee.items(), key=lambda item: item[1][0]["employee_id"][1]):
        prior_expected = []
        employee_max_delta = Decimal("0.00")
        employee_diff_count = 0
        for payslip in payslips:
            expected = compute_single_payslip(models, uid, cache, context, payslip, prior_expected)
            diffs = compare_payslip(payslip, expected)
            for diff in diffs:
                employee_max_delta = max(employee_max_delta, diff[3])
            employee_diff_count += len(diffs)
            prior_expected.append(expected)
            all_diffs.extend(
                {
                    "employee": payslip["employee_id"][1],
                    "period": payslip["date_from"][:7],
                    "field": field_name,
                    "actual": actual_value,
                    "expected": expected_value,
                    "delta": delta,
                }
                for field_name, actual_value, expected_value, delta in diffs
            )
        expected_history[employee_id] = prior_expected
        employee_rows.append(
            {
                "employee": payslips[0]["employee_id"][1],
                "months": len(payslips),
                "max_delta": employee_max_delta,
                "diff_count": employee_diff_count,
            }
        )

    return employee_rows, all_diffs, expected_history


def format_table(rows, headers):
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))
    header_line = " | ".join(str(headers[index]).ljust(widths[index]) for index in range(len(headers)))
    separator = "-+-".join("-" * widths[index] for index in range(len(headers)))
    lines = [header_line, separator]
    for row in rows:
        lines.append(" | ".join(str(row[index]).ljust(widths[index]) for index in range(len(row))))
    return lines


def verify_pit11(models, uid, context):
    existing_ids = execute(models, uid, "pl.payroll.pit11", "search", [[]])
    if existing_ids:
        execute(models, uid, "pl.payroll.pit11", "unlink", [existing_ids])

    wizard_id = execute(models, uid, "pl.payroll.pit11.wizard", "create", [{"year": TARGET_YEAR}])
    execute(models, uid, "pl.payroll.pit11.wizard", "action_generate", [[wizard_id]])

    records = execute(
        models,
        uid,
        "pl.payroll.pit11",
        "search_read",
        [[("year", "=", TARGET_YEAR)]],
        {
            "fields": [
                "employee_id",
                "company_id",
                "total_gross",
                "total_zus_ee",
                "total_health",
                "health_deductible",
                "total_kup",
                "total_income",
                "total_pit_paid",
                "total_ppk_er",
                "payslip_count",
            ],
            "limit": 200,
        },
    )

    expected = {}
    for payslip in context["payslips"]:
        if parse_date(payslip["date_from"]).year != TARGET_YEAR:
            continue
        key = (payslip["employee_id"][0], payslip["company_id"][0])
        bucket = expected.setdefault(
            key,
            {
                "employee": payslip["employee_id"][1],
                "company": payslip["company_id"][1],
                "total_gross": Decimal("0.00"),
                "total_zus_ee": Decimal("0.00"),
                "total_health": Decimal("0.00"),
                "health_deductible": Decimal("0.00"),
                "total_kup": Decimal("0.00"),
                "total_income": Decimal("0.00"),
                "total_pit_paid": Decimal("0.00"),
                "total_ppk_er": Decimal("0.00"),
                "payslip_count": 0,
            },
        )
        effective_gross = round_amount(
            to_decimal(payslip["gross"])
            if (payslip["sick_days"] or 0) + (payslip["sick_days_100"] or 0) <= 0
            else get_adjusted_gross_for_sick(
                to_decimal(payslip["gross"]),
                payslip["working_days_in_month"] or 30,
                payslip["sick_days"] or 0,
                payslip["sick_days_100"] or 0,
            ) + to_decimal(payslip["sick_leave_amount"])
        )
        bucket["total_gross"] += effective_gross + to_decimal(payslip["ppk_er"])
        bucket["total_zus_ee"] += to_decimal(payslip["zus_total_ee"])
        bucket["total_health"] += to_decimal(payslip["health"])
        bucket["health_deductible"] += round_amount(to_decimal(payslip["health_basis"]) * Decimal("0.0775"))
        bucket["total_kup"] += to_decimal(payslip["kup_amount"])
        bucket["total_income"] += to_decimal(payslip["taxable_income"])
        bucket["total_pit_paid"] += to_decimal(payslip["pit_due"])
        bucket["total_ppk_er"] += to_decimal(payslip["ppk_er"])
        bucket["payslip_count"] += 1

    diffs = []
    for record in records:
        key = (record["employee_id"][0], record["company_id"][0])
        bucket = expected[key]
        checks = [
            ("total_gross", round_amount(bucket["total_gross"]), round_amount(record["total_gross"])),
            ("total_zus_ee", round_amount(bucket["total_zus_ee"]), round_amount(record["total_zus_ee"])),
            ("total_health", round_amount(bucket["total_health"]), round_amount(record["total_health"])),
            ("health_deductible", round_amount(bucket["health_deductible"]), round_amount(record["health_deductible"])),
            ("total_kup", round_amount(bucket["total_kup"]), round_amount(record["total_kup"])),
            ("total_income", round_amount(bucket["total_income"]), round_amount(record["total_income"])),
            ("total_pit_paid", round_amount(bucket["total_pit_paid"]), round_amount(record["total_pit_paid"])),
            ("total_ppk_er", round_amount(bucket["total_ppk_er"]), round_amount(record["total_ppk_er"])),
            ("payslip_count", bucket["payslip_count"], record["payslip_count"]),
        ]
        for field_name, expected_value, actual_value in checks:
            if isinstance(expected_value, Decimal):
                if abs(expected_value - actual_value) > TOLERANCE:
                    diffs.append((bucket["employee"], field_name, actual_value, expected_value))
            elif expected_value != actual_value:
                diffs.append((bucket["employee"], field_name, actual_value, expected_value))

    return {
        "record_count": len(records),
        "expected_count": len(expected),
        "diffs": diffs,
    }


def verify_zus_dra(models, uid, context):
    existing_ids = execute(models, uid, "pl.payroll.zus.dra", "search", [[]])
    if existing_ids:
        execute(models, uid, "pl.payroll.zus.dra", "unlink", [existing_ids])

    wizard_id = execute(
        models,
        uid,
        "pl.payroll.zus.dra.wizard",
        "create",
        [{"year": TARGET_DRA_YEAR, "month": TARGET_DRA_MONTH}],
    )
    execute(models, uid, "pl.payroll.zus.dra.wizard", "action_generate", [[wizard_id]])

    records = execute(
        models,
        uid,
        "pl.payroll.zus.dra",
        "search_read",
        [[("year", "=", TARGET_DRA_YEAR), ("month", "=", TARGET_DRA_MONTH)]],
        {
            "fields": [
                "id",
                "company_id",
                "employee_count",
                "payslip_count",
                "total_emerytalne_ee",
                "total_emerytalne_er",
                "total_rentowe_ee",
                "total_rentowe_er",
                "total_chorobowe",
                "total_wypadkowe",
                "total_health",
                "total_fp",
                "total_fgsp",
                "total_zus_employee",
                "total_zus_employer",
                "total_all",
                "line_ids",
            ],
            "limit": 20,
        },
    )

    january_payslips = [
        row for row in context["payslips"]
        if row["date_from"] == f"{TARGET_DRA_YEAR}-{TARGET_DRA_MONTH:02d}-01"
    ]
    by_company = defaultdict(list)
    for payslip in january_payslips:
        by_company[payslip["company_id"][0]].append(payslip)

    diffs = []
    for record in records:
        company_id = record["company_id"][0]
        payslips = by_company[company_id]
        expected = {
            "employee_count": len({row["employee_id"][0] for row in payslips}),
            "payslip_count": len(payslips),
            "total_emerytalne_ee": round_amount(sum((to_decimal(row["zus_emerytalne_ee"]) for row in payslips), Decimal("0.00"))),
            "total_emerytalne_er": round_amount(sum((to_decimal(row["zus_emerytalne_er"]) for row in payslips), Decimal("0.00"))),
            "total_rentowe_ee": round_amount(sum((to_decimal(row["zus_rentowe_ee"]) for row in payslips), Decimal("0.00"))),
            "total_rentowe_er": round_amount(sum((to_decimal(row["zus_rentowe_er"]) for row in payslips), Decimal("0.00"))),
            "total_chorobowe": round_amount(sum((to_decimal(row["zus_chorobowe_ee"]) for row in payslips), Decimal("0.00"))),
            "total_wypadkowe": round_amount(sum((to_decimal(row["zus_wypadkowe_er"]) for row in payslips), Decimal("0.00"))),
            "total_health": round_amount(sum((to_decimal(row["health"]) for row in payslips), Decimal("0.00"))),
            "total_fp": round_amount(sum((to_decimal(row["zus_fp"]) for row in payslips), Decimal("0.00"))),
            "total_fgsp": round_amount(sum((to_decimal(row["zus_fgsp"]) for row in payslips), Decimal("0.00"))),
        }
        expected["total_zus_employee"] = round_amount(
            expected["total_emerytalne_ee"]
            + expected["total_rentowe_ee"]
            + expected["total_chorobowe"]
            + expected["total_health"]
        )
        expected["total_zus_employer"] = round_amount(
            expected["total_emerytalne_er"]
            + expected["total_rentowe_er"]
            + expected["total_wypadkowe"]
            + expected["total_fp"]
            + expected["total_fgsp"]
        )
        expected["total_all"] = round_amount(expected["total_zus_employee"] + expected["total_zus_employer"])

        for field_name, expected_value in expected.items():
            actual_value = record[field_name]
            if isinstance(expected_value, Decimal):
                actual_value = round_amount(actual_value)
                if abs(expected_value - actual_value) > TOLERANCE:
                    diffs.append((record["company_id"][1], field_name, actual_value, expected_value))
            elif expected_value != actual_value:
                diffs.append((record["company_id"][1], field_name, actual_value, expected_value))

        line_count = len(record["line_ids"])
        if line_count != expected["payslip_count"]:
            diffs.append((record["company_id"][1], "line_ids", line_count, expected["payslip_count"]))

    return {
        "record_count": len(records),
        "expected_count": len(by_company),
        "diffs": diffs,
    }


def verify_batch_wizard(models, uid, context, expected_history):
    month_start = BATCH_MONTH.isoformat()
    month_end = date(BATCH_MONTH.year, BATCH_MONTH.month, calendar.monthrange(BATCH_MONTH.year, BATCH_MONTH.month)[1]).isoformat()

    existing = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search_read",
        [[("date_from", "=", month_start), ("date_to", "=", month_end)]],
        {"fields": ["id", "employee_id", "payslip_line_ids", "state", "company_id"], "limit": 200},
    )
    existing_ids = [row["id"] for row in existing]
    existing_line_ids = sorted({line_id for row in existing for line_id in row["payslip_line_ids"]})
    if existing_line_ids:
        execute(models, uid, "pl.payroll.payslip.line", "unlink", [existing_line_ids])
    if existing_ids:
        execute(models, uid, "pl.payroll.payslip", "unlink", [existing_ids])

    company_id = existing[0]["company_id"][0] if existing else execute(
        models, uid, "res.users", "read", [[uid]], {"fields": ["company_id"]}
    )[0]["company_id"][0]
    deleted_count = len(existing_ids)

    wizard_id = execute(
        models,
        uid,
        "pl.payroll.batch.wizard",
        "create",
        [{
            "date_from": month_start,
            "date_to": month_end,
            "company_id": company_id,
            "auto_compute": True,
        }],
    )
    execute(models, uid, "pl.payroll.batch.wizard", "action_generate", [[wizard_id]])

    recreated = execute(
        models,
        uid,
        "pl.payroll.payslip",
        "search_read",
        [[("date_from", "=", month_start), ("date_to", "=", month_end)]],
        {
            "fields": [
                "id",
                "employee_id",
                "contract_id",
                "company_id",
                "date_from",
                "date_to",
                "state",
                "gross",
                "sick_days",
                "sick_days_100",
                "vacation_days",
                "vacation_pay",
                "sick_leave_amount",
                "sick_leave_basis",
                "working_days_in_month",
                "overtime_hours_150",
                "overtime_hours_200",
                "overtime_amount",
                "zus_emerytalne_ee",
                "zus_rentowe_ee",
                "zus_chorobowe_ee",
                "zus_total_ee",
                "health_basis",
                "health",
                "kup_amount",
                "taxable_income",
                "pit_advance",
                "pit_reducing",
                "pit_due",
                "ppk_ee",
                "net",
                "zus_emerytalne_er",
                "zus_rentowe_er",
                "zus_wypadkowe_er",
                "zus_fp",
                "zus_fgsp",
                "ppk_er",
                "total_employer_cost",
                "payslip_line_ids",
            ],
            "order": "employee_id, id",
            "limit": 200,
        },
    )

    cache = {}
    diffs = []
    states = defaultdict(int)
    for payslip in recreated:
        states[payslip["state"]] += 1
        employee_id = payslip["employee_id"][0]
        prior_expected = [
            row for row in expected_history[employee_id]
            if row["date_from"] < parse_date(payslip["date_from"])
        ]
        expected = compute_single_payslip(models, uid, cache, context, payslip, prior_expected)
        for field_name, actual_value, expected_value, delta in compare_payslip(payslip, expected):
            diffs.append((payslip["employee_id"][1], field_name, actual_value, expected_value, delta))

    return {
        "deleted_count": deleted_count,
        "recreated_count": len(recreated),
        "states": dict(states),
        "diffs": diffs,
    }


def build_scenarios(models, uid, context):
    scenario_rows = []
    name_to_slips = defaultdict(list)
    for payslip in context["payslips"]:
        name_to_slips[payslip["employee_id"][1]].append(payslip)

    def first_for(name, month):
        for row in name_to_slips.get(name, []):
            if row["date_from"] == month:
                return row
        return None

    standard = first_for("Tomasz Kowalski", "2026-02-01")
    scenario_rows.append(("Tomasz Kowalski", "standard", "OK" if standard else "MISSING", format_money(standard["net"]) if standard else "-"))

    creative = first_for("Michał Adamski", "2025-01-01")
    scenario_rows.append(("Michał Adamski", "autorskie 50%", "OK" if creative else "MISSING", format_money(creative["kup_amount"]) if creative else "-"))

    opt_out = first_for("Monika Brzeska", "2025-01-01")
    scenario_rows.append(("Monika Brzeska", "PPK opt-out", "OK" if opt_out and round_amount(opt_out["ppk_ee"]) == Decimal("0.00") else "FAIL", format_money(opt_out["ppk_ee"]) if opt_out else "-"))

    september = first_for("Aleksander Volkov", "2025-09-01")
    october = first_for("Aleksander Volkov", "2025-10-01")
    crossing = "FAIL"
    detail = "-"
    if september and october:
        crossing = "OK" if round_amount(october["pit_due"]) >= round_amount(september["pit_due"]) else "FAIL"
        detail = f"{format_money(september['pit_due'])} -> {format_money(october['pit_due'])}"
    scenario_rows.append(("Aleksander Volkov", "threshold crossing", crossing, detail))

    student = first_for("Jakub Wiśniewski", "2025-07-01")
    student_ok = student and round_amount(student["zus_total_ee"]) == Decimal("0.00") and round_amount(student["health"]) == Decimal("0.00")
    scenario_rows.append(("Jakub Wiśniewski", "student zlecenie", "OK" if student_ok else "FAIL", f"ZUS={format_money(student['zus_total_ee'])}, health={format_money(student['health'])}" if student else "-"))

    dzielo = first_for("Bartosz Nowicki", "2025-11-01")
    dzielo_ok = dzielo and round_amount(dzielo["zus_total_ee"]) == Decimal("0.00") and round_amount(dzielo["health"]) == Decimal("0.00")
    scenario_rows.append(("Bartosz Nowicki", "dzieło", "OK" if dzielo_ok else "FAIL", f"net={format_money(dzielo['net'])}" if dzielo else "-"))

    part_time = first_for("Natalia Ivanchuk", "2025-04-01")
    scenario_rows.append(("Natalia Ivanchuk", "half-time", "OK" if part_time else "MISSING", format_money(part_time["kup_amount"]) if part_time else "-"))

    sick = first_for("Tomasz Kowalski", "2025-10-01")
    sick_ok = sick and round_amount(sick["sick_leave_amount"]) > Decimal("0.00")
    scenario_rows.append(("Tomasz Kowalski", "sick leave 80%", "OK" if sick_ok else "FAIL", format_money(sick["sick_leave_amount"]) if sick else "-"))

    return scenario_rows


def print_section(title):
    print("")
    print(title)
    print("=" * len(title))


def main():
    uid, models = connect()
    context = read_context(models, uid)

    employee_rows, calc_diffs, expected_history = verify_confirmed_payslips(models, uid, context)
    pit11_result = verify_pit11(models, uid, context)
    dra_result = verify_zus_dra(models, uid, context)
    batch_result = verify_batch_wizard(models, uid, context, expected_history)
    scenario_rows = build_scenarios(models, uid, context)

    print_section("Calculation Summary")
    summary_table = format_table(
        [
            (
                row["employee"],
                row["months"],
                row["diff_count"],
                format_money(row["max_delta"]),
            )
            for row in employee_rows
        ],
        ("Employee", "Months", "Diffs", "Max delta"),
    )
    for line in summary_table:
        print(line)

    print_section("Scenario Checks")
    for line in format_table(scenario_rows, ("Employee", "Scenario", "Status", "Detail")):
        print(line)

    print_section("PIT-11 Check")
    print(f"Records: {pit11_result['record_count']} / expected {pit11_result['expected_count']}")
    print(f"Differences: {len(pit11_result['diffs'])}")
    for employee, field_name, actual, expected in pit11_result["diffs"][:10]:
        print(f"- {employee}: {field_name} actual={actual} expected={expected}")

    print_section("ZUS DRA Check")
    print(f"Records: {dra_result['record_count']} / expected {dra_result['expected_count']}")
    print(f"Differences: {len(dra_result['diffs'])}")
    for company, field_name, actual, expected in dra_result["diffs"][:10]:
        print(f"- {company}: {field_name} actual={actual} expected={expected}")

    print_section("Batch Wizard Check")
    print(f"Deleted payslips: {batch_result['deleted_count']}")
    print(f"Recreated payslips: {batch_result['recreated_count']}")
    print(f"States: {batch_result['states']}")
    print(f"Differences: {len(batch_result['diffs'])}")
    for employee, field_name, actual, expected, delta in batch_result["diffs"][:10]:
        print(f"- {employee}: {field_name} actual={actual} expected={expected} delta={delta}")

    print_section("Top Calculation Differences")
    sorted_diffs = sorted(calc_diffs, key=lambda row: row["delta"], reverse=True)
    for diff in sorted_diffs[:15]:
        print(
            f"- {diff['employee']} {diff['period']} {diff['field']}: "
            f"actual={diff['actual']} expected={diff['expected']} delta={diff['delta']}"
        )

    total_failures = len(calc_diffs) + len(pit11_result["diffs"]) + len(dra_result["diffs"]) + len(batch_result["diffs"])
    print("")
    print(f"TOTAL_FAILURES={total_failures}")

    return 1 if total_failures else 0


if __name__ == "__main__":
    sys.exit(main())
