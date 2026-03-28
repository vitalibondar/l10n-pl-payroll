# ⚠️ FICTIONAL TEST DATA — nie są to dane prawdziwych osób.
# Generated for testing purposes only. PESEL numbers have invalid checksums.

import json
from datetime import date


SCENARIO_PEOPLE = [
    {"name": "Jan Kowalski", "gender": "male", "birthday": "1988-04-15"},
    {"name": "Anna Nowak", "gender": "female", "birthday": "1990-11-03"},
    {"name": "Piotr Wiśniewski", "gender": "male", "birthday": "1985-02-22"},
    {"name": "Maria Wójcik", "gender": "female", "birthday": "1997-07-09"},
    {"name": "Jakub Kamiński", "gender": "male", "birthday": "1993-01-19"},
    {"name": "Oleg Shevchenko", "gender": "male", "birthday": "2002-05-12"},
    {"name": "Katarzyna Lewandowska", "gender": "female", "birthday": "1987-09-27"},
    {"name": "Tomasz Zieliński", "gender": "male", "birthday": "1991-06-14"},
    {"name": "Natalia Kravchuk", "gender": "female", "birthday": "1995-08-30"},
    {"name": "Andrzej Dąbrowski", "gender": "male", "birthday": "1983-12-05"},
    {"name": "Ewa Majewska", "gender": "female", "birthday": "1994-03-18"},
    {"name": "Olena Bondarenko", "gender": "female", "birthday": "1989-10-21"},
]

ADDRESSES = [
    {"street": "ul. Jasna 12/4", "zip": "00-041", "city": "Warszawa", "country_code": "PL"},
    {"street": "ul. Modrzewiowa 7/9", "zip": "30-221", "city": "Kraków", "country_code": "PL"},
    {"street": "ul. Słoneczna 18", "zip": "80-244", "city": "Gdańsk", "country_code": "PL"},
    {"street": "ul. Dniprovska 5", "zip": "50-201", "city": "Wrocław", "country_code": "PL"},
]
SERIALS = [1234, 2345, 3456, 4567, 5678, 6789, 7890, 8901, 9012, 1123, 2234, 3345]


def pesel_checksum(first_ten_digits):
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    total = sum(int(digit) * weight for digit, weight in zip(first_ten_digits, weights))
    return (10 - total % 10) % 10


def date_to_pesel_prefix(birthday):
    year = birthday.year % 100
    month = birthday.month
    if 1800 <= birthday.year <= 1899:
        month += 80
    elif 2000 <= birthday.year <= 2099:
        month += 20
    elif 2100 <= birthday.year <= 2199:
        month += 40
    elif 2200 <= birthday.year <= 2299:
        month += 60
    return f"{year:02d}{month:02d}{birthday.day:02d}"


def generate_invalid_pesel(birthday, serial):
    first_ten_digits = f"{date_to_pesel_prefix(birthday)}{serial:04d}"
    valid_checksum = pesel_checksum(first_ten_digits)
    invalid_checksum = (valid_checksum + 5) % 10
    if invalid_checksum == valid_checksum:
        invalid_checksum = (valid_checksum + 1) % 10
    return f"{first_ten_digits}{invalid_checksum}"


def validate_invalid_pesel(pesel):
    return len(pesel) == 11 and pesel_checksum(pesel[:10]) != int(pesel[-1])


def generate_invalid_nip(first_nine_digits="123456789"):
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    valid_checksum = sum(int(digit) * weight for digit, weight in zip(first_nine_digits, weights)) % 11
    invalid_checksum = (valid_checksum + 5) % 10
    if invalid_checksum == valid_checksum:
        invalid_checksum = (valid_checksum + 1) % 10
    return f"{first_nine_digits}{invalid_checksum}"


def generate_person(index):
    scenario = SCENARIO_PEOPLE[index]
    birthday = date.fromisoformat(scenario["birthday"])
    return {
        "name": scenario["name"],
        "gender": scenario["gender"],
        "birthday": scenario["birthday"],
        "pesel": generate_invalid_pesel(birthday, SERIALS[index]),
        "address": ADDRESSES[index % len(ADDRESSES)],
    }


def generate_batch():
    return {
        "company_nip": generate_invalid_nip(),
        "employees": [generate_person(index) for index in range(len(SCENARIO_PEOPLE))],
    }


def main():
    print(json.dumps(generate_batch(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
