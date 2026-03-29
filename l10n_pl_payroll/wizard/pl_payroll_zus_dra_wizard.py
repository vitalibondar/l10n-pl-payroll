from calendar import monthrange
from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError


class PlPayrollZusDraWizard(models.TransientModel):
    _name = "pl.payroll.zus.dra.wizard"
    _description = "Generate ZUS DRA"

    year = fields.Integer(required=True, default=lambda self: fields.Date.context_today(self).year)
    month = fields.Integer(required=True, default=lambda self: fields.Date.context_today(self).month)

    def action_generate(self):
        self.ensure_one()
        if self.month < 1 or self.month > 12:
            raise UserError(_("Month must be between 1 and 12."))

        date_from = date(self.year, self.month, 1)
        date_to = date(self.year, self.month, monthrange(self.year, self.month)[1])
        payslips = self.env["pl.payroll.payslip"].search(
            [
                ("state", "=", "confirmed"),
                ("date_from", ">=", date_from),
                ("date_to", "<=", date_to),
                ("company_id", "in", self.env.companies.ids),
            ],
            order="company_id, employee_id, date_from, id",
        )
        if not payslips:
            raise UserError(_("No confirmed payslips found for %02d/%s.") % (self.month, self.year))

        dra_model = self.env["pl.payroll.zus.dra"]
        grouped_payslips = {}
        for payslip in payslips:
            grouped_payslips.setdefault(payslip.company_id.id, self.env["pl.payroll.payslip"])
            grouped_payslips[payslip.company_id.id] |= payslip

        for _company_id, company_payslips in grouped_payslips.items():
            company = company_payslips[0].company_id
            vals = dra_model.prepare_vals_from_payslips(company, self.year, self.month, company_payslips)
            existing = dra_model.search(
                [
                    ("company_id", "=", company.id),
                    ("year", "=", self.year),
                    ("month", "=", self.month),
                ],
                limit=1,
            )
            if existing:
                existing.line_ids.unlink()
                existing.write(vals)
            else:
                dra_model.create(vals)

        action = self.env.ref("l10n_pl_payroll.action_pl_payroll_zus_dra").read()[0]
        action["domain"] = [
            ("year", "=", self.year),
            ("month", "=", self.month),
            ("company_id", "in", self.env.companies.ids),
        ]
        return action
