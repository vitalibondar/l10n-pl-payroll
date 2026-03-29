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
    sick_days = fields.Integer(string="Dni chorobowe (wynagrodzenie)", default=0)
    sick_days_100 = fields.Integer(
        string="Dni chorobowe 100%",
        default=0,
        help="Ciąża lub wypadek przy pracy",
    )
    sick_leave_amount = fields.Float(string="Wynagrodzenie chorobowe", readonly=True)
    sick_leave_basis = fields.Float(string="Podstawa chorobowego", readonly=True)
    working_days_in_month = fields.Integer(
        string="Dni robocze w miesiącu",
        default=0,
        help="Actual working days in month. If 0, treated as full month.",
    )
    overtime_hours_150 = fields.Float(string="Overtime Hours 150%")
    overtime_hours_200 = fields.Float(string="Overtime Hours 200%")
    overtime_amount = fields.Float(string="Overtime Amount", readonly=True)
    payslip_line_ids = fields.One2many("pl.payroll.payslip.line", "payslip_id")
    bonus_gross_total = fields.Float(compute="_compute_payslip_line_totals", store=True)
    deduction_gross_total = fields.Float(compute="_compute_payslip_line_totals", store=True)
    deduction_net_total = fields.Float(compute="_compute_payslip_line_totals", store=True)

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
    etat_fraction = fields.Float(compute="_compute_etat_fraction", store=True, string="Wymiar etatu")
    below_minimum_wage = fields.Boolean(compute="_compute_minimum_wage_warning", store=True)
    ytd_sick_days = fields.Integer(compute="_compute_ytd_sick_days", string="Dni chorobowe (rocznie)")

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

    @api.depends(
        "contract_id.resource_calendar_id.attendance_ids.hour_from",
        "contract_id.resource_calendar_id.attendance_ids.hour_to",
        "company_id.resource_calendar_id.attendance_ids.hour_from",
        "company_id.resource_calendar_id.attendance_ids.hour_to",
    )
    def _compute_etat_fraction(self):
        for payslip in self:
            payslip.etat_fraction = float(payslip._get_etat_fraction())

    @api.depends(
        "gross",
        "date_to",
        "contract_id.resource_calendar_id.attendance_ids.hour_from",
        "contract_id.resource_calendar_id.attendance_ids.hour_to",
        "company_id.resource_calendar_id.attendance_ids.hour_from",
        "company_id.resource_calendar_id.attendance_ids.hour_to",
    )
    def _compute_minimum_wage_warning(self):
        for payslip in self:
            below_minimum_wage = False
            if payslip.gross and payslip.date_to:
                minimum_wage = payslip._get_minimum_wage_parameter()
                if minimum_wage is not False:
                    threshold = payslip._round_amount(minimum_wage * payslip._get_etat_fraction())
                    below_minimum_wage = payslip._to_decimal(payslip.gross) < threshold
            payslip.below_minimum_wage = below_minimum_wage

    @api.depends("payslip_line_ids.category", "payslip_line_ids.amount")
    def _compute_payslip_line_totals(self):
        for payslip in self:
            bonus_gross_total = Decimal("0.00")
            deduction_gross_total = Decimal("0.00")
            deduction_net_total = Decimal("0.00")
            for line in payslip.payslip_line_ids:
                amount = payslip._to_decimal(line.amount)
                if line.category == "bonus_gross":
                    bonus_gross_total += amount
                elif line.category == "deduction_gross":
                    deduction_gross_total += amount
                elif line.category == "deduction_net":
                    deduction_net_total += amount
            payslip.bonus_gross_total = float(payslip._round_amount(bonus_gross_total))
            payslip.deduction_gross_total = float(payslip._round_amount(deduction_gross_total))
            payslip.deduction_net_total = float(payslip._round_amount(deduction_net_total))

    @api.depends("employee_id", "date_from", "sick_days", "sick_days_100")
    def _compute_ytd_sick_days(self):
        for payslip in self:
            if not payslip.employee_id or not payslip.date_from:
                payslip.ytd_sick_days = 0
                continue
            current_year = fields.Date.to_date(payslip.date_from).year
            ytd = payslip._get_ytd_totals(payslip.employee_id.id, current_year, payslip.date_from)
            payslip.ytd_sick_days = ytd["sick_days_used"] + payslip._get_total_sick_days()

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
        bonus_gross_total = self._to_decimal(self.bonus_gross_total)
        deduction_gross_total = self._to_decimal(self.deduction_gross_total)
        deduction_net_total = self._to_decimal(self.deduction_net_total)
        gross = self._round_amount(base_gross + overtime_amount + bonus_gross_total - deduction_gross_total)
        sick_amount, sick_basis, adjusted_gross = self._compute_sick_leave(gross)
        effective_gross = self._round_amount(adjusted_gross + sick_amount)
        current_year = fields.Date.to_date(self.date_from).year
        ytd = self._get_ytd_totals(self.employee_id.id, current_year, self.date_from)
        zus_cap_basis = self._get_zus_cap_basis(ytd["zus_basis"], adjusted_gross)
        student_zlecenie_exempt = self._is_student_zlecenie_exempt()

        if student_zlecenie_exempt:
            zus_emerytalne_ee = Decimal("0.00")
            zus_rentowe_ee = Decimal("0.00")
            zus_chorobowe_ee = Decimal("0.00")
            zus_total_ee = Decimal("0.00")
        else:
            zus_emerytalne_ee = self._percent_of_amount(zus_cap_basis, "ZUS_EMERY_EE")
            zus_rentowe_ee = self._percent_of_amount(zus_cap_basis, "ZUS_RENT_EE")
            zus_chorobowe_ee = self._percent_of_gross(adjusted_gross, "ZUS_CHOR_EE")
            zus_total_ee = self._round_amount(zus_emerytalne_ee + zus_rentowe_ee + zus_chorobowe_ee)

        health_basis = self._round_amount(adjusted_gross - zus_total_ee + sick_amount)
        if student_zlecenie_exempt:
            health = Decimal("0.00")
            ppk_er = Decimal("0.00")
        else:
            health = self._round_amount(health_basis * self._get_parameter("HEALTH") / Decimal("100"))
            ppk_er = self._compute_ppk_employer(adjusted_gross)
        kup_amount = self._compute_kup_amount(health_basis)
        taxable_income = self._floor_amount(health_basis - kup_amount + ppk_er)
        pit_advance, pit_reducing, pit_due = self._compute_pit_amounts(
            effective_gross,
            taxable_income,
            ytd,
        )

        if student_zlecenie_exempt:
            ppk_ee = Decimal("0.00")
        else:
            ppk_ee = self._compute_ppk_employee(adjusted_gross)
        net_before_deductions = self._round_amount(effective_gross - zus_total_ee - health - pit_due - ppk_ee)
        net = self._round_amount(net_before_deductions - deduction_net_total)

        if student_zlecenie_exempt:
            zus_emerytalne_er = Decimal("0.00")
            zus_rentowe_er = Decimal("0.00")
            zus_wypadkowe_er = Decimal("0.00")
            zus_fp = Decimal("0.00")
            zus_fgsp = Decimal("0.00")
        else:
            zus_emerytalne_er = self._percent_of_amount(zus_cap_basis, "ZUS_EMERY_ER")
            zus_rentowe_er = self._percent_of_amount(zus_cap_basis, "ZUS_RENT_ER")
            zus_wypadkowe_er = self._percent_of_gross(adjusted_gross, "ZUS_WYPAD_ER", company_specific=True)
            zus_fp = self._percent_of_gross(adjusted_gross, "ZUS_FP")
            zus_fgsp = self._percent_of_gross(adjusted_gross, "ZUS_FGSP")
        total_employer_cost = self._round_amount(
            effective_gross
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
                "sick_leave_amount": float(sick_amount),
                "sick_leave_basis": float(sick_basis),
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

    def _compute_sick_leave_basis(self):
        self.ensure_one()
        prior_payslips = self.search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "=", "confirmed"),
                ("date_from", "<", self.date_from),
            ],
            order="date_from desc, id desc",
            limit=12,
        )

        if not prior_payslips:
            wage = self._to_decimal(self.contract_id.wage)
            zus_rate = (
                self._get_parameter("ZUS_EMERY_EE")
                + self._get_parameter("ZUS_RENT_EE")
                + self._get_parameter("ZUS_CHOR_EE")
            ) / Decimal("100")
            return self._round_amount(wage * (Decimal("1") - zus_rate))

        total = sum(
            (
                self._to_decimal(payslip.gross) - self._to_decimal(payslip.zus_total_ee)
                for payslip in prior_payslips
            ),
            Decimal("0.00"),
        )
        return self._round_amount(total / Decimal(str(len(prior_payslips))))

    def _compute_sick_leave(self, gross):
        self.ensure_one()
        sick_80 = self.sick_days or 0
        sick_100 = self.sick_days_100 or 0
        total_sick = sick_80 + sick_100
        if total_sick <= 0:
            return Decimal("0.00"), Decimal("0.00"), gross

        basis = self._compute_sick_leave_basis()
        daily_rate = basis / Decimal("30")
        sick_amount = self._round_amount(
            daily_rate * Decimal(str(sick_80)) * Decimal("0.80")
            + daily_rate * Decimal(str(sick_100)) * Decimal("1.00")
        )
        adjusted_gross = self._get_adjusted_gross_for_sick(gross)
        return sick_amount, basis, adjusted_gross

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
            "gross": sum((payslip._get_effective_gross_amount() for payslip in payslips), Decimal("0.00")),
            "zus_basis": sum(
                (payslip._get_adjusted_gross_for_sick(payslip.gross) for payslip in payslips),
                Decimal("0.00"),
            ),
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
            "sick_days_used": sum((payslip._get_total_sick_days() for payslip in payslips), 0),
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

    def _get_etat_fraction(self):
        self.ensure_one()
        calendar = self.contract_id.resource_calendar_id
        if not calendar:
            return Decimal("1")
        company_calendar = self.company_id.resource_calendar_id
        contract_hours = self._get_calendar_hours_per_week(calendar)
        company_hours = self._get_calendar_hours_per_week(company_calendar)
        if contract_hours <= Decimal("0") or company_hours <= Decimal("0"):
            return Decimal("1")
        fraction = contract_hours / company_hours
        return min(fraction, Decimal("1"))

    def _get_total_sick_days(self):
        self.ensure_one()
        return (self.sick_days or 0) + (self.sick_days_100 or 0)

    def _get_adjusted_gross_for_sick(self, gross):
        self.ensure_one()
        gross = self._to_decimal(gross)
        total_sick = self._get_total_sick_days()
        working_days = self.working_days_in_month or 30
        if total_sick <= 0 or working_days <= 0:
            return gross

        gross_reduction = self._round_amount(
            gross / Decimal(str(working_days)) * Decimal(str(total_sick))
        )
        return max(Decimal("0.00"), gross - gross_reduction)

    def _get_effective_gross_amount(self):
        self.ensure_one()
        gross = self._to_decimal(self.gross)
        if self._get_total_sick_days() <= 0:
            return gross
        return self._round_amount(
            self._get_adjusted_gross_for_sick(gross) + self._to_decimal(self.sick_leave_amount)
        )

    def _get_calendar_hours_per_week(self, calendar):
        if not calendar:
            return Decimal("0")
        total = Decimal("0")
        for attendance in calendar.attendance_ids:
            hours = Decimal(str(attendance.hour_to or 0.0)) - Decimal(str(attendance.hour_from or 0.0))
            if hours > Decimal("0"):
                total += hours
        return total

    def _compute_kup_amount(self, health_basis):
        self.ensure_one()
        if self.contract_id.kup_type == "autorskie":
            creative_share = self._to_decimal(self.contract_id.kup_autorskie_pct) / Decimal("100")
            return self._round_amount(health_basis * creative_share * Decimal("0.5"))
        if self.contract_id.kup_type == "standard_20":
            return self._round_amount(health_basis * Decimal("0.20"))
        kup_full = self._get_parameter("KUP_STANDARD")
        return self._round_amount(kup_full * self._get_etat_fraction())

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

    def _is_student_zlecenie_exempt(self):
        self.ensure_one()
        if not self._is_mandate_contract():
            return False
        if not self.employee_id.is_student:
            return False

        birthday = self.employee_id.birthday
        if not birthday:
            return False

        payslip_date = fields.Date.to_date(self.date_from)
        birthday = fields.Date.to_date(birthday)
        age = payslip_date.year - birthday.year
        if (payslip_date.month, payslip_date.day) < (birthday.month, birthday.day):
            age -= 1
        return age < 26

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

    def _get_minimum_wage_parameter(self):
        self.ensure_one()
        for code in ("MINIMUM_WAGE", "MIN_WAGE"):
            parameter = self.env["pl.payroll.parameter"].get_value(code, self.date_to)
            if parameter is not False:
                return self._to_decimal(parameter)
        return False

    def _round_amount(self, value):
        return self._to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def _floor_amount(self, value):
        return self._to_decimal(value).quantize(WHOLE_ZLOTY, rounding=ROUND_DOWN)

    def _to_decimal(self, value):
        return Decimal(str(value or 0.0))
