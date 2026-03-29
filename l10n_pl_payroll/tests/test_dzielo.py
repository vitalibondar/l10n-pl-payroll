from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestDzielo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.calendar = cls._make_calendar("Test Dzielo Full Time", 16.0)
        cls.contract_type_dzielo = cls.env.ref("l10n_pl_payroll.contract_type_umowa_o_dzielo")

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

    def test_dzielo_no_zus(self):
        contract = self._make_contract("Dzielo No ZUS", Decimal("3000.00"))

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.zus_total_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_emerytalne_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_rentowe_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_wypadkowe_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_fp, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_fgsp, Decimal("0.00"))
        self.assertDecimalEqual(payslip.health_basis, Decimal("0.00"))
        self.assertDecimalEqual(payslip.health, Decimal("0.00"))
        self.assertDecimalEqual(payslip.total_employer_cost, Decimal("3000.00"))

    def test_dzielo_kup_20(self):
        contract = self._make_contract("Dzielo KUP 20", Decimal("3000.00"), kup_type="standard")

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.kup_amount, Decimal("600.00"))

    def test_dzielo_kup_50_autorskie(self):
        contract = self._make_contract(
            "Dzielo KUP 50",
            Decimal("3000.00"),
            kup_type="autorskie",
            kup_autorskie_pct=50.0,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.kup_amount, Decimal("1500.00"))

    def test_dzielo_flat_pit(self):
        contract = self._make_contract("Dzielo PIT", Decimal("3000.00"), kup_type="standard")

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.taxable_income, Decimal("2400.00"))
        self.assertDecimalEqual(payslip.pit_advance, Decimal("288.00"))
        self.assertDecimalEqual(payslip.pit_reducing, Decimal("0.00"))
        self.assertDecimalEqual(payslip.pit_due, Decimal("288.00"))

    def test_dzielo_no_ppk(self):
        contract = self._make_contract("Dzielo PPK", Decimal("3000.00"), ppk_participation="default")

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.ppk_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.ppk_er, Decimal("0.00"))

    def test_dzielo_below_200(self):
        contract = self._make_contract("Dzielo 200", Decimal("200.00"), kup_type="autorskie", kup_autorskie_pct=50.0)

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.kup_amount, Decimal("0.00"))
        self.assertDecimalEqual(payslip.taxable_income, Decimal("200.00"))
        self.assertDecimalEqual(payslip.pit_due, Decimal("24.00"))

    def test_dzielo_net(self):
        contract = self._make_contract(
            "Dzielo Net",
            Decimal("3000.00"),
            kup_type="autorskie",
            kup_autorskie_pct=50.0,
        )

        payslip = self._create_payslip(contract)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.net, Decimal("2820.00"))
        self.assertDecimalEqual(
            payslip.net,
            self.to_decimal(payslip.gross) - self.to_decimal(payslip.pit_due),
        )

    def _make_employee(self, name):
        return self.Employee.create(
            {
                "name": name,
                "ssnid": "99123112345",
                "birthday": "1990-01-01",
                "gender": "male",
                "country_id": self.env.ref("base.pl").id,
            }
        )

    def _make_contract(
        self,
        name,
        wage,
        kup_type="standard",
        kup_autorskie_pct=0.0,
        ppk_participation="default",
    ):
        employee = self._make_employee(name)
        return self.Contract.create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.env.company.id,
                "date_start": date(2026, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": self.calendar.id,
                "contract_type_id": self.contract_type_dzielo.id,
                "kup_type": kup_type,
                "kup_autorskie_pct": kup_autorskie_pct,
                "ppk_participation": ppk_participation,
                "ppk_ee_rate": 2.0,
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

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
