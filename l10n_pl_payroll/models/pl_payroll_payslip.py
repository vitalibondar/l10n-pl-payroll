from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from odoo import api, fields, models
from odoo.exceptions import UserError


TWOPLACES = Decimal("0.01")
WHOLE_ZLOTY = Decimal("1")


class PlPayrollPayslip(models.Model):
    _name = "pl.payroll.payslip"
    _description = "Polish Payroll Payslip"
    _order = "date_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    contract_id = fields.Many2one("hr.contract", required=True)
    company_id = fields.Many2one("res.company", related="contract_id.company_id", store=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )

    gross = fields.Float(related="contract_id.wage", readonly=True)

    zus_emerytalne_ee = fields.Float()
    zus_rentowe_ee = fields.Float()
    zus_chorobowe_ee = fields.Float()
    zus_total_ee = fields.Float()

    health_basis = fields.Float()
    health = fields.Float()

    kup_amount = fields.Float()

    taxable_income = fields.Float()
    pit_advance = fields.Float()
    pit_reducing = fields.Float()
    pit_due = fields.Float()

    ppk_ee = fields.Float()

    net = fields.Float()

    zus_emerytalne_er = fields.Float()
    zus_rentowe_er = fields.Float()
    zus_wypadkowe_er = fields.Float()
    zus_fp = fields.Float()
    zus_fgsp = fields.Float()
    ppk_er = fields.Float()
    total_employer_cost = fields.Float()

    notes = fields.Text()

    @api.depends("employee_id.name", "date_from")
    def _compute_name(self):
        for payslip in self:
            if payslip.employee_id and payslip.date_from:
                payslip.name = "%s - %s" % (
                    payslip.employee_id.name,
                    fields.Date.to_date(payslip.date_from).strftime("%Y-%m"),
                )
            else:
                payslip.name = False

    def compute_payslip(self):
        for payslip in self:
            payslip._compute_single_payslip()
        return True

    def _compute_single_payslip(self):
        self.ensure_one()

        gross = self._to_decimal(self.gross)
        zus_emerytalne_ee = self._percent_of_gross(gross, "ZUS_EMERY_EE")
        zus_rentowe_ee = self._percent_of_gross(gross, "ZUS_RENT_EE")
        zus_chorobowe_ee = self._percent_of_gross(gross, "ZUS_CHOR_EE")
        zus_total_ee = self._round_amount(zus_emerytalne_ee + zus_rentowe_ee + zus_chorobowe_ee)

        health_basis = self._round_amount(gross - zus_total_ee)
        health = self._round_amount(health_basis * self._get_parameter("HEALTH") / Decimal("100"))
        kup_amount = self._compute_kup_amount(health_basis)
        taxable_income = self._floor_amount(health_basis - kup_amount)

        pit_advance = Decimal("0.00")
        pit_reducing = Decimal("0.00")
        pit_due = Decimal("0")
        if self.contract_id.ulga_type not in ("mlodzi", "na_powrot", "rodzina_4_plus", "senior"):
            pit_advance = self._round_amount(
                taxable_income * self._get_parameter("PIT_RATE_1") / Decimal("100")
            )
            if self.contract_id.pit2_filed:
                pit_reducing = self._round_amount(self._get_parameter("PIT_REDUCING"))
            pit_due = self._floor_amount(max(Decimal("0.00"), pit_advance - pit_reducing))

        ppk_ee = self._compute_ppk_employee(gross)
        net = self._round_amount(gross - zus_total_ee - health - pit_due - ppk_ee)

        zus_emerytalne_er = self._percent_of_gross(gross, "ZUS_EMERY_ER")
        zus_rentowe_er = self._percent_of_gross(gross, "ZUS_RENT_ER")
        zus_wypadkowe_er = self._percent_of_gross(gross, "ZUS_WYPAD_ER", company_specific=True)
        zus_fp = self._percent_of_gross(gross, "ZUS_FP")
        zus_fgsp = self._percent_of_gross(gross, "ZUS_FGSP")
        ppk_er = self._compute_ppk_employer(gross)
        total_employer_cost = self._round_amount(
            gross
            + zus_emerytalne_er
            + zus_rentowe_er
            + zus_wypadkowe_er
            + zus_fp
            + zus_fgsp
            + ppk_er
        )

        self.write(
            {
                "zus_emerytalne_ee": float(zus_emerytalne_ee),
                "zus_rentowe_ee": float(zus_rentowe_ee),
                "zus_chorobowe_ee": float(zus_chorobowe_ee),
                "zus_total_ee": float(zus_total_ee),
                "health_basis": float(health_basis),
                "health": float(health),
                "kup_amount": float(kup_amount),
                "taxable_income": float(taxable_income),
                "pit_advance": float(pit_advance),
                "pit_reducing": float(pit_reducing),
                "pit_due": float(pit_due),
                "ppk_ee": float(ppk_ee),
                "net": float(net),
                "zus_emerytalne_er": float(zus_emerytalne_er),
                "zus_rentowe_er": float(zus_rentowe_er),
                "zus_wypadkowe_er": float(zus_wypadkowe_er),
                "zus_fp": float(zus_fp),
                "zus_fgsp": float(zus_fgsp),
                "ppk_er": float(ppk_er),
                "total_employer_cost": float(total_employer_cost),
                "state": "computed",
            }
        )

    def _compute_kup_amount(self, health_basis):
        self.ensure_one()
        if self.contract_id.kup_type == "autorskie":
            creative_share = self._to_decimal(self.contract_id.kup_autorskie_pct) / Decimal("100")
            return self._round_amount(health_basis * creative_share * Decimal("0.5"))
        if self.contract_id.kup_type == "standard_20":
            return self._round_amount(health_basis * Decimal("0.20"))
        return self._round_amount(self._get_parameter("KUP_STANDARD"))

    def _compute_ppk_employee(self, gross):
        self.ensure_one()
        if self.contract_id.ppk_participation == "opt_out":
            return Decimal("0.00")

        if self.contract_id.ppk_participation == "reduced":
            base_rate = self._get_parameter("PPK_EE_REDUCED")
        else:
            base_rate = self._to_decimal(self.contract_id.ppk_ee_rate)

        additional_rate = self._to_decimal(self.contract_id.ppk_additional)
        return self._round_amount(gross * (base_rate + additional_rate) / Decimal("100"))

    def _compute_ppk_employer(self, gross):
        self.ensure_one()
        if self.contract_id.ppk_participation == "opt_out":
            return Decimal("0.00")
        return self._round_amount(gross * self._get_parameter("PPK_ER") / Decimal("100"))

    def _percent_of_gross(self, gross, code, company_specific=False):
        rate = self._get_parameter(code, company_specific=company_specific)
        return self._round_amount(gross * rate / Decimal("100"))

    def _get_parameter(self, code, company_specific=False):
        parameter = self.env["pl.payroll.parameter"].get_value(
            code,
            self.date_to,
            self.company_id if company_specific else False,
        )
        if parameter is False:
            raise UserError("Missing payroll parameter: %s" % code)
        return self._to_decimal(parameter)

    def _round_amount(self, value):
        return self._to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def _floor_amount(self, value):
        return self._to_decimal(value).quantize(WHOLE_ZLOTY, rounding=ROUND_DOWN)

    def _to_decimal(self, value):
        return Decimal(str(value or 0.0))
