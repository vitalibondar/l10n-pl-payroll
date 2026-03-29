from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestZusDra(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract_type_praca = cls.env.ref("l10n_pl_payroll.contract_type_umowa_o_prace")
        cls.contract_type_zlecenie = cls.env.ref("l10n_pl_payroll.contract_type_umowa_zlecenie")
        cls.test_company = cls.env["res.company"].create(
            {
                "name": "Test ZUS DRA Company",
                "currency_id": cls.env.company.currency_id.id,
                "country_id": cls.env.ref("base.pl").id,
            }
        )
        cls.full_time_calendar = cls._make_calendar("Test ZUS DRA Calendar")
        cls.test_company.write({"resource_calendar_id": cls.full_time_calendar.id})

    @classmethod
    def _make_calendar(cls, name):
        calendar = cls.env["resource.calendar"].create(
            {
                "name": name,
                "tz": "Europe/Warsaw",
                "company_id": cls.test_company.id,
            }
        )
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for dayofweek, weekday in enumerate(weekdays):
            cls.env["resource.calendar.attendance"].create(
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

    def test_dra_totals_match_payslips(self):
        employee_one = self._make_employee("DRA Standard One", "96010112345")
        employee_two = self._make_employee("DRA Standard Two", "97020212345")
        contract_one = self._make_contract("DRA Contract One", employee_one, Decimal("7600.00"))
        contract_two = self._make_contract("DRA Contract Two", employee_two, Decimal("6400.00"))

        payslips = self._model("pl.payroll.payslip")
        payslips |= self._make_confirmed_payslip(contract_one, 2026, 7)
        payslips |= self._make_confirmed_payslip(contract_two, 2026, 7)

        self._model("pl.payroll.zus.dra.wizard").create({"year": 2026, "month": 7}).action_generate()
        dra = self._model("pl.payroll.zus.dra").search(
            [
                ("company_id", "=", self.test_company.id),
                ("year", "=", 2026),
                ("month", "=", 7),
            ],
            limit=1,
        )

        self.assertDecimalEqual(dra.total_emerytalne_ee, self._sum_field(payslips, "zus_emerytalne_ee"))
        self.assertDecimalEqual(dra.total_emerytalne_er, self._sum_field(payslips, "zus_emerytalne_er"))
        self.assertDecimalEqual(dra.total_rentowe_ee, self._sum_field(payslips, "zus_rentowe_ee"))
        self.assertDecimalEqual(dra.total_rentowe_er, self._sum_field(payslips, "zus_rentowe_er"))
        self.assertDecimalEqual(dra.total_chorobowe, self._sum_field(payslips, "zus_chorobowe_ee"))
        self.assertDecimalEqual(dra.total_wypadkowe, self._sum_field(payslips, "zus_wypadkowe_er"))
        self.assertDecimalEqual(dra.total_health, self._sum_field(payslips, "health"))
        self.assertDecimalEqual(dra.total_fp, self._sum_field(payslips, "zus_fp"))
        self.assertDecimalEqual(dra.total_fgsp, self._sum_field(payslips, "zus_fgsp"))
        self.assertDecimalEqual(dra.total_all, dra.total_zus_employee + dra.total_zus_employer)

    def test_dra_employee_count(self):
        employee_one = self._make_employee("DRA Count One", "98030312345")
        employee_two = self._make_employee("DRA Count Two", "99040412345")
        contract_one = self._make_contract("DRA Count Contract One", employee_one, Decimal("7100.00"))
        contract_two = self._make_contract("DRA Count Contract Two", employee_two, Decimal("6800.00"))

        self._make_confirmed_payslip(contract_one, 2026, 8)
        self._make_confirmed_payslip(contract_two, 2026, 8)

        self._model("pl.payroll.zus.dra.wizard").create({"year": 2026, "month": 8}).action_generate()
        dra = self._model("pl.payroll.zus.dra").search(
            [
                ("company_id", "=", self.test_company.id),
                ("year", "=", 2026),
                ("month", "=", 8),
            ],
            limit=1,
        )

        self.assertEqual(dra.employee_count, 2)
        self.assertEqual(dra.payslip_count, 2)

    def test_dra_regeneration(self):
        employee_one = self._make_employee("DRA Regen One", "00121212345")
        employee_two = self._make_employee("DRA Regen Two", "01010112345")
        contract_one = self._make_contract("DRA Regen Contract One", employee_one, Decimal("7200.00"))
        contract_two = self._make_contract("DRA Regen Contract Two", employee_two, Decimal("6900.00"))

        self._make_confirmed_payslip(contract_one, 2026, 9)
        wizard = self._model("pl.payroll.zus.dra.wizard").create({"year": 2026, "month": 9})
        wizard.action_generate()

        first = self._model("pl.payroll.zus.dra").search(
            [
                ("company_id", "=", self.test_company.id),
                ("year", "=", 2026),
                ("month", "=", 9),
            ],
            limit=1,
        )
        self.assertEqual(first.payslip_count, 1)
        self.assertEqual(len(first.line_ids), 1)

        self._make_confirmed_payslip(contract_two, 2026, 9)
        wizard.action_generate()

        records = self._model("pl.payroll.zus.dra").search(
            [
                ("company_id", "=", self.test_company.id),
                ("year", "=", 2026),
                ("month", "=", 9),
            ]
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records.id, first.id)
        self.assertEqual(records.payslip_count, 2)
        self.assertEqual(len(records.line_ids), 2)

    def test_dra_student_excluded(self):
        employee = self._make_employee("DRA Student", "02020212345", birthday="2005-01-01", is_student=True)
        contract = self._make_contract(
            "DRA Student Contract",
            employee,
            Decimal("4200.00"),
            contract_type=self.contract_type_zlecenie,
        )
        payslip = self._make_confirmed_payslip(contract, 2026, 10)

        self._model("pl.payroll.zus.dra.wizard").create({"year": 2026, "month": 10}).action_generate()
        dra = self._model("pl.payroll.zus.dra").search(
            [
                ("company_id", "=", self.test_company.id),
                ("year", "=", 2026),
                ("month", "=", 10),
            ],
            limit=1,
        )
        line = dra.line_ids.filtered(lambda item: item.employee_id == employee)

        self.assertEqual(len(line), 1)
        self.assertEqual(payslip.zus_total_ee, 0.0)
        self.assertDecimalEqual(line.emerytalne_ee, Decimal("0.00"))
        self.assertDecimalEqual(line.emerytalne_er, Decimal("0.00"))
        self.assertDecimalEqual(line.rentowe_ee, Decimal("0.00"))
        self.assertDecimalEqual(line.rentowe_er, Decimal("0.00"))
        self.assertDecimalEqual(line.chorobowe, Decimal("0.00"))
        self.assertDecimalEqual(line.wypadkowe, Decimal("0.00"))
        self.assertDecimalEqual(line.health, Decimal("0.00"))
        self.assertDecimalEqual(line.fp, Decimal("0.00"))
        self.assertDecimalEqual(line.fgsp, Decimal("0.00"))

    def _model(self, model_name):
        return self.env[model_name].with_context(allowed_company_ids=[self.test_company.id]).with_company(self.test_company)

    def _make_employee(self, name, ssnid, birthday="1990-01-01", is_student=False):
        return self._model("hr.employee").create(
            {
                "name": name,
                "company_id": self.test_company.id,
                "ssnid": ssnid,
                "birthday": birthday,
                "gender": "female",
                "country_id": self.env.ref("base.pl").id,
                "is_student": is_student,
            }
        )

    def _make_contract(self, name, employee, wage, contract_type=None):
        return self._model("hr.contract").create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.test_company.id,
                "date_start": date(2026, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": self.full_time_calendar.id,
                "contract_type_id": (contract_type or self.contract_type_praca).id,
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

    def _make_confirmed_payslip(self, contract, year, month):
        payslip = self._model("pl.payroll.payslip").create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": date(year, month, 1),
                "date_to": date(year, month, monthrange(year, month)[1]),
            }
        )
        payslip.action_confirm()
        return payslip

    def _sum_field(self, payslips, field_name):
        return self.round_amount(
            sum((Decimal(str(getattr(payslip, field_name) or 0.0)) for payslip in payslips), Decimal("0.00"))
        )

    def round_amount(self, value):
        return Decimal(str(value or 0.0)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
