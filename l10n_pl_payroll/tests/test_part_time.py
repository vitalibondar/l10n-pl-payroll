from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestPartTime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.Parameter = cls.env["pl.payroll.parameter"]
        cls.full_time_calendar = cls.env.ref("l10n_pl_payroll.demo_calendar_full_time")
        cls.half_time_calendar = cls.env.ref("l10n_pl_payroll.demo_calendar_half_time")
        cls.contract_type_praca = cls.env.ref("l10n_pl_payroll.demo_contract_type_umowa_o_prace")
        cls.env.company.resource_calendar_id = cls.full_time_calendar

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

    def test_half_time_kup_proportional(self):
        contract = self._make_contract(
            "Half Time Standard",
            Decimal("4806.00"),
            resource_calendar=self.half_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.etat_fraction, Decimal("0.50"))
        self.assertDecimalEqual(payslip.kup_amount, Decimal("125.00"))

    def test_full_time_kup_unchanged(self):
        contract = self._make_contract(
            "Full Time Standard",
            Decimal("4806.00"),
            resource_calendar=self.full_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.etat_fraction, Decimal("1.00"))
        self.assertDecimalEqual(payslip.kup_amount, Decimal("250.00"))

    def test_autorskie_kup_not_proportional(self):
        contract = self._make_contract(
            "Half Time Creative",
            Decimal("10000.00"),
            kup_type="autorskie",
            kup_autorskie_pct=50.0,
            resource_calendar=self.half_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        expected_kup = self.round_amount(self.to_decimal(payslip.health_basis) * Decimal("0.25"))
        self.assertDecimalEqual(payslip.etat_fraction, Decimal("0.50"))
        self.assertDecimalEqual(payslip.kup_amount, expected_kup)

    def test_below_minimum_wage_warning(self):
        contract = self._make_contract(
            "Below Minimum Half Time",
            Decimal("2000.00"),
            resource_calendar=self.half_time_calendar,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertEqual(self.to_decimal(self.Parameter.get_value("MINIMUM_WAGE", payslip.date_to)), Decimal("4806"))
        self.assertTrue(payslip.below_minimum_wage)
        self.assertDecimalEqual(payslip.etat_fraction, Decimal("0.50"))

    def test_no_calendar_defaults_full(self):
        contract = self._make_contract(
            "No Calendar Standard",
            Decimal("4806.00"),
            resource_calendar=False,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.etat_fraction, Decimal("1.00"))
        self.assertDecimalEqual(payslip.kup_amount, Decimal("250.00"))
        self.assertFalse(payslip.below_minimum_wage)

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

    def _make_contract(
        self,
        name,
        wage,
        kup_type="standard",
        kup_autorskie_pct=0.0,
        resource_calendar=None,
    ):
        employee = self._make_employee(name)
        values = {
            "name": name,
            "employee_id": employee.id,
            "company_id": self.env.company.id,
            "date_start": date(2026, 1, 1),
            "wage": float(wage),
            "contract_type_id": self.contract_type_praca.id,
            "kup_type": kup_type,
            "kup_autorskie_pct": kup_autorskie_pct,
            "ppk_participation": "default",
            "ppk_ee_rate": 2.0,
            "ppk_additional": 0.0,
            "pit2_filed": True,
            "ulga_type": "none",
            "zus_code": "0110",
        }
        if resource_calendar:
            values["resource_calendar_id"] = resource_calendar.id
        return self.Contract.create(values)

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

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
