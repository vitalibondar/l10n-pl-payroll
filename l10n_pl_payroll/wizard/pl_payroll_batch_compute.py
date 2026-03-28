from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PlPayrollBatchCompute(models.TransientModel):
    _name = "pl.payroll.batch.compute"
    _description = "Polish Payroll Batch Compute"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_compute(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise ValidationError(_("Date From must be earlier than or equal to Date To."))

        contracts = self.env["hr.contract"].search(
            [
                ("employee_id", "!=", False),
                ("company_id", "in", self.env.companies.ids),
                ("date_start", "<=", self.date_to),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", self.date_from),
            ]
        )

        payslips = self.env["pl.payroll.payslip"]
        payslips_to_compute = self.env["pl.payroll.payslip"]
        for contract in contracts:
            payslip = payslips.search(
                [
                    ("contract_id", "=", contract.id),
                    ("date_from", "=", self.date_from),
                    ("date_to", "=", self.date_to),
                ],
                limit=1,
            )
            if not payslip:
                payslip = payslips.create(
                    {
                        "employee_id": contract.employee_id.id,
                        "contract_id": contract.id,
                        "date_from": self.date_from,
                        "date_to": self.date_to,
                    }
                )
            if payslip.state == "cancelled":
                payslip.write({"state": "draft"})
            if payslip.state != "confirmed":
                payslips_to_compute |= payslip
            payslips |= payslip

        if payslips_to_compute:
            payslips_to_compute.compute_payslip()

        return {
            "type": "ir.actions.act_window",
            "name": _("Payslips"),
            "res_model": "pl.payroll.payslip",
            "view_mode": "tree,form",
            "domain": [("id", "in", payslips.ids)],
        }
