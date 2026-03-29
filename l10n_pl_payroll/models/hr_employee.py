from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_student = fields.Boolean(
        string="Status ucznia / studenta",
        default=False,
        help="Zaznacz dla osoby uczącej się do 26. roku życia. Przy umowie zlecenia "
             "taki status może zwalniać z naliczania składek ZUS i zdrowotnej.",
    )
