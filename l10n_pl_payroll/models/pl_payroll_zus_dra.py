from decimal import Decimal, ROUND_HALF_UP

from odoo import api, fields, models


TWOPLACES = Decimal("0.01")


class PlPayrollZusDra(models.Model):
    _name = "pl.payroll.zus.dra"
    _description = "Deklaracja miesięczna ZUS DRA"
    _order = "year desc, month desc, company_id"
    _sql_constraints = [
        (
            "pl_payroll_zus_dra_company_year_month_unique",
            "unique(company_id, year, month)",
            "Deklaracja ZUS DRA już istnieje dla tej firmy i okresu.",
        )
    ]

    name = fields.Char(compute="_compute_name", store=True, string="Nazwa")
    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        required=True,
        help="Firma, dla której przygotowano deklarację rozliczeniową ZUS DRA.",
    )
    year = fields.Integer(
        string="Rok rozliczenia",
        required=True,
        help="Rok deklaracji ZUS DRA.",
    )
    month = fields.Integer(
        string="Miesiąc rozliczenia",
        required=True,
        help="Miesiąc deklaracji ZUS DRA.",
    )
    state = fields.Selection(
        [
            ("draft", "Szkic"),
            ("confirmed", "Zatwierdzona"),
        ],
        string="Status",
        default="draft",
        required=True,
        help="Etap przygotowania deklaracji ZUS DRA. Ułatwia odróżnienie wersji roboczej od dokumentu gotowego do rozliczenia.",
    )

    employee_count = fields.Integer(
        readonly=True,
        string="Liczba pracowników",
        help="Liczba pracowników ujętych w deklaracji za dany okres.",
    )
    payslip_count = fields.Integer(
        readonly=True,
        string="Liczba list płac",
        help="Liczba potwierdzonych list płac wykorzystanych do deklaracji.",
    )

    total_emerytalne_ee = fields.Float(readonly=True, string="Składka emerytalna (pracownik)")
    total_emerytalne_er = fields.Float(readonly=True, string="Składka emerytalna (pracodawca)")
    total_rentowe_ee = fields.Float(readonly=True, string="Składka rentowa (pracownik)")
    total_rentowe_er = fields.Float(readonly=True, string="Składka rentowa (pracodawca)")
    total_chorobowe = fields.Float(readonly=True, string="Składka chorobowa")
    total_wypadkowe = fields.Float(readonly=True, string="Składka wypadkowa")
    total_health = fields.Float(readonly=True, string="Składka zdrowotna")
    total_fp = fields.Float(readonly=True, string="Składka na Fundusz Pracy")
    total_fgsp = fields.Float(readonly=True, string="Składka na FGŚP")

    total_zus_employee = fields.Float(
        readonly=True,
        compute="_compute_overall_totals",
        store=True,
        string="Składki pracownika razem",
        help="Suma składek finansowanych przez pracownika wraz ze składką zdrowotną.",
    )
    total_zus_employer = fields.Float(
        readonly=True,
        compute="_compute_overall_totals",
        store=True,
        string="Składki pracodawcy razem",
        help="Suma składek finansowanych przez pracodawcę za dany miesiąc.",
    )
    total_all = fields.Float(
        readonly=True,
        compute="_compute_overall_totals",
        store=True,
        string="Łącznie do zapłaty",
        help="Łączna kwota zobowiązania wobec ZUS za dany okres.",
    )

    line_ids = fields.One2many(
        "pl.payroll.zus.dra.line",
        "dra_id",
        string="Pozycje pracowników",
        readonly=True,
    )

    @api.depends("company_id.name", "year", "month")
    def _compute_name(self):
        for record in self:
            if record.company_id and record.year and record.month:
                record.name = "ZUS DRA %s-%02d - %s" % (record.year, record.month, record.company_id.name)
            else:
                record.name = False

    @api.depends(
        "total_emerytalne_ee",
        "total_rentowe_ee",
        "total_chorobowe",
        "total_health",
        "total_emerytalne_er",
        "total_rentowe_er",
        "total_wypadkowe",
        "total_fp",
        "total_fgsp",
    )
    def _compute_overall_totals(self):
        for record in self:
            total_zus_employee = (
                self._to_decimal(record.total_emerytalne_ee)
                + self._to_decimal(record.total_rentowe_ee)
                + self._to_decimal(record.total_chorobowe)
                + self._to_decimal(record.total_health)
            )
            total_zus_employer = (
                self._to_decimal(record.total_emerytalne_er)
                + self._to_decimal(record.total_rentowe_er)
                + self._to_decimal(record.total_wypadkowe)
                + self._to_decimal(record.total_fp)
                + self._to_decimal(record.total_fgsp)
            )
            record.total_zus_employee = float(self._round_amount(total_zus_employee))
            record.total_zus_employer = float(self._round_amount(total_zus_employer))
            record.total_all = float(self._round_amount(total_zus_employee + total_zus_employer))

    @api.model
    def prepare_vals_from_payslips(self, company, year, month, payslips):
        return {
            "company_id": company.id,
            "year": year,
            "month": month,
            "employee_count": len(payslips.mapped("employee_id")),
            "payslip_count": len(payslips),
            "total_emerytalne_ee": float(self._sum_field(payslips, "zus_emerytalne_ee")),
            "total_emerytalne_er": float(self._sum_field(payslips, "zus_emerytalne_er")),
            "total_rentowe_ee": float(self._sum_field(payslips, "zus_rentowe_ee")),
            "total_rentowe_er": float(self._sum_field(payslips, "zus_rentowe_er")),
            "total_chorobowe": float(self._sum_field(payslips, "zus_chorobowe_ee")),
            "total_wypadkowe": float(self._sum_field(payslips, "zus_wypadkowe_er")),
            "total_health": float(self._sum_field(payslips, "health")),
            "total_fp": float(self._sum_field(payslips, "zus_fp")),
            "total_fgsp": float(self._sum_field(payslips, "zus_fgsp")),
            "line_ids": [(0, 0, self._prepare_line_vals(payslip)) for payslip in payslips],
            "state": "draft",
        }

    @api.model
    def _prepare_line_vals(self, payslip):
        return {
            "company_id": payslip.company_id.id,
            "employee_id": payslip.employee_id.id,
            "payslip_id": payslip.id,
            "gross": float(self._round_amount(payslip.gross)),
            "emerytalne_ee": float(self._round_amount(payslip.zus_emerytalne_ee)),
            "emerytalne_er": float(self._round_amount(payslip.zus_emerytalne_er)),
            "rentowe_ee": float(self._round_amount(payslip.zus_rentowe_ee)),
            "rentowe_er": float(self._round_amount(payslip.zus_rentowe_er)),
            "chorobowe": float(self._round_amount(payslip.zus_chorobowe_ee)),
            "wypadkowe": float(self._round_amount(payslip.zus_wypadkowe_er)),
            "health": float(self._round_amount(payslip.health)),
            "fp": float(self._round_amount(payslip.zus_fp)),
            "fgsp": float(self._round_amount(payslip.zus_fgsp)),
        }

    @api.model
    def _sum_field(self, payslips, field_name):
        return self._round_amount(
            sum((self._to_decimal(getattr(payslip, field_name)) for payslip in payslips), Decimal("0.00"))
        )

    @api.model
    def _round_amount(self, value):
        return self._to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @api.model
    def _to_decimal(self, value):
        return Decimal(str(value or 0.0))
