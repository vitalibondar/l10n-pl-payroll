from calendar import monthrange
from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPayrollBatchWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract_type_praca = cls.env.ref("l10n_pl_payroll.contract_type_umowa_o_prace")
        cls.test_company = cls.env["res.company"].create(
            {
                "name": "Test Batch Wizard Company",
                "currency_id": cls.env.company.currency_id.id,
                "country_id": cls.env.ref("base.pl").id,
            }
        )
        cls.department_prod = cls.env["hr.department"].create({"name": "Batch Wizard Production"})
        cls.department_admin = cls.env["hr.department"].create({"name": "Batch Wizard Admin"})
        cls.calendar = cls._make_calendar("Batch Wizard Calendar")
        cls.test_company.write({"resource_calendar_id": cls.calendar.id})

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

    def test_batch_creates_payslips(self):
        employee_one = self._make_employee("Batch Create One", self.department_prod)
        employee_two = self._make_employee("Batch Create Two", self.department_admin)
        self._make_contract("Batch Create Contract One", employee_one)
        self._make_contract("Batch Create Contract Two", employee_two)

        wizard = self._make_wizard(date(2026, 1, 1), date(2026, 1, 31), auto_compute=False)
        action = wizard.action_generate()
        payslips = self._model("pl.payroll.payslip").search(
            [
                ("company_id", "=", self.test_company.id),
                ("date_from", "=", date(2026, 1, 1)),
                ("date_to", "=", date(2026, 1, 31)),
            ]
        )

        self.assertEqual(len(payslips), 2)
        self.assertEqual(set(payslips.mapped("state")), {"draft"})
        self.assertEqual(action["res_model"], "pl.payroll.payslip")

    def test_batch_skips_existing(self):
        employee_one = self._make_employee("Batch Skip One", self.department_prod)
        employee_two = self._make_employee("Batch Skip Two", self.department_prod)
        contract_one = self._make_contract("Batch Skip Contract One", employee_one)
        contract_two = self._make_contract("Batch Skip Contract Two", employee_two)
        self._model("pl.payroll.payslip").create(
            {
                "employee_id": contract_one.employee_id.id,
                "contract_id": contract_one.id,
                "date_from": date(2026, 2, 1),
                "date_to": date(2026, 2, 28),
            }
        )

        wizard = self._make_wizard(date(2026, 2, 1), date(2026, 2, 28), auto_compute=False)
        action = wizard.action_generate()
        created_ids = action["domain"][0][2]
        payslips = self._model("pl.payroll.payslip").search(
            [
                ("company_id", "=", self.test_company.id),
                ("date_from", "=", date(2026, 2, 1)),
            ]
        )

        self.assertEqual(len(created_ids), 1)
        self.assertEqual(len(payslips), 2)
        self.assertIn(contract_two.employee_id.id, payslips.mapped("employee_id").ids)

    def test_batch_department_filter(self):
        employee_one = self._make_employee("Batch Department One", self.department_prod)
        employee_two = self._make_employee("Batch Department Two", self.department_admin)
        self._make_contract("Batch Department Contract One", employee_one)
        self._make_contract("Batch Department Contract Two", employee_two)

        wizard = self._make_wizard(
            date(2026, 3, 1),
            date(2026, 3, 31),
            department_ids=[self.department_prod.id],
            auto_compute=False,
        )
        wizard.action_generate()
        payslips = self._model("pl.payroll.payslip").search(
            [
                ("company_id", "=", self.test_company.id),
                ("date_from", "=", date(2026, 3, 1)),
            ]
        )

        self.assertEqual(len(payslips), 1)
        self.assertEqual(payslips.employee_id, employee_one)

    def test_batch_auto_compute(self):
        employee = self._make_employee("Batch Auto Compute", self.department_prod)
        self._make_contract("Batch Auto Compute Contract", employee)

        wizard = self._make_wizard(date(2026, 4, 1), date(2026, 4, 30), auto_compute=True)
        wizard.action_generate()
        payslip = self._model("pl.payroll.payslip").search(
            [
                ("company_id", "=", self.test_company.id),
                ("date_from", "=", date(2026, 4, 1)),
            ],
            limit=1,
        )

        self.assertEqual(payslip.state, "computed")

    def test_batch_confirm_action(self):
        employee_one = self._make_employee("Batch Confirm One", self.department_prod)
        employee_two = self._make_employee("Batch Confirm Two", self.department_prod)
        contract_one = self._make_contract("Batch Confirm Contract One", employee_one)
        contract_two = self._make_contract("Batch Confirm Contract Two", employee_two)
        payslips = self._model("pl.payroll.payslip")
        payslip_one = payslips.create(
            {
                "employee_id": contract_one.employee_id.id,
                "contract_id": contract_one.id,
                "date_from": date(2026, 5, 1),
                "date_to": date(2026, 5, monthrange(2026, 5)[1]),
            }
        )
        payslip_two = payslips.create(
            {
                "employee_id": contract_two.employee_id.id,
                "contract_id": contract_two.id,
                "date_from": date(2026, 5, 1),
                "date_to": date(2026, 5, monthrange(2026, 5)[1]),
            }
        )

        self.env.ref("l10n_pl_payroll.action_server_pl_payroll_batch_confirm").with_context(
            allowed_company_ids=[self.test_company.id],
            active_model="pl.payroll.payslip",
            active_id=payslip_one.id,
            active_ids=[payslip_one.id, payslip_two.id],
        ).run()

        self.assertEqual(set((payslip_one | payslip_two).mapped("state")), {"confirmed"})

    def _make_wizard(self, date_from, date_to, department_ids=None, auto_compute=True):
        return self._model("pl.payroll.batch.wizard").create(
            {
                "date_from": date_from,
                "date_to": date_to,
                "company_id": self.test_company.id,
                "department_ids": [(6, 0, department_ids or [])],
                "auto_compute": auto_compute,
            }
        )

    def _make_employee(self, name, department):
        return self._model("hr.employee").create(
            {
                "name": name,
                "company_id": self.test_company.id,
                "department_id": department.id,
                "ssnid": "99123112345",
                "birthday": "1990-01-01",
                "gender": "female",
                "country_id": self.env.ref("base.pl").id,
            }
        )

    def _make_contract(self, name, employee):
        return self._model("hr.contract").create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.test_company.id,
                "date_start": date(2026, 1, 1),
                "state": "open",
                "wage": 6000.0,
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

    def _model(self, model_name):
        return self.env[model_name].with_context(allowed_company_ids=[self.test_company.id]).with_company(self.test_company)
