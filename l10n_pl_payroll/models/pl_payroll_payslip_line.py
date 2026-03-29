from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PlPayrollPayslipLine(models.Model):
    _name = "pl.payroll.payslip.line"
    _description = "Polish Payroll Payslip Line"
    _order = "id"

    payslip_id = fields.Many2one("pl.payroll.payslip", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    category = fields.Selection(
        [
            ("bonus_gross", "Bonus (Gross)"),
            ("deduction_gross", "Deduction (Gross)"),
            ("deduction_net", "Deduction (Net)"),
        ],
        required=True,
    )
    amount = fields.Float(required=True)
    note = fields.Text()

    @api.constrains("amount")
    def _check_amount_positive(self):
        for line in self:
            if line.amount <= 0.0:
                raise ValidationError("Payslip line amount must be greater than zero.")
