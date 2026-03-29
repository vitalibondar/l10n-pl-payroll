from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError


class PlPayrollPit11Wizard(models.TransientModel):
    _name = "pl.payroll.pit11.wizard"
    _description = "Generate PIT-11"

    year = fields.Integer(required=True, default=lambda self: fields.Date.context_today(self).year - 1)

    def action_generate(self):
        self.ensure_one()

        payslips = self.env["pl.payroll.payslip"].search(
            [
                ("state", "=", "confirmed"),
                ("date_from", ">=", date(self.year, 1, 1)),
                ("date_to", "<=", date(self.year, 12, 31)),
                ("company_id", "in", self.env.companies.ids),
            ],
            order="employee_id, company_id, date_from, id",
        )
        if not payslips:
            raise UserError(_("No confirmed payslips found for year %s.") % self.year)

        pit11_model = self.env["pl.payroll.pit11"]
        grouped_payslips = {}
        for payslip in payslips:
            key = (payslip.employee_id.id, payslip.company_id.id)
            grouped_payslips.setdefault(key, self.env["pl.payroll.payslip"])
            grouped_payslips[key] |= payslip

        for (_employee_id, _company_id), employee_payslips in grouped_payslips.items():
            employee = employee_payslips[0].employee_id
            company = employee_payslips[0].company_id
            vals = pit11_model.prepare_vals_from_payslips(employee, company, self.year, employee_payslips)
            existing = pit11_model.search(
                [
                    ("employee_id", "=", employee.id),
                    ("company_id", "=", company.id),
                    ("year", "=", self.year),
                ],
                limit=1,
            )
            if existing:
                existing.write(vals)
            else:
                pit11_model.create(vals)

        action = self.env.ref("l10n_pl_payroll.action_pl_payroll_pit11").read()[0]
        action["domain"] = [
            ("year", "=", self.year),
            ("company_id", "in", self.env.companies.ids),
        ]
        return action
