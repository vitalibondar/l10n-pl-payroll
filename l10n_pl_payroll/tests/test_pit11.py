from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestPit11(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Pit11 = cls.env["pl.payroll.pit11"]
        cls.Wizard = cls.env["pl.payroll.pit11.wizard"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.contract_type_praca = cls.env.ref("l10n_pl_payroll.contract_type_umowa_o_prace")
        cls.full_time_calendar = cls._make_calendar("Test PIT11 Full Time")
        cls.env.company.write({"resource_calendar_id": cls.full_time_calendar.id})

    @classmethod
    def _make_calendar(cls, name):
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
                    "hour_to": 16.0,
                    "day_period": "morning",
                }
            )
        return calendar

    def test_pit11_generation(self):
        employee_one = self._make_employee("PIT11 Employee One", "91010112345")
        employee_two = self._make_employee("PIT11 Employee Two", "92020212345")
        contract_one = self._make_contract("PIT11 Contract One", employee_one, Decimal("8000.00"))
        contract_two = self._make_contract("PIT11 Contract Two", employee_two, Decimal("6200.00"), ppk_participation="opt_out")

        slips_one = self.env["pl.payroll.payslip"]
        slips_one |= self._make_confirmed_payslip(contract_one, 2025, 1)
        slips_one |= self._make_confirmed_payslip(contract_one, 2025, 2)
        self._make_confirmed_payslip(contract_one, 2026, 1)
        slips_two = self._make_confirmed_payslip(contract_two, 2025, 1)

        action = self.Wizard.create({"year": 2025}).action_generate()
        records = self.Pit11.search(
            [
                ("year", "=", 2025),
                ("employee_id", "in", [employee_one.id, employee_two.id]),
            ]
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(action["res_model"], "pl.payroll.pit11")

        pit11_one = records.filtered(lambda record: record.employee_id == employee_one)
        expected_one = self._expected_totals(slips_one)
        self.assertDecimalEqual(pit11_one.total_gross, expected_one["total_gross"])
        self.assertDecimalEqual(pit11_one.total_zus_ee, expected_one["total_zus_ee"])
        self.assertDecimalEqual(pit11_one.total_health, expected_one["total_health"])
        self.assertDecimalEqual(pit11_one.total_kup, expected_one["total_kup"])
        self.assertDecimalEqual(pit11_one.total_income, expected_one["total_income"])
        self.assertDecimalEqual(pit11_one.total_pit_paid, expected_one["total_pit_paid"])
        self.assertEqual(pit11_one.payslip_count, 2)

        pit11_two = records.filtered(lambda record: record.employee_id == employee_two)
        expected_two = self._expected_totals(slips_two)
        self.assertDecimalEqual(pit11_two.total_gross, expected_two["total_gross"])
        self.assertDecimalEqual(pit11_two.total_income, expected_two["total_income"])

    def test_pit11_health_deductible(self):
        employee = self._make_employee("PIT11 Health", "93030312345")
        contract = self._make_contract("PIT11 Health Contract", employee, Decimal("7000.00"))
        payslip = self._make_confirmed_payslip(contract, 2025, 3)

        self.Wizard.create({"year": 2025}).action_generate()
        pit11 = self.Pit11.search(
            [("employee_id", "=", employee.id), ("year", "=", 2025)],
            limit=1,
        )

        expected = payslip._round_amount(Decimal(str(payslip.health_basis)) * Decimal("0.0775"))
        self.assertDecimalEqual(pit11.health_deductible, expected)

    def test_pit11_regeneration(self):
        employee = self._make_employee("PIT11 Recompute", "94040412345")
        contract = self._make_contract("PIT11 Recompute Contract", employee, Decimal("7500.00"))

        self._make_confirmed_payslip(contract, 2025, 4)
        wizard = self.Wizard.create({"year": 2025})
        wizard.action_generate()

        first = self.Pit11.search(
            [("employee_id", "=", employee.id), ("year", "=", 2025)],
            limit=1,
        )
        self.assertEqual(first.payslip_count, 1)

        self._make_confirmed_payslip(contract, 2025, 5)
        wizard.action_generate()

        records = self.Pit11.search([("employee_id", "=", employee.id), ("year", "=", 2025)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records.id, first.id)
        self.assertEqual(records.payslip_count, 2)

    def test_pit11_ppk_er_included(self):
        employee = self._make_employee("PIT11 PPK", "95050512345")
        contract = self._make_contract("PIT11 PPK Contract", employee, Decimal("8100.00"))
        payslip = self._make_confirmed_payslip(contract, 2025, 6)

        self.Wizard.create({"year": 2025}).action_generate()
        pit11 = self.Pit11.search(
            [("employee_id", "=", employee.id), ("year", "=", 2025)],
            limit=1,
        )

        expected_total_gross = payslip._round_amount(
            payslip._get_effective_gross_amount() + Decimal(str(payslip.ppk_er))
        )
        self.assertGreater(payslip.ppk_er, 0.0)
        self.assertDecimalEqual(pit11.total_ppk_er, payslip.ppk_er)
        self.assertDecimalEqual(pit11.total_gross, expected_total_gross)

    def _make_employee(self, name, ssnid):
        return self.Employee.create(
            {
                "name": name,
                "ssnid": ssnid,
                "birthday": "1990-01-01",
                "gender": "female",
                "country_id": self.env.ref("base.pl").id,
            }
        )

    def _make_contract(self, name, employee, wage, ppk_participation="default"):
        return self.Contract.create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.env.company.id,
                "date_start": date(2025, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": self.full_time_calendar.id,
                "contract_type_id": self.contract_type_praca.id,
                "kup_type": "standard",
                "kup_autorskie_pct": 0.0,
                "ppk_participation": ppk_participation,
                "ppk_ee_rate": 2.0,
                "ppk_additional": 0.0,
                "pit2_filed": True,
                "ulga_type": "none",
                "zus_code": "0110",
            }
        )

    def _make_confirmed_payslip(self, contract, year, month):
        payslip = self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": date(year, month, 1),
                "date_to": date(year, month, monthrange(year, month)[1]),
            }
        )
        payslip.action_confirm()
        return payslip

    def _expected_totals(self, payslips):
        return {
            "total_gross": self.round_amount(
                sum(
                    (
                        payslip._get_effective_gross_amount() + Decimal(str(payslip.ppk_er))
                        for payslip in payslips
                    ),
                    Decimal("0.00"),
                )
            ),
            "total_zus_ee": self.round_amount(
                sum((Decimal(str(payslip.zus_total_ee)) for payslip in payslips), Decimal("0.00"))
            ),
            "total_health": self.round_amount(
                sum((Decimal(str(payslip.health)) for payslip in payslips), Decimal("0.00"))
            ),
            "total_kup": self.round_amount(
                sum((Decimal(str(payslip.kup_amount)) for payslip in payslips), Decimal("0.00"))
            ),
            "total_income": self.round_amount(
                sum((Decimal(str(payslip.taxable_income)) for payslip in payslips), Decimal("0.00"))
            ),
            "total_pit_paid": self.round_amount(
                sum((Decimal(str(payslip.pit_due)) for payslip in payslips), Decimal("0.00"))
            ),
        }

    def round_amount(self, value):
        return Decimal(str(value or 0.0)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
