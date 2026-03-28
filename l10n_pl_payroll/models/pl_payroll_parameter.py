from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PlPayrollParameter(models.Model):
    _name = "pl.payroll.parameter"
    _description = "Polish Payroll Parameter"
    _order = "code, date_from desc"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    value = fields.Float(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date()
    value_type = fields.Selection(
        [("percent", "Відсоток"), ("amount", "Сума")],
        required=True,
    )
    company_id = fields.Many2one("res.company")
    note = fields.Text()

    @api.constrains("date_from", "date_to")
    def _check_date_range(self):
        for record in self:
            if record.date_to and record.date_to < record.date_from:
                raise ValidationError("Date To must be greater than or equal to Date From.")

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
                        "Parameter periods cannot overlap for the same code and company."
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
