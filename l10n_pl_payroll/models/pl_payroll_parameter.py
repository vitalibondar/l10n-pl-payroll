from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PlPayrollParameter(models.Model):
    _name = "pl.payroll.parameter"
    _description = "Parametr płacowy PL"
    _order = "code, date_from desc"

    name = fields.Char(
        string="Nazwa parametru",
        required=True,
        help="Czytelna nazwa parametru widoczna dla księgowej.",
    )
    code = fields.Char(
        string="Kod parametru",
        required=True,
        index=True,
        help="Stały kod techniczny używany w obliczeniach payroll.",
    )
    value = fields.Float(
        string="Wartość",
        required=True,
        help="Wartość liczbowa parametru obowiązująca w danym okresie.",
    )
    date_from = fields.Date(
        string="Data od",
        required=True,
        help="Pierwszy dzień obowiązywania parametru.",
    )
    date_to = fields.Date(
        string="Data do",
        help="Ostatni dzień obowiązywania parametru. Puste pole oznacza brak końca okresu.",
    )
    value_type = fields.Selection(
        [("percent", "Procent"), ("amount", "Kwota")],
        string="Typ wartości",
        required=True,
        help="Określa, czy parametr przechowuje procent czy kwotę.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        help="Jeżeli pole jest puste, parametr obowiązuje globalnie dla wszystkich firm.",
    )
    note = fields.Text(
        string="Uwagi",
        help="Dowolne objaśnienia, źródło stawki albo notatka o zmianie przepisów.",
    )

    @api.constrains("date_from", "date_to")
    def _check_date_range(self):
        for record in self:
            if record.date_to and record.date_to < record.date_from:
                raise ValidationError(_("Data do nie może być wcześniejsza niż data od."))

    @api.constrains("code", "date_from", "date_to", "company_id")
    def _check_no_overlap(self):
        for record in self:
            others = self.search(
                [
                    ("id", "!=", record.id),
                    ("code", "=", record.code),
                    ("company_id", "=", record.company_id.id or False),
                ]
            )
            for other in others:
                if self._dates_overlap(
                    record.date_from,
                    record.date_to,
                    other.date_from,
                    other.date_to,
                ):
                    raise ValidationError(
                        _("Okresy parametrów nie mogą się nakładać dla tego samego kodu i firmy.")
                    )

    @api.model
    def get_value(self, code, date=None, company_id=None):
        target_date = fields.Date.to_date(date) if date else fields.Date.context_today(self)
        company = company_id.id if hasattr(company_id, "id") else company_id or False

        parameter = self.search(
            self._get_effective_domain(code, target_date, company),
            order="date_from desc, id desc",
            limit=1,
        )
        if not parameter and company:
            parameter = self.search(
                self._get_effective_domain(code, target_date, False),
                order="date_from desc, id desc",
                limit=1,
            )
        return parameter.value if parameter else False

    @api.model
    def _get_effective_domain(self, code, target_date, company):
        return [
            ("code", "=", code),
            ("company_id", "=", company),
            ("date_from", "<=", target_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", target_date),
        ]

    @api.model
    def _dates_overlap(self, start_a, end_a, start_b, end_b):
        end_a = end_a or fields.Date.to_date("9999-12-31")
        end_b = end_b or fields.Date.to_date("9999-12-31")
        return start_a <= end_b and start_b <= end_a
