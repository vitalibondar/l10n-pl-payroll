from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestStudentExemption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Calendar = cls.env["resource.calendar"]
        cls.CalendarAttendance = cls.env["resource.calendar.attendance"]
        cls.calendar = cls._make_calendar("Test Student Exemption Full Time", 16.0)
        cls.contract_type_praca = cls.env.ref("l10n_pl_payroll.contract_type_umowa_o_prace")
        cls.contract_type_zlecenie = cls.env.ref("l10n_pl_payroll.contract_type_umowa_zlecenie")

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

    def test_student_zlecenie_no_zus(self):
        employee = self._make_employee("Student Zlecenie", "2004-06-15", is_student=True)
        contract = self._make_contract(
            employee,
            "Student zlecenie",
            Decimal("5000.00"),
            self.contract_type_zlecenie,
        )

        payslip = self._create_payslip(contract, 2026, 1)
        payslip.compute_payslip()

        self.assertDecimalEqual(payslip.zus_emerytalne_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_rentowe_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_chorobowe_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_total_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.health, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_emerytalne_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_rentowe_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_wypadkowe_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_fp, Decimal("0.00"))
        self.assertDecimalEqual(payslip.zus_fgsp, Decimal("0.00"))
        self.assertDecimalEqual(payslip.ppk_ee, Decimal("0.00"))
        self.assertDecimalEqual(payslip.ppk_er, Decimal("0.00"))
        self.assertDecimalEqual(payslip.health_basis, Decimal("5000.00"))
        self.assertDecimalEqual(payslip.net, self.to_decimal(payslip.gross) - self.to_decimal(payslip.pit_due))

    def test_student_praca_normal_zus(self):
        employee = self._make_employee("Student Praca", "2004-06-15", is_student=True)
        contract = self._make_contract(
            employee,
            "Student praca",
            Decimal("5000.00"),
            self.contract_type_praca,
            ppk_participation="opt_out",
        )

        payslip = self._create_payslip(contract, 2026, 1)
        payslip.compute_payslip()

        self.assertGreater(payslip.zus_total_ee, 0.0)
        self.assertGreater(payslip.health, 0.0)
        self.assertGreater(payslip.zus_emerytalne_er, 0.0)
        self.assertGreater(payslip.total_employer_cost, payslip.gross)

    def test_non_student_zlecenie_normal_zus(self):
        employee = self._make_employee("Non Student Zlecenie", "2004-06-15", is_student=False)
        contract = self._make_contract(
            employee,
            "Non student zlecenie",
            Decimal("5000.00"),
            self.contract_type_zlecenie,
            ppk_participation="opt_out",
        )

        payslip = self._create_payslip(contract, 2026, 1)
        payslip.compute_payslip()

        self.assertGreater(payslip.zus_total_ee, 0.0)
        self.assertGreater(payslip.health, 0.0)
        self.assertGreater(payslip.zus_emerytalne_er, 0.0)
        self.assertGreater(payslip.total_employer_cost, payslip.gross)

    def test_student_turns_26_mid_year(self):
        employee = self._make_employee("Student 26", "2000-07-01", is_student=True)
        contract = self._make_contract(
            employee,
            "Student birthday threshold",
            Decimal("5000.00"),
            self.contract_type_zlecenie,
            ppk_participation="opt_out",
        )

        june = self._create_payslip(contract, 2026, 6)
        june.compute_payslip()

        july = self._create_payslip(contract, 2026, 7)
        july.compute_payslip()

        self.assertDecimalEqual(june.zus_total_ee, Decimal("0.00"))
        self.assertDecimalEqual(june.health, Decimal("0.00"))
        self.assertGreater(july.zus_total_ee, 0.0)
        self.assertGreater(july.health, 0.0)

    def _make_employee(self, name, birthday, is_student):
        return self.Employee.create(
            {
                "name": name,
                "ssnid": "99123112345",
                "birthday": birthday,
                "gender": "male",
                "country_id": self.env.ref("base.pl").id,
                "is_student": is_student,
            }
        )

    def _make_contract(
        self,
        employee,
        name,
        wage,
        contract_type,
        ppk_participation="default",
    ):
        ppk_ee_rate = 0.0 if ppk_participation == "opt_out" else 2.0
        return self.Contract.create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.env.company.id,
                "date_start": date(2026, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": self.calendar.id,
                "contract_type_id": contract_type.id,
                "kup_type": "standard",
                "kup_autorskie_pct": 0.0,
                "ppk_participation": ppk_participation,
                "ppk_ee_rate": ppk_ee_rate,
                "ppk_additional": 0.0,
                "pit2_filed": True,
                "ulga_type": "none",
                "zus_code": "0110",
            }
        )

    def _create_payslip(self, contract, year, month):
        date_from = date(year, month, 1)
        date_to = date(year, month, monthrange(year, month)[1])
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": date_from,
                "date_to": date_to,
            }
        )

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
