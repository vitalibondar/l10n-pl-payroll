from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PlPayrollPayslipLine(models.Model):
    _name = "pl.payroll.payslip.line"
    _description = "Pozycja listy płac"
    _order = "id"

    payslip_id = fields.Many2one(
        "pl.payroll.payslip",
        string="Lista płac",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Nazwa składnika",
        required=True,
        help="Nazwa dodatku, premii albo potrącenia widoczna na liście płac.",
    )
    category = fields.Selection(
        [
            ("bonus_gross", "Dodatek / premia brutto"),
            ("deduction_gross", "Potrącenie brutto"),
            ("deduction_net", "Potrącenie netto"),
        ],
        string="Rodzaj składnika",
        required=True,
        help="Wybierz, czy pozycja zwiększa brutto, zmniejsza brutto czy obniża już wyliczone netto.",
    )
    amount = fields.Float(
        string="Kwota",
        required=True,
        help="Kwota dodatku albo potrącenia w złotych.",
    )
    note = fields.Text(
        string="Uwagi",
        help="Krótka adnotacja wyjaśniająca, skąd pochodzi ta pozycja.",
    )

    @api.constrains("amount")
    def _check_amount_positive(self):
        for line in self:
            if line.amount <= 0.0:
                raise ValidationError(_("Kwota pozycji listy płac musi być większa od zera."))
