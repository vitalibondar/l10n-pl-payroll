from odoo import fields, models


class PlPayrollZusDraLine(models.Model):
    _name = "pl.payroll.zus.dra.line"
    _description = "Pozycja deklaracji ZUS DRA"
    _order = "employee_id, id"

    dra_id = fields.Many2one(
        "pl.payroll.zus.dra",
        string="Deklaracja ZUS DRA",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one("res.company", string="Firma", required=True, readonly=True)
    employee_id = fields.Many2one("hr.employee", string="Pracownik", readonly=True)
    payslip_id = fields.Many2one("pl.payroll.payslip", string="Lista płac", readonly=True)

    gross = fields.Float(string="Wynagrodzenie brutto", readonly=True)
    emerytalne_ee = fields.Float(string="Składka emerytalna (pracownik)", readonly=True)
    emerytalne_er = fields.Float(string="Składka emerytalna (pracodawca)", readonly=True)
    rentowe_ee = fields.Float(string="Składka rentowa (pracownik)", readonly=True)
    rentowe_er = fields.Float(string="Składka rentowa (pracodawca)", readonly=True)
    chorobowe = fields.Float(string="Składka chorobowa", readonly=True)
    wypadkowe = fields.Float(string="Składka wypadkowa", readonly=True)
    health = fields.Float(string="Składka zdrowotna", readonly=True)
    fp = fields.Float(string="Składka na Fundusz Pracy", readonly=True)
    fgsp = fields.Float(string="Składka na FGŚP", readonly=True)
