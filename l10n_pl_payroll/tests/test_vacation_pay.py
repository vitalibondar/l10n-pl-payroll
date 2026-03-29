from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestVacationPay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.full_time_calendar = cls._make_calendar("Vacation Full Time", 16.0)
        cls.half_time_calendar = cls._make_calendar("Vacation Half Time", 12.0)
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

    def test_fixed_salary_no_supplement(self):
        contract = self._make_contract(
            "Vacation Fixed Salary",
            Decimal("6000.00"),
            resource_calendar=self.full_time_calendar,
        )
        self._make_confirmed_payslip(contract, 2025, 1)
        self._make_confirmed_payslip(contract, 2025, 2)
        self._make_confirmed_payslip(contract, 2025, 3)

        payslip = self._create_payslip(contract, 2025, 4, vacation_days=3.0)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.vacation_pay, Decimal("0.00"))
        self.assertDecimalEqual(payslip.gross, Decimal("6000.00"))

    def test_variable_supplement_calculated(self):
        contract = self._make_contract(
            "Vacation Variable Half Time",
            Decimal("5000.00"),
            resource_calendar=self.half_time_calendar,
        )
        history = self.env["pl.payroll.payslip"]
        history |= self._make_confirmed_payslip(
            contract,
            2025,
            1,
            overtime_hours_150=10.0,
            payslip_lines=[{"name": "Premia styczeń", "category": "bonus_gross", "amount": 400.0}],
        )
        history |= self._make_confirmed_payslip(
            contract,
            2025,
            2,
            overtime_hours_200=5.0,
            payslip_lines=[{"name": "Premia luty", "category": "bonus_gross", "amount": 300.0}],
        )
        history |= self._make_confirmed_payslip(
            contract,
            2025,
            3,
            payslip_lines=[{"name": "Premia marzec", "category": "bonus_gross", "amount": 500.0}],
        )

        payslip = self._create_payslip(contract, 2025, 4, vacation_days=2.0)
        payslip.compute_payslip()

        standard_hours = payslip._get_parameter("STANDARD_MONTHLY_HOURS")
        total_variable = sum(
            (
                Decimal(str(item.overtime_amount))
                + Decimal(str(item.bonus_gross_total))
                for item in history
            ),
            Decimal("0.00"),
        )
        total_hours = sum(
            (standard_hours * item._get_etat_fraction() for item in history),
            Decimal("0.00"),
        )
        vacation_hours = Decimal("2.0") * Decimal("8.00") * payslip._get_etat_fraction()
        expected = payslip._round_amount(total_variable / total_hours * vacation_hours)

        self.assertGreater(float(payslip.vacation_pay), 0.0)
        self.assertDecimalEqual(payslip.vacation_pay, expected)
        self.assertDecimalEqual(payslip.gross, Decimal("5000.00") + expected)

    def test_zero_vacation_days_no_effect(self):
        contract = self._make_contract(
            "Vacation Zero Days",
            Decimal("6200.00"),
            resource_calendar=self.full_time_calendar,
        )
        self._make_confirmed_payslip(
            contract,
            2025,
            1,
            payslip_lines=[{"name": "Premia styczeń", "category": "bonus_gross", "amount": 700.0}],
        )

        payslip = self._create_payslip(contract, 2025, 2, vacation_days=0.0)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.vacation_pay, Decimal("0.00"))
        self.assertDecimalEqual(payslip.gross, Decimal("6200.00"))

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
                "date_start": date(2025, 1, 1),
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

    def _create_payslip(self, contract, year, month, vacation_days=0.0, overtime_hours_150=0.0, overtime_hours_200=0.0, payslip_lines=None):
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": date(year, month, 1),
                "date_to": date(year, month, monthrange(year, month)[1]),
                "vacation_days": vacation_days,
                "overtime_hours_150": overtime_hours_150,
                "overtime_hours_200": overtime_hours_200,
                "payslip_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": line["name"],
                            "category": line["category"],
                            "amount": line["amount"],
                        },
                    )
                    for line in (payslip_lines or [])
                ],
            }
        )

    def _make_confirmed_payslip(self, contract, year, month, vacation_days=0.0, overtime_hours_150=0.0, overtime_hours_200=0.0, payslip_lines=None):
        payslip = self._create_payslip(
            contract,
            year,
            month,
            vacation_days=vacation_days,
            overtime_hours_150=overtime_hours_150,
            overtime_hours_200=overtime_hours_200,
            payslip_lines=payslip_lines,
        )
        payslip.action_confirm()
        return payslip

    def round_amount(self, value):
        return Decimal(str(value or 0.0)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
