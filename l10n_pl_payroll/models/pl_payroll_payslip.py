from datetime import date
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from odoo import _, api, fields, models
from odoo.exceptions import UserError


TWOPLACES = Decimal("0.01")
WHOLE_ZLOTY = Decimal("1")


class PlPayrollPayslip(models.Model):
    _name = "pl.payroll.payslip"
    _description = "Lista płac PL"
    _order = "date_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True, string="Nazwa")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Pracownik",
        required=True,
        help="Pracownik, dla którego naliczasz listę płac.",
    )
    department_id = fields.Many2one(
        "hr.department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
        string="Wydział",
        help="Wydział pracownika pobrany z kartoteki pracownika.",
    )
    contract_id = fields.Many2one(
        "hr.contract",
        string="Umowa",
        required=True,
        help="Aktywna umowa, z której pobierane są stawka, KUP, PPK i kod ZUS.",
    )
    kup_type = fields.Selection(
        related="contract_id.kup_type",
        readonly=True,
        string="Wariant KUP",
        help="Wariant kosztów uzyskania przychodu pobrany z umowy pracownika.",
    )
    company_id = fields.Many2one(
        "res.company",
        related="contract_id.company_id",
        store=True,
        string="Firma",
        help="Firma, w której rozliczana jest lista płac.",
    )
    date_from = fields.Date(
        string="Okres od",
        required=True,
        help="Pierwszy dzień okresu rozliczeniowego listy płac.",
    )
    date_to = fields.Date(
        string="Okres do",
        required=True,
        help="Ostatni dzień okresu rozliczeniowego listy płac.",
    )
    state = fields.Selection(
        [
            ("draft", "Szkic"),
            ("computed", "Obliczona"),
            ("confirmed", "Zatwierdzona"),
            ("cancelled", "Anulowana"),
        ],
        string="Status",
        default="draft",
        help="Status listy płac. Po zatwierdzeniu dane wchodzą do rozliczeń PIT i ZUS.",
    )

    gross = fields.Float(
        string="Wynagrodzenie brutto",
        readonly=True,
        help="Łączne brutto po doliczeniu dodatków brutto i pomniejszeniu potrąceń brutto.",
    )
    sick_days = fields.Integer(
        string="Dni choroby 80%",
        default=0,
        help="Liczba dni wynagrodzenia chorobowego płatnego w wysokości 80% podstawy.",
    )
    sick_days_100 = fields.Integer(
        string="Dni choroby 100%",
        default=0,
        help="Liczba dni choroby płatnych 100% podstawy, np. w ciąży albo po wypadku przy pracy.",
    )
    vacation_days = fields.Float(
        string="Dni urlopu",
        default=0,
        help="Liczba dni urlopu wypoczynkowego rozliczana na tej liście płac.",
    )
    vacation_pay = fields.Float(
        string="Wynagrodzenie urlopowe",
        readonly=True,
        help="Kwota wynagrodzenia za urlop obliczona z podstawy urlopowej.",
    )
    sick_leave_amount = fields.Float(
        string="Wynagrodzenie chorobowe",
        readonly=True,
        help="Kwota wynagrodzenia chorobowego naliczona za dni choroby w tym okresie.",
    )
    sick_leave_basis = fields.Float(
        string="Podstawa wynagrodzenia chorobowego",
        readonly=True,
        help="Podstawa służąca do obliczenia wynagrodzenia chorobowego.",
    )
    working_days_in_month = fields.Integer(
        string="Dni robocze w miesiącu",
        default=0,
        help="Liczba dni roboczych w miesiącu używana do proporcji. "
             "Jeżeli pole zostanie puste, system traktuje miesiąc jak pełny.",
    )
    overtime_hours_150 = fields.Float(
        string="Nadgodziny 150% (godz.)",
        help="Liczba godzin nadliczbowych rozliczanych z dodatkiem 50%.",
    )
    overtime_hours_200 = fields.Float(
        string="Nadgodziny 200% (godz.)",
        help="Liczba godzin nadliczbowych rozliczanych z dodatkiem 100%.",
    )
    overtime_amount = fields.Float(
        string="Dodatek za nadgodziny",
        readonly=True,
        help="Łączna kwota dodatków za nadgodziny naliczona na tej liście płac.",
    )
    payslip_line_ids = fields.One2many(
        "pl.payroll.payslip.line",
        "payslip_id",
        string="Składniki dodatkowe",
        help="Dodatki, premie i potrącenia uwzględnione na liście płac.",
    )
    bonus_gross_total = fields.Float(
        compute="_compute_payslip_line_totals",
        store=True,
        string="Suma dodatków brutto",
        help="Łączna kwota dodatków i premii, które zwiększają wynagrodzenie brutto.",
    )
    deduction_gross_total = fields.Float(
        compute="_compute_payslip_line_totals",
        store=True,
        string="Suma potrąceń brutto",
        help="Łączna kwota potrąceń pomniejszających wynagrodzenie brutto przed podatkiem i składkami.",
    )
    deduction_net_total = fields.Float(
        compute="_compute_payslip_line_totals",
        store=True,
        string="Suma potrąceń netto",
        help="Łączna kwota potrąceń odejmowanych już po wyliczeniu wynagrodzenia netto.",
    )

    zus_emerytalne_ee = fields.Float(
        string="Składka emerytalna (pracownik)",
        help="Składka emerytalna potrącana z wynagrodzenia pracownika.",
    )
    zus_rentowe_ee = fields.Float(
        string="Składka rentowa (pracownik)",
        help="Składka rentowa potrącana z wynagrodzenia pracownika.",
    )
    zus_chorobowe_ee = fields.Float(
        string="Składka chorobowa (pracownik)",
        help="Składka chorobowa finansowana przez pracownika.",
    )
    zus_total_ee = fields.Float(
        string="Składki ZUS pracownika razem",
        help="Suma składek społecznych finansowanych przez pracownika.",
    )

    health_basis = fields.Float(
        string="Podstawa składki zdrowotnej",
        help="Podstawa, od której nalicza się składkę zdrowotną.",
    )
    health = fields.Float(
        string="Składka zdrowotna",
        help="Składka zdrowotna pobierana z wynagrodzenia pracownika.",
    )

    kup_amount = fields.Float(
        string="Koszty uzyskania przychodu",
        help="Koszty uzyskania przychodu uwzględnione przy obliczeniu zaliczki PIT.",
    )

    taxable_income = fields.Float(
        string="Dochód do opodatkowania",
        help="Dochód po składkach i kosztach uzyskania przychodu, który podlega PIT.",
    )
    pit_advance = fields.Float(
        string="Naliczona zaliczka PIT",
        help="Kwota podatku wyliczona według skali przed końcowym rozliczeniem zaliczki za miesiąc.",
    )
    pit_reducing = fields.Float(
        string="Kwota zmniejszająca podatek",
        help="Miesięczna kwota obniżająca zaliczkę PIT po złożeniu PIT-2.",
    )
    pit_due = fields.Float(
        string="Zaliczka PIT do urzędu",
        help="Końcowa zaliczka PIT do odprowadzenia za ten miesiąc po zastosowaniu ulg i zaokrągleń.",
    )

    ppk_ee = fields.Float(
        string="Wpłata PPK pracownika",
        help="Wpłata finansowana przez pracownika w ramach PPK.",
    )

    net = fields.Float(
        string="Wynagrodzenie netto",
        help="Kwota do wypłaty pracownikowi po wszystkich potrąceniach.",
    )

    zus_emerytalne_er = fields.Float(
        string="Składka emerytalna (pracodawca)",
        help="Składka emerytalna finansowana przez pracodawcę.",
    )
    zus_rentowe_er = fields.Float(
        string="Składka rentowa (pracodawca)",
        help="Składka rentowa finansowana przez pracodawcę.",
    )
    zus_wypadkowe_er = fields.Float(
        string="Składka wypadkowa",
        help="Składka wypadkowa finansowana przez pracodawcę według stopy firmy.",
    )
    zus_fp = fields.Float(
        string="Składka na Fundusz Pracy",
        help="Składka na Fundusz Pracy finansowana przez pracodawcę.",
    )
    zus_fgsp = fields.Float(
        string="Składka na FGŚP",
        help="Składka na Fundusz Gwarantowanych Świadczeń Pracowniczych finansowana przez pracodawcę.",
    )
    ppk_er = fields.Float(
        string="Wpłata PPK pracodawcy",
        help="Wpłata PPK finansowana przez pracodawcę. Dla pracownika stanowi przychód do PIT.",
    )
    total_employer_cost = fields.Float(
        string="Łączny koszt pracodawcy",
        help="Pełny koszt zatrudnienia: brutto plus składki i wpłaty finansowane przez pracodawcę.",
    )

    creative_report_id = fields.Many2one(
        "pl.payroll.creative.report",
        string="Zatwierdzony raport twórczy",
        readonly=True,
        help="Raport pracy twórczej przypięty do tej listy płac.",
    )
    creative_report_required = fields.Boolean(
        compute="_compute_creative_report_flags",
        string="Wymaga raportu twórczego",
        help="Pole informacyjne. Pokazuje, że dla tej listy płac trzeba dołączyć "
             "zatwierdzony raport pracy twórczej, aby rozliczyć 50% KUP autorskie.",
    )
    creative_report_missing = fields.Boolean(
        compute="_compute_creative_report_flags",
        string="Brakuje raportu twórczego",
        help="Pole ostrzegawcze. Informuje, że lista płac korzysta z pracy twórczej, "
             "ale nie ma jeszcze podpiętego zatwierdzonego raportu.",
    )
    etat_fraction = fields.Float(
        compute="_compute_etat_fraction",
        store=True,
        string="Wymiar etatu",
        help="Udział etatu obliczony na podstawie kalendarza czasu pracy.",
    )
    below_minimum_wage = fields.Boolean(
        compute="_compute_minimum_wage_warning",
        store=True,
        string="Poniżej minimalnego wynagrodzenia",
        help="Pole ostrzegawcze. Pokazuje, że brutto na tej liście płac jest niższe "
             "od minimalnego wynagrodzenia wyliczonego dla danego wymiaru etatu.",
    )
    ytd_sick_days = fields.Integer(
        compute="_compute_ytd_sick_days",
        string="Dni choroby od początku roku",
        help="Łączna liczba dni choroby wykorzystanych od początku roku do tej listy płac.",
    )

    notes = fields.Text(
        string="Uwagi do listy płac",
        help="Dodatkowe notatki księgowe albo kadrowe do tej listy płac.",
    )

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
        vacation_supplement, _base_gross = self._compute_vacation_pay(base_gross)
        bonus_gross_total = self._to_decimal(self.bonus_gross_total)
        deduction_gross_total = self._to_decimal(self.deduction_gross_total)
        deduction_net_total = self._to_decimal(self.deduction_net_total)
        gross = self._round_amount(
            base_gross + overtime_amount + vacation_supplement + bonus_gross_total - deduction_gross_total
        )

        if self._is_dzielo_contract():
            if gross <= Decimal("200.00"):
                kup_amount = Decimal("0.00")
                taxable_income = gross
                pit_rate = self._get_parameter("DZIELO_PIT_RATE")
                pit_advance = self._round_amount(taxable_income * pit_rate / Decimal("100"))
            else:
                if self.contract_id.kup_type == "autorskie":
                    kup_rate = self._get_parameter("KUP_AUTORSKIE_50_RATE")
                    kup_amount = self._round_amount(gross * kup_rate / Decimal("100"))
                else:
                    kup_rate = self._get_parameter("KUP_STANDARD_20_RATE")
                    kup_amount = self._round_amount(gross * kup_rate / Decimal("100"))
                taxable_income = self._floor_amount(gross - kup_amount)
                pit_rate = self._get_parameter("DZIELO_PIT_RATE")
                pit_advance = self._round_amount(taxable_income * pit_rate / Decimal("100"))

            pit_due = self._floor_amount(pit_advance)
            net_before_deductions = self._round_amount(gross - pit_due)
            net = self._round_amount(net_before_deductions - deduction_net_total)
            self.write(
                {
                    "gross": float(gross),
                    "sick_leave_amount": 0.0,
                    "sick_leave_basis": 0.0,
                    "vacation_pay": 0.0,
                    "overtime_amount": float(overtime_amount),
                    "zus_emerytalne_ee": 0.0,
                    "zus_rentowe_ee": 0.0,
                    "zus_chorobowe_ee": 0.0,
                    "zus_total_ee": 0.0,
                    "health_basis": 0.0,
                    "health": 0.0,
                    "kup_amount": float(kup_amount),
                    "taxable_income": float(taxable_income),
                    "pit_advance": float(pit_advance),
                    "pit_reducing": 0.0,
                    "pit_due": float(pit_due),
                    "ppk_ee": 0.0,
                    "net": float(net),
                    "zus_emerytalne_er": 0.0,
                    "zus_rentowe_er": 0.0,
                    "zus_wypadkowe_er": 0.0,
                    "zus_fp": 0.0,
                    "zus_fgsp": 0.0,
                    "ppk_er": 0.0,
                    "total_employer_cost": float(gross),
                    "state": "computed",
                }
            )
            return

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

        health_basis_raw = self._round_amount(adjusted_gross - zus_total_ee + sick_amount)
        health_basis = health_basis_raw
        if student_zlecenie_exempt:
            health = Decimal("0.00")
            ppk_er = Decimal("0.00")
        else:
            minimum_health_basis = self._get_minimum_health_basis()
            if health_basis < minimum_health_basis:
                health_basis = minimum_health_basis
            health = self._round_amount(health_basis * self._get_parameter("HEALTH") / Decimal("100"))
            ppk_er = self._compute_ppk_employer(adjusted_gross)
        kup_amount = self._compute_kup_amount(health_basis_raw)
        taxable_income = self._floor_amount(health_basis_raw - kup_amount + ppk_er)
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
                "vacation_pay": float(vacation_supplement),
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

    def _compute_vacation_pay(self, base_gross):
        self.ensure_one()
        if self._is_mandate_contract() or self._is_dzielo_contract():
            return Decimal("0.00"), base_gross

        vacation_days = self._to_decimal(self.vacation_days)
        if vacation_days <= Decimal("0.00"):
            return Decimal("0.00"), base_gross

        prior_payslips = self.search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "=", "confirmed"),
                ("date_from", "<", self.date_from),
            ],
            order="date_from desc, id desc",
            limit=3,
        )
        if not prior_payslips:
            return Decimal("0.00"), base_gross

        total_variable = Decimal("0.00")
        total_hours_worked = Decimal("0.00")
        standard_hours = self._get_parameter("STANDARD_MONTHLY_HOURS")

        for payslip in prior_payslips:
            variable_amount = (
                self._to_decimal(payslip.overtime_amount)
                + self._to_decimal(payslip.bonus_gross_total)
            )
            total_variable += variable_amount
            total_hours_worked += standard_hours * payslip._get_etat_fraction()

        if total_variable <= Decimal("0.00") or total_hours_worked <= Decimal("0.00"):
            return Decimal("0.00"), base_gross

        day_hours = Decimal("8.00") * self._get_etat_fraction()
        vacation_hours = vacation_days * day_hours
        supplement = self._round_amount(total_variable / total_hours_worked * vacation_hours)
        return supplement, base_gross

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
            raise UserError(_("Parametr STANDARD_MONTHLY_HOURS musi mieć wartość większą od zera."))

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

    def _get_minimum_health_basis(self):
        self.ensure_one()
        minimum_wage = self._get_minimum_wage_parameter()
        if minimum_wage is False:
            return Decimal("0.00")
        minimum_gross = self._round_amount(minimum_wage * self._get_etat_fraction())
        zus_rate = (
            self._get_parameter("ZUS_EMERY_EE")
            + self._get_parameter("ZUS_RENT_EE")
            + self._get_parameter("ZUS_CHOR_EE")
        ) / Decimal("100")
        return self._round_amount(minimum_gross * (Decimal("1") - zus_rate))

    def _compute_kup_amount(self, health_basis):
        self.ensure_one()
        if self.contract_id.kup_type == "autorskie":
            creative_share = self._to_decimal(self.contract_id.kup_autorskie_pct) / Decimal("100")
            kup_rate = self._get_parameter("KUP_AUTORSKIE_50_RATE")
            return self._round_amount(health_basis * creative_share * kup_rate / Decimal("100"))
        if self.contract_id.kup_type == "standard_20":
            kup_rate = self._get_parameter("KUP_STANDARD_20_RATE")
            return self._round_amount(health_basis * kup_rate / Decimal("100"))
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

    def _is_dzielo_contract(self):
        self.ensure_one()
        contract_type_name = (self.contract_id.contract_type_id.name or "").strip().lower()
        return contract_type_name == "umowa o dzieło"

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
            raise UserError(_("Brakuje parametru płacowego: %s") % code)
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
