from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")
WHOLE_ZLOTY = Decimal("1")


@tagged("post_install", "-at_install")
class TestSickLeave(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.ContractType = cls.env["hr.contract.type"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Parameter = cls.env["pl.payroll.parameter"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.calendar = cls._make_calendar("Sick Leave Full Time", 16.0)
        cls.contract_type_praca = cls.ContractType.search([("name", "=", "Umowa o pracę")], limit=1)
        if not cls.contract_type_praca:
            cls.contract_type_praca = cls.ContractType.create({"name": "Umowa o pracę"})
        cls.env.company.resource_calendar_id = cls.calendar

    def test_sick_leave_80_percent(self):
        contract = self._make_contract("Sick 80", Decimal("5000.00"))
        self._seed_history(contract, [Decimal("5000.00")] * 12)

        payslip = self._create_payslip(contract, 2026, 1, sick_days=5, working_days_in_month=20)
        payslip.compute_payslip()

        expected_basis = Decimal("4314.50")
        expected_amount = self.round_amount(expected_basis / Decimal("30") * Decimal("5") * Decimal("0.80"))

        self.assertDecimalEqual(payslip.sick_leave_basis, expected_basis)
        self.assertDecimalEqual(payslip.sick_leave_amount, expected_amount)
        self.assertEqual(payslip.ytd_sick_days, 5)

    def test_sick_leave_100_percent(self):
        contract = self._make_contract("Sick 100", Decimal("5000.00"))
        self._seed_history(contract, [Decimal("5000.00")] * 12)

        payslip = self._create_payslip(contract, 2026, 1, sick_days_100=3, working_days_in_month=20)
        payslip.compute_payslip()

        expected_basis = Decimal("4314.50")
        expected_amount = self.round_amount(expected_basis / Decimal("30") * Decimal("3"))

        self.assertDecimalEqual(payslip.sick_leave_basis, expected_basis)
        self.assertDecimalEqual(payslip.sick_leave_amount, expected_amount)
        self.assertEqual(payslip.ytd_sick_days, 3)

    def test_sick_leave_no_zus_on_sick_portion(self):
        contract = self._make_contract("Sick No ZUS", Decimal("6000.00"))
        self._seed_history(contract, [Decimal("6000.00")] * 12)

        payslip = self._create_payslip(contract, 2026, 1, sick_days=6, working_days_in_month=20)
        payslip.compute_payslip()

        adjusted_gross = Decimal("4200.00")
        expected_zus_total = self.round_amount(
            self.percent_of(adjusted_gross, "ZUS_EMERY_EE", payslip.date_to)
            + self.percent_of(adjusted_gross, "ZUS_RENT_EE", payslip.date_to)
            + self.percent_of(adjusted_gross, "ZUS_CHOR_EE", payslip.date_to)
        )

        self.assertDecimalEqual(payslip.zus_total_ee, expected_zus_total)

    def test_sick_leave_health_includes_sick(self):
        contract = self._make_contract("Sick Health", Decimal("5400.00"))
        self._seed_history(contract, [Decimal("5400.00")] * 12)

        payslip = self._create_payslip(contract, 2026, 1, sick_days=4, working_days_in_month=20)
        payslip.compute_payslip()

        adjusted_gross = Decimal("4320.00")
        zus_total = self.round_amount(
            self.percent_of(adjusted_gross, "ZUS_EMERY_EE", payslip.date_to)
            + self.percent_of(adjusted_gross, "ZUS_RENT_EE", payslip.date_to)
            + self.percent_of(adjusted_gross, "ZUS_CHOR_EE", payslip.date_to)
        )
        basis = Decimal("4659.66")
        sick_amount = self.round_amount(basis / Decimal("30") * Decimal("4") * Decimal("0.80"))
        expected_health_basis = self.round_amount(adjusted_gross - zus_total + sick_amount)
        expected_health = self.round_amount(
            expected_health_basis * self.get_parameter("HEALTH", payslip.date_to) / Decimal("100")
        )

        self.assertDecimalEqual(payslip.sick_leave_amount, sick_amount)
        self.assertDecimalEqual(payslip.health_basis, expected_health_basis)
        self.assertDecimalEqual(payslip.health, expected_health)

    def test_sick_leave_basis_from_history(self):
        contract = self._make_contract("Sick Basis", Decimal("7000.00"))
        history_grosses = [
            Decimal("4000.00"),
            Decimal("4200.00"),
            Decimal("4400.00"),
            Decimal("4600.00"),
            Decimal("4800.00"),
            Decimal("5000.00"),
            Decimal("5200.00"),
            Decimal("5400.00"),
            Decimal("5600.00"),
            Decimal("5800.00"),
            Decimal("6000.00"),
            Decimal("6200.00"),
        ]
        self._seed_history(contract, history_grosses)

        payslip = self._create_payslip(contract, 2026, 1, sick_days=1, working_days_in_month=20)

        expected_basis = self.round_amount(
            sum((gross - self.employee_zus_total(gross, payslip.date_to) for gross in history_grosses), Decimal("0.00"))
            / Decimal("12")
        )

        self.assertDecimalEqual(payslip._compute_sick_leave_basis(), expected_basis)

    def test_no_sick_days_unchanged(self):
        contract = self._make_contract("No Sick", Decimal("5000.00"))
        payslip = self._create_payslip(contract, 2026, 1)

        payslip.compute_payslip()

        gross = Decimal("5000.00")
        zus_total = self.employee_zus_total(gross, payslip.date_to)
        health_basis = self.round_amount(gross - zus_total)
        health = self.round_amount(health_basis * self.get_parameter("HEALTH", payslip.date_to) / Decimal("100"))
        kup_amount = self.get_parameter("KUP_STANDARD", payslip.date_to)
        taxable_income = self.floor_amount(health_basis - kup_amount)
        pit_advance = self.round_amount(
            taxable_income * self.get_parameter("PIT_RATE_1", payslip.date_to) / Decimal("100")
        )
        pit_reducing = self.round_amount(self.get_parameter("PIT_REDUCING", payslip.date_to))
        pit_due = self.floor_amount(max(Decimal("0.00"), pit_advance - pit_reducing))
        expected_net = self.round_amount(gross - zus_total - health - pit_due)

        self.assertDecimalEqual(payslip.sick_leave_basis, Decimal("0.00"))
        self.assertDecimalEqual(payslip.sick_leave_amount, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_total_ee, zus_total)
        self.assertDecimalEqual(payslip.health_basis, health_basis)
        self.assertDecimalEqual(payslip.net, expected_net)

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

    def _make_contract(self, name, wage):
        employee = self._make_employee(name)
        return self.Contract.create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.env.company.id,
                "date_start": date(2025, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": self.calendar.id,
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

    def _seed_history(self, contract, gross_values):
        for month, gross in enumerate(gross_values, start=1):
            date_from = date(2025, month, 1)
            date_to = date(2025, month, monthrange(2025, month)[1])
            self.Payslip.create(
                {
                    "employee_id": contract.employee_id.id,
                    "contract_id": contract.id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "gross": float(gross),
                    "zus_total_ee": float(self.employee_zus_total(gross, date_to)),
                    "state": "confirmed",
                }
            )

    def _create_payslip(
        self,
        contract,
        year,
        month,
        sick_days=0,
        sick_days_100=0,
        working_days_in_month=0,
    ):
        date_from = date(year, month, 1)
        date_to = date(year, month, monthrange(year, month)[1])
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": date_from,
                "date_to": date_to,
                "sick_days": sick_days,
                "sick_days_100": sick_days_100,
                "working_days_in_month": working_days_in_month,
            }
        )

    def employee_zus_total(self, gross, target_date):
        return self.round_amount(
            self.percent_of(gross, "ZUS_EMERY_EE", target_date)
            + self.percent_of(gross, "ZUS_RENT_EE", target_date)
            + self.percent_of(gross, "ZUS_CHOR_EE", target_date)
        )

    def percent_of(self, amount, code, target_date):
        return self.round_amount(amount * self.get_parameter(code, target_date) / Decimal("100"))

    def get_parameter(self, code, target_date):
        return Decimal(str(self.Parameter.get_value(code, target_date) or 0.0))

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def floor_amount(self, value):
        return self.to_decimal(value).quantize(WHOLE_ZLOTY, rounding=ROUND_DOWN)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
