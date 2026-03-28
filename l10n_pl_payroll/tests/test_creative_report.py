from datetime import date

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCreativeReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["pl.payroll.creative.report"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.employee = cls.env.ref("l10n_pl_payroll.demo_employee_3")
        cls.contract = cls.env.ref("l10n_pl_payroll.demo_contract_3")

    def _create_report(self, **kwargs):
        vals = {
            "employee_id": self.employee.id,
            "date": date(2026, 1, 15),
            "description": "Creative work: UI/UX design for new module.",
        }
        vals.update(kwargs)
        return self.Report.create(vals)

    def _create_payslip(self, contract):
        return self.Payslip.create({
            "employee_id": contract.employee_id.id,
            "contract_id": contract.id,
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 1, 31),
        })

    # -- Workflow tests --

    def test_report_workflow_draft_to_accepted(self):
        report = self._create_report()
        self.assertEqual(report.state, "draft")

        report.action_submit()
        self.assertEqual(report.state, "submitted")

        report.action_accept()
        self.assertEqual(report.state, "accepted")
        self.assertTrue(report.accepted_by)
        self.assertTrue(report.accepted_date)

    def test_report_workflow_submit_and_reject(self):
        report = self._create_report()
        report.action_submit()
        report.action_reject()
        self.assertEqual(report.state, "rejected")

    def test_report_workflow_reset_to_draft(self):
        report = self._create_report()
        report.action_submit()
        report.action_accept()
        report.action_reset()
        self.assertEqual(report.state, "draft")
        self.assertFalse(report.accepted_by)
        self.assertFalse(report.accepted_date)

    def test_submit_non_draft_raises(self):
        report = self._create_report()
        report.action_submit()
        with self.assertRaises(UserError):
            report.action_submit()

    def test_accept_non_submitted_raises(self):
        report = self._create_report()
        with self.assertRaises(UserError):
            report.action_accept()

    def test_reject_non_submitted_raises(self):
        report = self._create_report()
        with self.assertRaises(UserError):
            report.action_reject()

    def test_reset_draft_raises(self):
        report = self._create_report()
        with self.assertRaises(UserError):
            report.action_reset()

    # -- Payslip integration tests --

    def test_payslip_links_accepted_report(self):
        report = self._create_report()
        report.action_submit()
        report.action_accept()

        payslip = self._create_payslip(self.contract)
        payslip.compute_payslip()

        self.assertEqual(payslip.creative_report_id, report)
        self.assertFalse(payslip.creative_report_missing)

    def test_payslip_creative_report_required(self):
        payslip = self._create_payslip(self.contract)
        self.assertTrue(payslip.creative_report_required)

    def test_payslip_creative_report_missing_flag(self):
        payslip = self._create_payslip(self.contract)
        payslip.compute_payslip()

        self.assertTrue(payslip.creative_report_missing)

    def test_payslip_no_creative_report_needed_for_standard_kup(self):
        employee = self.env.ref("l10n_pl_payroll.demo_employee_1")
        contract = self.env.ref("l10n_pl_payroll.demo_contract_1")
        payslip = self.Payslip.create({
            "employee_id": employee.id,
            "contract_id": contract.id,
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 1, 31),
        })
        payslip.compute_payslip()
        self.assertFalse(payslip.creative_report_required)
        self.assertFalse(payslip.creative_report_missing)
