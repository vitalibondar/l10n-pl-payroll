from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from .test_fixtures import SCENARIO_XMLIDS


@tagged("post_install", "-at_install")
class TestPayrollBatchComputeWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["pl.payroll.batch.compute"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.contracts = cls.env["hr.contract"].browse(
            [
                cls.env.ref(contract_xmlid).id
                for _employee_xmlid, contract_xmlid in SCENARIO_XMLIDS.values()
            ]
        )

    def test_batch_wizard_creates_and_computes_demo_payslips(self):
        wizard = self.Wizard.create(
            {
                "date_from": date(2026, 1, 1),
                "date_to": date(2026, 1, 31),
            }
        )

        action = wizard.action_compute()
        payslips = self.Payslip.search(
            [
                ("contract_id", "in", self.contracts.ids),
                ("date_from", "=", date(2026, 1, 1)),
                ("date_to", "=", date(2026, 1, 31)),
            ]
        )

        self.assertEqual(len(payslips), len(self.contracts))
        self.assertEqual(set(payslips.mapped("state")), {"computed"})
        self.assertTrue(all(net > 0.0 for net in payslips.mapped("net")))
        self.assertEqual(action["res_model"], "pl.payroll.payslip")
        self.assertEqual(action["view_mode"], "tree,form")
