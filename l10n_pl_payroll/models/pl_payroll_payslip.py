from datetime import date
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
    department_id = fields.Many2one("hr.department", related="employee_id.department_id", store=True, readonly=True)
    contract_id = fields.Many2one("hr.contract", required=True)
    kup_type = fields.Selection(related="contract_id.kup_type", readonly=True, string="Typ KUP")
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

    gross = fields.Float(string="Brutto", readonly=True)
    overtime_hours_150 = fields.Float(string="Overtime Hours 150%")
    overtime_hours_200 = fields.Float(string="Overtime Hours 200%")
    overtime_amount = fields.Float(string="Overtime Amount", readonly=True)

    zus_emerytalne_ee = fields.Float(string="ZUS Emerytalne (EE)")
    zus_rentowe_ee = fields.Float(string="ZUS Rentowe (EE)")
    zus_chorobowe_ee = fields.Float(string="ZUS Chorobowe (EE)")
    zus_total_ee = fields.Float(string="ZUS Łącznie (EE)")

    health_basis = fields.Float(string="Podstawa zdrowotna")
    health = fields.Float(string="Składka zdrowotna")

    kup_amount = fields.Float(string="KUP")

    taxable_income = fields.Float(string="Dochód do opodatkowania")
    pit_advance = fields.Float(string="Zaliczka PIT")
    pit_reducing = fields.Float(string="Kwota zmniejszająca")
    pit_due = fields.Float(string="PIT do zapłaty")

    ppk_ee = fields.Float(string="PPK (EE)")

    net = fields.Float(string="Netto")

    zus_emerytalne_er = fields.Float(string="ZUS Emerytalne (ER)")
    zus_rentowe_er = fields.Float(string="ZUS Rentowe (ER)")
    zus_wypadkowe_er = fields.Float(string="ZUS Wypadkowe (ER)")
    zus_fp = fields.Float(string="Fundusz Pracy")
    zus_fgsp = fields.Float(string="FGŚP")
    ppk_er = fields.Float(string="PPK (ER)")
    total_employer_cost = fields.Float(string="Całkowity koszt pracodawcy")

    creative_report_id = fields.Many2one("pl.payroll.creative.report", readonly=True)
    creative_report_required = fields.Boolean(compute="_compute_creative_report_flags")
    creative_report_missing = fields.Boolean(compute="_compute_creative_report_flags")

    notes = fields.Text(string="Notes")

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

    @api.depends("contract_id.kup_type", "creative_report_id", "state")
    def _compute_creative_report_flags(self):
        for payslip in self:
            payslip.creative_report_required = (
                payslip.contract_id.kup_type == "autorskie"
            )
            payslip.creative_report_missing = (
                payslip.creative_report_required
                and not payslip.creative_report_id
            )

    def compute_payslip(self):
        for payslip in self:
            payslip._compute_single_payslip()
        return True

    def action_compute(self):
        self.compute_payslip()
        return True

    def action_confirm(self):
        for payslip in self:
            if payslip.state == "cancelled":
                continue
            if payslip.state == "draft":
                payslip.compute_payslip()
            payslip.write({"state": "confirmed"})
        return True

    def action_cancel(self):
        self.filtered(lambda payslip: payslip.state != "cancelled").write({"state": "cancelled"})
        return True

    def _compute_single_payslip(self):
        self.ensure_one()

        self._link_creative_report()

        base_gross = self._to_decimal(self.contract_id.wage)
        overtime_amount = self._compute_overtime_amount(base_gross)
        gross = self._round_amount(base_gross + overtime_amount)
        current_year = fields.Date.to_date(self.date_from).year
        ytd = self._get_ytd_totals(self.employee_id.id, current_year, self.date_from)
        zus_cap_basis = self._get_zus_cap_basis(ytd["zus_basis"], gross)

        zus_emerytalne_ee = self._percent_of_amount(zus_cap_basis, "ZUS_EMERY_EE")
        zus_rentowe_ee = self._percent_of_amount(zus_cap_basis, "ZUS_RENT_EE")
        zus_chorobowe_ee = self._percent_of_gross(gross, "ZUS_CHOR_EE")
        zus_total_ee = self._round_amount(zus_emerytalne_ee + zus_rentowe_ee + zus_chorobowe_ee)

        health_basis = self._round_amount(gross - zus_total_ee)
        health = self._round_amount(health_basis * self._get_parameter("HEALTH") / Decimal("100"))
        ppk_er = self._compute_ppk_employer(gross)
        kup_amount = self._compute_kup_amount(health_basis)
        taxable_income = self._floor_amount(health_basis - kup_amount + ppk_er)
        pit_advance, pit_reducing, pit_due = self._compute_pit_amounts(
            gross,
            taxable_income,
            ytd,
        )

        ppk_ee = self._compute_ppk_employee(gross)
        net = self._round_amount(gross - zus_total_ee - health - pit_due - ppk_ee)

        zus_emerytalne_er = self._percent_of_amount(zus_cap_basis, "ZUS_EMERY_ER")
        zus_rentowe_er = self._percent_of_amount(zus_cap_basis, "ZUS_RENT_ER")
        zus_wypadkowe_er = self._percent_of_gross(gross, "ZUS_WYPAD_ER", company_specific=True)
        zus_fp = self._percent_of_gross(gross, "ZUS_FP")
        zus_fgsp = self._percent_of_gross(gross, "ZUS_FGSP")
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
                "gross": float(gross),
                "overtime_amount": float(overtime_amount),
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

    def _link_creative_report(self):
        self.ensure_one()
        if self.contract_id.kup_type != "autorskie":
            return
        payslip_date = fields.Date.to_date(self.date_from)
        report = self.env["pl.payroll.creative.report"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("date", ">=", payslip_date.replace(day=1)),
                ("date", "<=", self.date_to),
                ("state", "=", "accepted"),
            ],
            limit=1,
        )
        if report:
            self.creative_report_id = report
            report.payslip_id = self

    def _compute_overtime_amount(self, base_gross):
        self.ensure_one()

        overtime_hours_150 = self._to_decimal(self.overtime_hours_150)
        overtime_hours_200 = self._to_decimal(self.overtime_hours_200)
        if overtime_hours_150 <= Decimal("0.00") and overtime_hours_200 <= Decimal("0.00"):
            return Decimal("0.00")

        standard_monthly_hours = self._get_parameter("STANDARD_MONTHLY_HOURS")
        if standard_monthly_hours <= Decimal("0.00"):
            raise UserError("Payroll parameter STANDARD_MONTHLY_HOURS must be greater than zero.")

        hourly_rate = base_gross / standard_monthly_hours
        overtime_amount = (
            overtime_hours_150 * hourly_rate * Decimal("1.5")
            + overtime_hours_200 * hourly_rate * Decimal("2.0")
        )
        return self._round_amount(overtime_amount)

    def _get_ytd_totals(self, employee_id, year, before_date):
        before_date = fields.Date.to_date(before_date)
        payslips = self.search(
            [
                ("employee_id", "=", employee_id),
                ("state", "=", "confirmed"),
                ("date_from", ">=", date(year, 1, 1)),
                ("date_from", "<", before_date),
            ],
            order="date_from asc, id asc",
        )
        pit_payslips = payslips.filtered(lambda slip: self._to_decimal(slip.pit_advance) > Decimal("0.00"))
        return {
            "gross": sum((self._to_decimal(value) for value in payslips.mapped("gross")), Decimal("0.00")),
            "zus_basis": sum((self._to_decimal(value) for value in payslips.mapped("gross")), Decimal("0.00")),
            "taxable_income": sum(
                (self._to_decimal(value) for value in payslips.mapped("taxable_income")),
                Decimal("0.00"),
            ),
            "pit_taxable_income": sum(
                (self._to_decimal(value) for value in pit_payslips.mapped("taxable_income")),
                Decimal("0.00"),
            ),
            "pit_reducing": sum(
                (self._to_decimal(value) for value in payslips.mapped("pit_reducing")),
                Decimal("0.00"),
            ),
            "pit_paid": sum((self._to_decimal(value) for value in payslips.mapped("pit_due")), Decimal("0.00")),
        }

    def _compute_pit_amounts(self, gross, current_taxable_income, ytd):
        self.ensure_one()

        pit_advance = Decimal("0.00")
        pit_reducing = Decimal("0.00")
        pit_due = Decimal("0")
        ulga_limit = self._get_parameter("PIT_THRESHOLD")

        if self.contract_id.ulga_type in ("mlodzi", "na_powrot", "rodzina_4_plus", "senior"):
            if ytd["gross"] + gross <= ulga_limit:
                return pit_advance, pit_reducing, pit_due

        threshold = self._get_parameter("PIT_THRESHOLD")
        cumulative_taxable_before = ytd["pit_taxable_income"]
        cumulative_taxable_after = cumulative_taxable_before + current_taxable_income

        pit_before_current = self._compute_tax_on_base(cumulative_taxable_before, threshold)
        pit_cumulative = self._compute_tax_on_base(cumulative_taxable_after, threshold)
        pit_advance = self._round_amount(pit_cumulative - pit_before_current)

        if self.contract_id.pit2_filed and not self._is_mandate_contract():
            pit_reducing = self._round_amount(self._get_parameter("PIT_REDUCING"))

        reducing_cumulative = ytd["pit_reducing"] + pit_reducing
        pit_due = self._floor_amount(max(Decimal("0.00"), pit_cumulative - reducing_cumulative - ytd["pit_paid"]))
        return pit_advance, pit_reducing, pit_due

    def _compute_tax_on_base(self, taxable_income, threshold):
        first_rate = self._get_parameter("PIT_RATE_1")
        second_rate = self._get_parameter("PIT_RATE_2")

        if taxable_income <= threshold:
            return self._round_amount(taxable_income * first_rate / Decimal("100"))
        return self._round_amount(
            threshold * first_rate / Decimal("100")
            + (taxable_income - threshold) * second_rate / Decimal("100")
        )

    def _get_zus_cap_basis(self, cumulative_gross_before, current_gross):
        zus_cap = self._get_parameter("ZUS_BASIS_CAP")
        if cumulative_gross_before >= zus_cap:
            return Decimal("0.00")
        remaining = zus_cap - cumulative_gross_before
        return min(current_gross, remaining)

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

    def _is_mandate_contract(self):
        self.ensure_one()
        contract_type_name = (self.contract_id.contract_type_id.name or "").strip().lower()
        return contract_type_name == "umowa zlecenie"

    def _percent_of_gross(self, gross, code, company_specific=False):
        return self._percent_of_amount(gross, code, company_specific=company_specific)

    def _percent_of_amount(self, amount, code, company_specific=False):
        rate = self._get_parameter(code, company_specific=company_specific)
        return self._round_amount(amount * rate / Decimal("100"))

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
