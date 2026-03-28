from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import SavepointCase


TWOPLACES = Decimal("0.01")
WHOLE_ZLOTY = Decimal("1")


@tagged("post_install", "-at_install")
class TestPayrollCumulative(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.Parameter = cls.env["pl.payroll.parameter"]
        cls.calendar = cls.env.ref("l10n_pl_payroll.demo_calendar_full_time")
        cls.contract_type = cls.env.ref("l10n_pl_payroll.demo_contract_type_umowa_o_prace")
        cls.demo_andrzej = cls.env.ref("l10n_pl_payroll.demo_employee_andrzej_dabrowski")

    def test_scenario_10_pit_bracket_transition(self):
        history_contract = self._make_contract(
            self.demo_andrzej,
            "Scenario 10 history",
            Decimal("1000.00"),
            ppk_participation="opt_out",
        )
        current_contract = self._make_contract(
            self.demo_andrzej,
            "Scenario 10 current",
            Decimal("30000.00"),
            ppk_participation="opt_out",
        )

        for month in range(1, 11):
            payslip = self._create_payslip(history_contract, 2026, month)
            payslip.write(
                {
                    "taxable_income": 10000.0,
                    "pit_advance": 1200.0,
                    "pit_reducing": 300.0,
                    "pit_due": 900.0,
                    "state": "confirmed",
                }
            )

        november = self._create_payslip(current_contract, 2026, 11)
        november.compute_payslip()

        self.assertDecimalEqual(november.taxable_income, Decimal("25637"))
        self.assertDecimalEqual(november.pit_advance, Decimal("4203.84"))
        self.assertDecimalEqual(november.pit_reducing, Decimal("300.00"))
        self.assertDecimalEqual(november.pit_due, Decimal("3903"))

    def test_cumulative_pit_matches_annual_pit_after_twelve_months(self):
        employee = self._make_employee("Roczny PIT Test")
        contract = self._make_contract(
            employee,
            "Annual PIT",
            Decimal("15000.00"),
            ppk_participation="opt_out",
        )

        total_pit_due = Decimal("0.00")
        total_taxable_income = Decimal("0.00")
        total_pit_reducing = Decimal("0.00")

        for month in range(1, 13):
            payslip = self._create_payslip(contract, 2026, month)
            payslip.compute_payslip()
            total_pit_due += self.to_decimal(payslip.pit_due)
            total_taxable_income += self.to_decimal(payslip.taxable_income)
            total_pit_reducing += self.to_decimal(payslip.pit_reducing)
            payslip.write({"state": "confirmed"})

        threshold = self.to_decimal(self.Parameter.get_value("PIT_THRESHOLD", date(2026, 12, 31)))
        expected_annual_pit = self.floor_amount(
            self._tax_on_base(total_taxable_income, threshold) - total_pit_reducing
        )

        self.assertDecimalEqual(total_pit_due, expected_annual_pit)

    def test_zus_cap_applies_partial_month_for_employee_and_employer(self):
        employee = self._make_employee("ZUS Cap Test")
        contract = self._make_contract(
            employee,
            "ZUS cap",
            Decimal("25000.00"),
            ppk_participation="opt_out",
        )

        for month in range(1, 12):
            payslip = self._create_payslip(contract, 2026, month)
            payslip.compute_payslip()
            payslip.write({"state": "confirmed"})

        december = self._create_payslip(contract, 2026, 12)
        december.compute_payslip()

        partial_basis = Decimal("7600.00")
        expected_health_basis = Decimal("25000.00") - self.percent_of(partial_basis, "ZUS_EMERY_EE") - self.percent_of(
            partial_basis,
            "ZUS_RENT_EE",
        ) - self.percent_of(Decimal("25000.00"), "ZUS_CHOR_EE")
        self.assertDecimalEqual(december.zus_emerytalne_ee, self.percent_of(partial_basis, "ZUS_EMERY_EE"))
        self.assertDecimalEqual(december.zus_rentowe_ee, self.percent_of(partial_basis, "ZUS_RENT_EE"))
        self.assertDecimalEqual(december.zus_chorobowe_ee, self.percent_of(Decimal("25000.00"), "ZUS_CHOR_EE"))
        self.assertDecimalEqual(december.health_basis, expected_health_basis)
        self.assertDecimalEqual(december.zus_emerytalne_er, self.percent_of(partial_basis, "ZUS_EMERY_ER"))
        self.assertDecimalEqual(december.zus_rentowe_er, self.percent_of(partial_basis, "ZUS_RENT_ER"))

    def test_ulga_stops_after_cumulative_gross_exceeds_limit(self):
        employee = self._make_employee("Ulga Limit Test")
        contract = self._make_contract(
            employee,
            "Ulga limit",
            Decimal("20000.00"),
            ppk_participation="opt_out",
            ulga_type="mlodzi",
        )

        june = False
        for month in range(1, 7):
            payslip = self._create_payslip(contract, 2026, month)
            payslip.compute_payslip()
            payslip.write({"state": "confirmed"})
            june = payslip

        july = self._create_payslip(contract, 2026, 7)
        july.compute_payslip()

        self.assertDecimalEqual(june.pit_due, Decimal("0"))
        self.assertGreater(july.pit_due, 0.0)
        self.assertDecimalEqual(july.pit_advance, self.to_decimal(july.taxable_income) * Decimal("0.12"))

    def _make_employee(self, name):
        return self.Employee.create(
            {
                "name": name,
                "ssnid": "99123112345",
                "birthday": "1999-12-31",
                "gender": "male",
                "country_id": self.env.ref("base.pl").id,
            }
        )

    def _make_contract(
        self,
        employee,
        name,
        wage,
        ppk_participation="default",
        ulga_type="none",
    ):
        ppk_ee_rate = 0.0 if ppk_participation == "opt_out" else 2.0
        return self.Contract.create(
            {
                "name": name,
                "employee_id": employee.id,
                "company_id": self.env.company.id,
                "date_start": date(2026, 1, 1),
                "wage": float(wage),
                "resource_calendar_id": self.calendar.id,
                "contract_type_id": self.contract_type.id,
                "kup_type": "standard",
                "kup_autorskie_pct": 0.0,
                "ppk_participation": ppk_participation,
                "ppk_ee_rate": ppk_ee_rate,
                "ppk_additional": 0.0,
                "pit2_filed": True,
                "ulga_type": ulga_type,
                "zus_code": "0110",
            }
        )

    def _create_payslip(self, contract, year, month):
        date_from = date(year, month, 1)
        date_to = date(year, month, monthrange(year, month)[1])
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": date_from,
                "date_to": date_to,
            }
        )

    def _tax_on_base(self, taxable_income, threshold):
        rate_1 = self.to_decimal(self.Parameter.get_value("PIT_RATE_1", date(2026, 12, 31)))
        rate_2 = self.to_decimal(self.Parameter.get_value("PIT_RATE_2", date(2026, 12, 31)))
        if taxable_income <= threshold:
            return self.round_amount(taxable_income * rate_1 / Decimal("100"))
        return self.round_amount(
            threshold * rate_1 / Decimal("100")
            + (taxable_income - threshold) * rate_2 / Decimal("100")
        )

    def percent_of(self, amount, code):
        value = self.Parameter.get_value(code, date(2026, 12, 31))
        return self.round_amount(amount * self.to_decimal(value) / Decimal("100"))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def floor_amount(self, value):
        return self.to_decimal(value).quantize(WHOLE_ZLOTY, rounding=ROUND_DOWN)

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
