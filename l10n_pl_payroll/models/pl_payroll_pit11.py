from decimal import Decimal, ROUND_HALF_UP

from odoo import api, fields, models


TWOPLACES = Decimal("0.01")


class PlPayrollPit11(models.Model):
    _name = "pl.payroll.pit11"
    _description = "Informacja roczna PIT-11"
    _order = "year desc, employee_id"
    _sql_constraints = [
        (
            "pl_payroll_pit11_employee_company_year_unique",
            "unique(employee_id, company_id, year)",
            "PIT-11 już istnieje dla tego pracownika, firmy i roku.",
        )
    ]

    name = fields.Char(compute="_compute_name", store=True, string="Nazwa")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Pracownik",
        required=True,
        help="Pracownik, dla którego przygotowano informację PIT-11.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        required=True,
        help="Firma występująca jako płatnik na informacji PIT-11.",
    )
    year = fields.Integer(
        string="Rok podatkowy",
        required=True,
        help="Rok, za który zsumowano przychody, składki i zaliczki PIT.",
    )
    state = fields.Selection(
        [
            ("draft", "Szkic"),
            ("confirmed", "Zatwierdzony"),
        ],
        string="Status",
        default="draft",
        required=True,
        help="Status dokumentu PIT-11 w module payroll.",
    )

    total_gross = fields.Float(
        readonly=True,
        string="Przychód łącznie",
        help="Łączny przychód wykazany na PIT-11, razem z opodatkowaną wpłatą PPK pracodawcy.",
    )
    total_zus_ee = fields.Float(
        readonly=True,
        string="Składki ZUS pracownika łącznie",
        help="Suma składek społecznych finansowanych przez pracownika.",
    )
    total_health = fields.Float(
        readonly=True,
        string="Składka zdrowotna łącznie",
        help="Suma pobranych składek zdrowotnych za wskazany rok.",
    )
    health_deductible = fields.Float(
        readonly=True,
        string="Składka zdrowotna odliczana (7,75%)",
        help="Wartość historycznej części zdrowotnej prezentowana informacyjnie na formularzu PIT-11.",
    )
    total_kup = fields.Float(
        readonly=True,
        string="KUP łącznie",
        help="Suma kosztów uzyskania przychodu uwzględnionych przy rozliczeniu rocznym.",
    )
    total_income = fields.Float(
        readonly=True,
        string="Dochód łącznie",
        help="Dochód do opodatkowania po kosztach uzyskania przychodu.",
    )
    total_pit_paid = fields.Float(
        readonly=True,
        string="Pobrane zaliczki PIT",
        help="Łączna kwota zaliczek PIT pobranych i odprowadzonych w danym roku.",
    )
    total_ppk_er = fields.Float(
        readonly=True,
        string="Wpłata PPK pracodawcy jako przychód",
        help="Wpłata finansowana przez pracodawcę, która zwiększa przychód pracownika do PIT.",
    )

    payslip_count = fields.Integer(
        readonly=True,
        string="Liczba list płac",
        help="Ile list płac weszło do rozliczenia PIT-11.",
    )

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
