# ⚠️ FICTIONAL TEST DATA — nie sa to dane prawdziwych osob.
# Generated for testing purposes only. PESEL numbers have invalid checksums.

import argparse
import json
from copy import deepcopy
from datetime import date


FICTIONAL_COMPANY = {
    "name": "Payroll Fiction Sp. z o.o.",
    "nip": "1234563219",
}

SCENARIO_BLUEPRINTS = [
    {
        "scenario_no": 1,
        "employee": {
            "name": "Jan Kowalski",
            "birthday": "1990-01-15",
            "gender": "male",
            "country_xmlid": "base.pl",
            "street": "ul. Lipowa 12/3",
            "city": "Warszawa",
            "zip": "00-215",
        },
        "contract": {
            "name": "Scenario 1 - Umowa o prace",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 6000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 2,
        "employee": {
            "name": "Anna Nowak",
            "birthday": "1988-04-02",
            "gender": "female",
            "country_xmlid": "base.pl",
            "street": "ul. Kwiatowa 7/8",
            "city": "Krakow",
            "zip": "30-102",
        },
        "contract": {
            "name": "Scenario 2 - Umowa o prace autorskie",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 15000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "autorskie",
            "kup_autorskie_pct": 50.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 3,
        "employee": {
            "name": "Piotr Wisniewski",
            "birthday": "1985-07-23",
            "gender": "male",
            "country_xmlid": "base.pl",
            "street": "ul. Brzozowa 44",
            "city": "Gdansk",
            "zip": "80-221",
        },
        "contract": {
            "name": "Scenario 3 - Umowa o prace bez PPK",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 12000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "opt_out",
            "ppk_ee_rate": 0.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 4,
        "employee": {
            "name": "Maria Wojcik",
            "birthday": "1993-11-09",
            "gender": "female",
            "country_xmlid": "base.pl",
            "street": "ul. Spacerowa 19",
            "city": "Lodz",
            "zip": "90-402",
        },
        "contract": {
            "name": "Scenario 4 - Minimalne wynagrodzenie",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 4806.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 5,
        "employee": {
            "name": "Jakub Kaminski",
            "birthday": "1998-02-17",
            "gender": "male",
            "country_xmlid": "base.pl",
            "street": "ul. Slowackiego 21/6",
            "city": "Poznan",
            "zip": "60-825",
        },
        "contract": {
            "name": "Scenario 5 - Pol etatu",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 3000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 6,
        "employee": {
            "name": "Oleg Shevchenko",
            "birthday": "2002-05-14",
            "gender": "male",
            "country_xmlid": "base.ua",
            "street": "ul. Bema 14/2",
            "city": "Wroclaw",
            "zip": "50-265",
        },
        "contract": {
            "name": "Scenario 6 - Ulga dla mlodych",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 8000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "mlodzi",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 7,
        "employee": {
            "name": "Katarzyna Lewandowska",
            "birthday": "1987-09-30",
            "gender": "female",
            "country_xmlid": "base.pl",
            "street": "ul. Dluga 3/11",
            "city": "Gdynia",
            "zip": "81-363",
        },
        "contract": {
            "name": "Scenario 7 - PPK dodatkowe",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 25000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "additional",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 2.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 8,
        "employee": {
            "name": "Tomasz Zielinski",
            "birthday": "1995-06-05",
            "gender": "male",
            "country_xmlid": "base.pl",
            "street": "ul. Morska 88/4",
            "city": "Szczecin",
            "zip": "70-543",
        },
        "contract": {
            "name": "Scenario 8 - Umowa zlecenie 160h x 35 PLN",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uz",
            "wage": 5600.0,
            "hourly_rate": 35.0,
            "assumed_hours": 160,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard_20",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "opt_out",
            "ppk_ee_rate": 0.0,
            "ppk_additional": 0.0,
            "pit2_filed": False,
            "ulga_type": "none",
            "zus_code": "0411",
        },
    },
    {
        "scenario_no": 9,
        "employee": {
            "name": "Natalia Kravchuk",
            "birthday": "1996-08-18",
            "gender": "female",
            "country_xmlid": "base.ua",
            "street": "ul. Mickiewicza 5/7",
            "city": "Katowice",
            "zip": "40-084",
        },
        "contract": {
            "name": "Scenario 9 - Umowa zlecenie autorskie 160h x 40 PLN",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uz",
            "wage": 6400.0,
            "hourly_rate": 40.0,
            "assumed_hours": 160,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "autorskie",
            "kup_autorskie_pct": 50.0,
            "ppk_participation": "opt_out",
            "ppk_ee_rate": 0.0,
            "ppk_additional": 0.0,
            "pit2_filed": False,
            "ulga_type": "none",
            "zus_code": "0411",
        },
    },
    {
        "scenario_no": 10,
        "employee": {
            "name": "Andrzej Dabrowski",
            "birthday": "1984-12-01",
            "gender": "male",
            "country_xmlid": "base.pl",
            "street": "ul. Polna 60",
            "city": "Lublin",
            "zip": "20-400",
        },
        "contract": {
            "name": "Scenario 10 - Prog 32 proc.",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 30000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
            "prior_tax_base": 110000.0,
        },
    },
    {
        "scenario_no": 11,
        "employee": {
            "name": "Ewa Majewska",
            "birthday": "1994-03-12",
            "gender": "female",
            "country_xmlid": "base.pl",
            "street": "ul. Jasna 9/5",
            "city": "Bialystok",
            "zip": "15-001",
        },
        "contract": {
            "name": "Scenario 11 - PPK reduced",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 9000.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "standard",
            "kup_autorskie_pct": 0.0,
            "ppk_participation": "reduced",
            "ppk_ee_rate": 0.5,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        },
    },
    {
        "scenario_no": 12,
        "employee": {
            "name": "Olena Bondarenko",
            "birthday": "1991-10-27",
            "gender": "female",
            "country_xmlid": "base.ua",
            "street": "ul. Wislana 18/9",
            "city": "Rzeszow",
            "zip": "35-001",
        },
        "contract": {
            "name": "Scenario 12 - Na powrot z autorskimi",
            "contract_type_xmlid": "l10n_pl_payroll_demo_contract_type_uop",
            "wage": 7500.0,
            "date_start": "2026-01-01",
            "resource_calendar_xmlid": "resource.resource_calendar_std",
            "kup_type": "autorskie",
            "kup_autorskie_pct": 80.0,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "na_powrot",
            "zus_code": "0110",
        },
    },
]


def invalid_pesel(birth_date, gender, sequence):
    month = birth_date.month
    if 1800 <= birth_date.year <= 1899:
        month += 80
    elif 2000 <= birth_date.year <= 2099:
        month += 20
    elif 2100 <= birth_date.year <= 2199:
        month += 40
    elif 2200 <= birth_date.year <= 2299:
        month += 60

    base = f"{birth_date.year % 100:02d}{month:02d}{birth_date.day:02d}"
    seq = sequence * 10 + (0 if gender == "male" else 1)
    serial = f"1{seq:03d}"
    digits = [int(char) for char in base + serial]
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = (10 - sum(digit * weight for digit, weight in zip(digits, weights)) % 10) % 10
    invalid_checksum = (checksum + 1) % 10
    return base + serial + str(invalid_checksum)


def validate_pesel_checksum(pesel):
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = (10 - sum(int(digit) * weight for digit, weight in zip(pesel[:10], weights)) % 10) % 10
    return checksum == int(pesel[-1])


def build_scenarios():
    scenarios = []
    for index, blueprint in enumerate(SCENARIO_BLUEPRINTS, start=1):
        scenario = deepcopy(blueprint)
        birthday = date.fromisoformat(scenario["employee"]["birthday"])
        scenario["employee"]["pesel"] = invalid_pesel(
            birthday,
            scenario["employee"]["gender"],
            index,
        )
        scenario["employee"]["pesel_checksum_valid"] = validate_pesel_checksum(
            scenario["employee"]["pesel"]
        )
        scenario["company"] = deepcopy(FICTIONAL_COMPANY)
        scenarios.append(scenario)
    return scenarios


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = build_scenarios()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    for scenario in payload:
        print(
            f"{scenario['scenario_no']:02d}. "
            f"{scenario['employee']['name']} | "
            f"{scenario['contract']['name']} | "
            f"PESEL {scenario['employee']['pesel']}"
        )


if __name__ == "__main__":
    main()
