from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    kup_type = fields.Selection(
        [
            ("standard", "KUP standard 250 PLN"),
            ("standard_20", "KUP standard 20%"),
            ("autorskie", "KUP autorskie"),
        ],
        default="standard",
    )
    kup_autorskie_pct = fields.Float(default=0.0)
    ppk_participation = fields.Selection(
        [
            ("default", "PPK default"),
            ("opt_out", "PPK opt-out"),
            ("reduced", "PPK reduced"),
            ("additional", "PPK additional"),
        ],
        default="default",
    )
    ppk_ee_rate = fields.Float(default=2.0)
    ppk_additional = fields.Float(default=0.0)
    pit2_filed = fields.Boolean(default=True)
    ulga_type = fields.Selection(
        [
            ("none", "Brak"),
            ("mlodzi", "Ulga dla mlodych"),
            ("na_powrot", "Ulga na powrot"),
            ("rodzina_4_plus", "Ulga dla rodzin 4+"),
            ("senior", "Ulga dla seniorow"),
        ],
        default="none",
    )
    zus_code = fields.Char(default="0110")
