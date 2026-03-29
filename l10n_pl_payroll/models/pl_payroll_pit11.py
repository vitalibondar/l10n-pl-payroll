from decimal import Decimal, ROUND_HALF_UP

from odoo import api, fields, models


TWOPLACES = Decimal("0.01")


class PlPayrollPit11(models.Model):
    _name = "pl.payroll.pit11"
    _description = "PIT-11 Annual Tax Information"
    _order = "year desc, employee_id"
    _sql_constraints = [
        (
            "pl_payroll_pit11_employee_company_year_unique",
            "unique(employee_id, company_id, year)",
            "PIT-11 already exists for this employee, company, and year.",
        )
    ]

    name = fields.Char(compute="_compute_name", store=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    company_id = fields.Many2one("res.company", required=True)
    year = fields.Integer(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
        required=True,
    )

    total_gross = fields.Float(readonly=True, string="Przychód łącznie")
    total_zus_ee = fields.Float(readonly=True, string="ZUS EE łącznie")
    total_health = fields.Float(readonly=True, string="Składka zdrowotna łącznie")
    health_deductible = fields.Float(readonly=True, string="Składka zdrowotna odliczana (7.75%)")
    total_kup = fields.Float(readonly=True, string="KUP łącznie")
    total_income = fields.Float(readonly=True, string="Dochód łącznie")
    total_pit_paid = fields.Float(readonly=True, string="Zaliczki PIT zapłacone")
    total_ppk_er = fields.Float(readonly=True, string="PPK pracodawcy (przychód)")

    payslip_count = fields.Integer(readonly=True)

    @api.depends("employee_id.name", "year")
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.year:
                record.name = "%s - PIT-11 %s" % (record.employee_id.name, record.year)
            else:
                record.name = False

    @api.model
    def prepare_vals_from_payslips(self, employee, company, year, payslips):
        total_ppk_er = sum(
            (self._to_decimal(payslip.ppk_er) for payslip in payslips),
            Decimal("0.00"),
        )
        total_gross = self._round_amount(
            sum(
                (
                    payslip._get_effective_gross_amount()
                    + self._to_decimal(payslip.ppk_er)
                    for payslip in payslips
                ),
                Decimal("0.00"),
            )
        )
        total_zus_ee = self._round_amount(
            sum((self._to_decimal(payslip.zus_total_ee) for payslip in payslips), Decimal("0.00"))
        )
        total_health = self._round_amount(
            sum((self._to_decimal(payslip.health) for payslip in payslips), Decimal("0.00"))
        )
        health_deductible = self._round_amount(
            sum(
                (
                    self._round_amount(self._to_decimal(payslip.health_basis) * Decimal("0.0775"))
                    for payslip in payslips
                ),
                Decimal("0.00"),
            )
        )
        total_kup = self._round_amount(
            sum((self._to_decimal(payslip.kup_amount) for payslip in payslips), Decimal("0.00"))
        )
        total_income = self._round_amount(
            sum((self._to_decimal(payslip.taxable_income) for payslip in payslips), Decimal("0.00"))
        )
        total_pit_paid = self._round_amount(
            sum((self._to_decimal(payslip.pit_due) for payslip in payslips), Decimal("0.00"))
        )

        return {
            "employee_id": employee.id,
            "company_id": company.id,
            "year": year,
            "total_gross": float(total_gross),
            "total_zus_ee": float(total_zus_ee),
            "total_health": float(total_health),
            "health_deductible": float(health_deductible),
            "total_kup": float(total_kup),
            "total_income": float(total_income),
            "total_pit_paid": float(total_pit_paid),
            "total_ppk_er": float(self._round_amount(total_ppk_er)),
            "payslip_count": len(payslips),
            "state": "draft",
        }

    @api.model
    def _round_amount(self, value):
        return self._to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @api.model
    def _to_decimal(self, value):
        return Decimal(str(value or 0.0))
