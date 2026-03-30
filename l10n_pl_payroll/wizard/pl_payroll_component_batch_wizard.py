from calendar import monthrange

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PlPayrollComponentBatchWizard(models.TransientModel):
    _name = "pl.payroll.component.batch.wizard"
    _description = "Dodawanie składnika zbiorczego"

    component_type_id = fields.Many2one(
        "pl.payroll.component.type",
        string="Typ składnika",
        required=True,
        help="Typ składnika, który zostanie dodany do list płac wybranych pracowników.",
    )
    amount = fields.Float(
        string="Kwota",
        required=True,
        help="Kwota składnika w złotych.",
    )
    date_from = fields.Date(
        string="Okres od",
        required=True,
        help="Pierwszy dzień okresu rozliczeniowego.",
    )
    date_to = fields.Date(
        string="Okres do",
        required=True,
        help="Ostatni dzień okresu rozliczeniowego.",
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Pracownicy",
        help="Wybierz pracowników. Pozostaw puste i zaznacz 'Wszyscy aktywni', aby dodać do wszystkich.",
    )
    all_active_employees = fields.Boolean(
        string="Wszyscy aktywni pracownicy",
        help="Zaznacz, aby dodać składnik do wszystkich pracowników z aktywnymi umowami.",
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Wydział",
        help="Filtruj pracowników według wydziału. Działa razem z 'Wszyscy aktywni'.",
    )
    note = fields.Text(
        string="Uwagi",
        help="Opcjonalna adnotacja, która pojawi się na dodanych pozycjach listy płac.",
    )

    @api.onchange("date_from")
    def _onchange_date_from(self):
        if self.date_from:
            current_date = fields.Date.to_date(self.date_from)
            last_day = monthrange(current_date.year, current_date.month)[1]
            self.date_from = current_date.replace(day=1)
            self.date_to = current_date.replace(day=last_day)

    @api.onchange("component_type_id")
    def _onchange_component_type(self):
        if self.component_type_id and self.component_type_id.default_amount:
            self.amount = self.component_type_id.default_amount

    def action_apply(self):
        self.ensure_one()
        if self.amount <= 0:
            raise ValidationError(_("Kwota musi być większa od zera."))
        if self.date_from > self.date_to:
            raise ValidationError(_("Data 'Okres od' nie może być późniejsza niż 'Okres do'."))

        employees = self._get_employees()
        if not employees:
            raise UserError(_("Nie znaleziono pracowników spełniających kryteria."))

        Payslip = self.env["pl.payroll.payslip"]
        ct = self.component_type_id
        affected_payslips = self.env["pl.payroll.payslip"]

        for employee in employees:
            payslip = Payslip.search(
                [
                    ("employee_id", "=", employee.id),
                    ("date_from", "=", self.date_from),
                    ("date_to", "=", self.date_to),
                    ("state", "=", "draft"),
                ],
                limit=1,
            )
            if not payslip:
                contract = self._get_active_contract(employee)
                if not contract:
                    continue
                payslip = Payslip.create(
                    {
                        "employee_id": employee.id,
                        "contract_id": contract.id,
                        "date_from": self.date_from,
                        "date_to": self.date_to,
                    }
                )

            self.env["pl.payroll.payslip.line"].create(
                {
                    "payslip_id": payslip.id,
                    "component_type_id": ct.id,
                    "name": ct.name,
                    "category": ct.category,
                    "amount": self.amount,
                    "pit_taxable": ct.pit_taxable,
                    "zus_included": ct.zus_included,
                    "note": self.note or False,
                }
            )
            affected_payslips |= payslip

        return {
            "type": "ir.actions.act_window",
            "name": _("Listy płac ze składnikiem"),
            "res_model": "pl.payroll.payslip",
            "view_mode": "list,form",
            "domain": [("id", "in", affected_payslips.ids)],
        }

    def _get_employees(self):
        if self.all_active_employees:
            domain = [
                ("contract_id.state", "=", "open"),
                ("contract_id.date_start", "<=", self.date_to),
                "|",
                ("contract_id.date_end", "=", False),
                ("contract_id.date_end", ">=", self.date_from),
            ]
            if self.department_id:
                domain.append(("department_id", "=", self.department_id.id))
            return self.env["hr.employee"].search(domain)
        return self.employee_ids

    def _get_active_contract(self, employee):
        return self.env["hr.contract"].search(
            [
                ("employee_id", "=", employee.id),
                ("state", "=", "open"),
                ("date_start", "<=", self.date_to),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", self.date_from),
            ],
            limit=1,
        )
