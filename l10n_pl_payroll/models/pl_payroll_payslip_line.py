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
    component_type_id = fields.Many2one(
        "pl.payroll.component.type",
        string="Typ składnika",
        help="Typ składnika determinuje zasady PIT i ZUS.",
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
            ("benefit_in_kind", "Świadczenie rzeczowe"),
            ("deduction_net", "Potrącenie netto"),
        ],
        string="Rodzaj składnika",
        required=True,
        help="Wybierz, czy pozycja zwiększa brutto, zmniejsza brutto, jest świadczeniem rzeczowym czy obniża już wyliczone netto.",
    )
    amount = fields.Float(
        string="Kwota",
        required=True,
        help="Kwota dodatku albo potrącenia w złotych.",
    )
    pit_taxable = fields.Boolean(
        string="Podlega PIT",
        default=True,
    )
    zus_included = fields.Boolean(
        string="Podlega ZUS",
        default=True,
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

    @api.onchange("component_type_id")
    def _onchange_component_type(self):
        if self.component_type_id:
            ct = self.component_type_id
            self.name = ct.name
            self.category = ct.category
            self.pit_taxable = ct.pit_taxable
            self.zus_included = ct.zus_included
            if ct.default_amount:
                self.amount = ct.default_amount
