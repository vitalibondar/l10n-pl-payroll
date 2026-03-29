from odoo import fields, models


class PlPayrollZusDraLine(models.Model):
    _name = "pl.payroll.zus.dra.line"
    _description = "ZUS DRA Line (per employee)"
    _order = "employee_id, id"

    dra_id = fields.Many2one("pl.payroll.zus.dra", required=True, ondelete="cascade")
    company_id = fields.Many2one("res.company", required=True, readonly=True)
    employee_id = fields.Many2one("hr.employee", readonly=True)
    payslip_id = fields.Many2one("pl.payroll.payslip", readonly=True)

    gross = fields.Float(readonly=True)
    emerytalne_ee = fields.Float(readonly=True)
    emerytalne_er = fields.Float(readonly=True)
    rentowe_ee = fields.Float(readonly=True)
    rentowe_er = fields.Float(readonly=True)
    chorobowe = fields.Float(readonly=True)
    wypadkowe = fields.Float(readonly=True)
    health = fields.Float(readonly=True)
    fp = fields.Float(readonly=True)
    fgsp = fields.Float(readonly=True)
