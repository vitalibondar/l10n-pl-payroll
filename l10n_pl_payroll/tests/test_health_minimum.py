from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestHealthMinimum(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.full_time_calendar = cls._make_calendar("Test Health Minimum Full Time", 16.0)
        cls.half_time_calendar = cls._make_calendar("Test Health Minimum Half Time", 12.0)
        cls.contract_type_praca = cls.env.ref("l10n_pl_payroll.contract_type_umowa_o_prace")
        cls.env.company.write({"resource_calendar_id": cls.full_time_calendar.id})

    @classmethod
    def _make_calendar(cls, name, hour_to):
        calendar = cls.Calendar.create(
            {
                "name": name,
                "tz": "Europe/Warsaw",
                "company_id": cls.env.company.id,
            }
        )
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for dayofweek, weekday in enumerate(weekdays):
            cls.CalendarAttendance.create(
                {
                    "name": weekday,
                    "calendar_id": calendar.id,
                    "dayofweek": str(dayofweek),
                    "hour_from": 8.0,
                    "hour_to": hour_to,
                    "day_period": "morning",
                }
            )
        return calendar

    def test_health_basis_at_minimum(self):
        contract = self._make_contract(
            "Health Minimum Exact",
            Decimal("4806.00"),
            resource_calendar=self.full_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        expected_basis = payslip._get_minimum_health_basis()
        self.assertDecimalEqual(payslip.health_basis, expected_basis)

    def test_health_basis_below_minimum(self):
        contract = self._make_contract(
            "Health Minimum Below",
            Decimal("4000.00"),
            resource_calendar=self.full_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        actual_basis = self._expected_actual_health_basis(payslip, Decimal("4000.00"))
        minimum_basis = payslip._get_minimum_health_basis()

        self.assertLess(actual_basis, minimum_basis)
        self.assertDecimalEqual(payslip.health_basis, minimum_basis)
        self.assertDecimalEqual(
            payslip.taxable_income,
            payslip._floor_amount(actual_basis - Decimal("250.00")),
        )

    def test_health_basis_above_minimum(self):
        contract = self._make_contract(
            "Health Minimum Above",
            Decimal("6000.00"),
            resource_calendar=self.full_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        expected_basis = self._expected_actual_health_basis(payslip, Decimal("6000.00"))
        self.assertDecimalEqual(payslip.health_basis, expected_basis)

    def test_health_basis_part_time_minimum(self):
        contract = self._make_contract(
            "Health Minimum Half Time",
            Decimal("1500.00"),
            resource_calendar=self.half_time_calendar,
        )
        full_time_contract = self._make_contract(
            "Health Minimum Full Time Reference",
            Decimal("1500.00"),
            resource_calendar=self.full_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()
        full_time_payslip = self._create_payslip(full_time_contract)
        full_time_payslip.compute_payslip()

        actual_basis = self._expected_actual_health_basis(payslip, Decimal("1500.00"))
        minimum_basis = payslip._get_minimum_health_basis()
        full_time_minimum_basis = full_time_payslip._get_minimum_health_basis()

        self.assertLess(payslip.etat_fraction, 1.0)
        self.assertLess(actual_basis, minimum_basis)
        self.assertLess(minimum_basis, full_time_minimum_basis)
        self.assertDecimalEqual(payslip.health_basis, minimum_basis)

    def _make_employee(self, name):
        return self.Employee.create(
            {
                "name": name,
                "ssnid": "99123112345",
                "birthday": "1990-01-01",
                "gender": "female",
                "country_id": self.env.ref("base.pl").id,
            }
        )

    def _make_contract(self, name, wage, resource_calendar):
        employee = self._make_employee(name)
        return self.Contract.create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.env.company.id,
                "date_start": date(2026, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": resource_calendar.id,
                "contract_type_id": self.contract_type_praca.id,
                "kup_type": "standard",
                "kup_autorskie_pct": 0.0,
                "ppk_participation": "opt_out",
                "ppk_ee_rate": 0.0,
                "ppk_additional": 0.0,
                "pit2_filed": True,
                "ulga_type": "none",
                "zus_code": "0110",
            }
        )

    def _create_payslip(self, contract):
        target_date = date(2026, 1, 1)
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": target_date,
                "date_to": date(target_date.year, target_date.month, monthrange(target_date.year, target_date.month)[1]),
            }
        )

    def _expected_actual_health_basis(self, payslip, gross):
        gross = Decimal(str(gross))
        zus_total = (
            payslip._percent_of_amount(gross, "ZUS_EMERY_EE")
            + payslip._percent_of_amount(gross, "ZUS_RENT_EE")
            + payslip._percent_of_amount(gross, "ZUS_CHOR_EE")
        )
        return payslip._round_amount(gross - zus_total)

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
