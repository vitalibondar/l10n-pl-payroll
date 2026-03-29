from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_student = fields.Boolean(string="Student / uczeń", default=False)
