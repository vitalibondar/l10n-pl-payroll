from calendar import monthrange

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PlPayrollBatchWizard(models.TransientModel):
    _name = "pl.payroll.batch.wizard"
    _description = "Generowanie list płac"

    date_from = fields.Date(
        string="Okres od",
        required=True,
        help="Pierwszy dzień okresu list płac, który ma zostać wygenerowany.",
    )
    date_to = fields.Date(
        string="Okres do",
        required=True,
        help="Ostatni dzień okresu list płac, który ma zostać wygenerowany.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        required=True,
        default=lambda self: self.env.company,
        help="Firma, dla której mają zostać wygenerowane listy płac.",
    )
    department_ids = fields.Many2many(
        "hr.department",
        string="Wydziały",
        help="Pozostaw puste, aby wygenerować listy płac dla wszystkich wydziałów w wybranej firmie.",
    )
    auto_compute = fields.Boolean(
        default=True,
        string="Oblicz po utworzeniu",
        help="Jeżeli zaznaczone, system od razu przeliczy nowo utworzone listy płac.",
    )

    @api.onchange("date_from")
    def _onchange_date_from(self):
        if self.date_from:
            current_date = fields.Date.to_date(self.date_from)
            last_day = monthrange(current_date.year, current_date.month)[1]
            self.date_from = current_date.replace(day=1)
            self.date_to = current_date.replace(day=last_day)

    def action_generate(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise ValidationError(_("Data „Okres od” nie może być późniejsza niż „Okres do”."))

        contract_domain = [
            ("state", "=", "open"),
            ("employee_id", "!=", False),
            ("company_id", "=", self.company_id.id),
            ("date_start", "<=", self.date_to),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", self.date_from),
        ]
        if self.department_ids:
            contract_domain.append(("employee_id.department_id", "in", self.department_ids.ids))

        Contract = self.env["hr.contract"]
        Payslip = self.env["pl.payroll.payslip"]
        contracts = Contract.search(contract_domain)
        created_payslips = self.env["pl.payroll.payslip"]

        for contract in contracts:
            existing = Payslip.search(
                [
                    ("employee_id", "=", contract.employee_id.id),
                    ("company_id", "=", self.company_id.id),
                    ("date_from", "=", self.date_from),
                    ("date_to", "=", self.date_to),
                    ("state", "!=", "cancelled"),
                ],
                limit=1,
            )
            if existing:
                continue

            created_payslips |= Payslip.create(
                {
                    "employee_id": contract.employee_id.id,
                    "contract_id": contract.id,
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                }
            )

        if self.auto_compute and created_payslips:
            created_payslips.compute_payslip()

        return {
            "type": "ir.actions.act_window",
            "name": _("Nowo utworzone listy płac"),
            "res_model": "pl.payroll.payslip",
            "view_mode": "list,form",
            "domain": [("id", "in", created_payslips.ids)],
        }
