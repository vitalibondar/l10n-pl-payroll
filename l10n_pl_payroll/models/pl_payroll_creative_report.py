from odoo import api, fields, models
from odoo.exceptions import UserError


class PlPayrollCreativeReport(models.Model):
    _name = "pl.payroll.creative.report"
    _description = "Creative Work Report (Raport Autorski)"
    _order = "date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    date = fields.Date(required=True)
    description = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
    )
    accepted_by = fields.Many2one("res.users", readonly=True)
    accepted_date = fields.Date(readonly=True)
    payslip_id = fields.Many2one("pl.payroll.payslip", readonly=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends("employee_id.name", "date")
    def _compute_name(self):
        for report in self:
            if report.employee_id and report.date:
                report.name = "%s - %s" % (
                    report.employee_id.name,
                    fields.Date.to_date(report.date).strftime("%Y-%m"),
                )
            else:
                report.name = False

    def action_submit(self):
        for report in self:
            if report.state != "draft":
                raise UserError("Only draft reports can be submitted.")
            report.write({"state": "submitted"})
        return True

    def action_accept(self):
        for report in self:
            if report.state != "submitted":
                raise UserError("Only submitted reports can be accepted.")
            report.write({
                "state": "accepted",
                "accepted_by": self.env.uid,
                "accepted_date": fields.Date.context_today(self),
            })
        return True

    def action_reject(self):
        for report in self:
            if report.state != "submitted":
                raise UserError("Only submitted reports can be rejected.")
            report.write({
                "state": "rejected",
                "accepted_by": False,
                "accepted_date": False,
            })
        return True

    def action_reset(self):
        for report in self:
            if report.state not in ("submitted", "accepted", "rejected"):
                raise UserError("Only non-draft reports can be reset.")
            report.write({
                "state": "draft",
                "accepted_by": False,
                "accepted_date": False,
            })
        return True
