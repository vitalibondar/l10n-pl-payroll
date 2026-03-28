from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from .test_fixtures import EXPECTED_RESULTS, SCENARIO_XMLIDS


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestPayrollPayslip(TransactionCase):
    SUPPORTED_SCENARIOS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Parameter = cls.env["pl.payroll.parameter"]
        cls.Payslip = cls.env["pl.payroll.payslip"]
        cls.scenarios = {
            number: (cls.env.ref(employee_xmlid), cls.env.ref(contract_xmlid))
            for number, (employee_xmlid, contract_xmlid) in SCENARIO_XMLIDS.items()
        }

    def test_compute_payslip_for_supported_scenarios(self):
        field_map = {
            "gross": "gross",
            "zus_emerytalne_ee": "zus_emerytalne_ee",
            "zus_rentowe_ee": "zus_rentowe_ee",
            "zus_chorobowe_ee": "zus_chorobowe_ee",
            "health_basis": "health_basis",
            "health": "health",
            "kup_amount": "kup_amount",
            "taxable_income": "taxable_income_rounded",
            "pit_advance": "pit_advance",
            "pit_reducing": "pit_reducing_amount",
            "pit_due": "pit_due",
            "ppk_ee": "ppk_ee",
            "net": "net",
        }
        for scenario_number in self.SUPPORTED_SCENARIOS:
            with self.subTest(scenario=scenario_number):
                _employee, contract = self.scenarios[scenario_number]
                expected = EXPECTED_RESULTS[scenario_number]

                payslip = self._create_payslip(contract)
                payslip.compute_payslip()

                self.assertEqual(payslip.state, "computed")
                for field_name, expected_key in field_map.items():
                    self.assertDecimalEqual(
                        getattr(payslip, field_name),
                        expected.get(expected_key, Decimal("0.00")),
                    )

                self.assertDecimalEqual(
                    payslip.zus_total_ee,
                    expected["zus_emerytalne_ee"]
                    + expected["zus_rentowe_ee"]
                    + expected["zus_chorobowe_ee"],
                )

    def test_compute_employer_side_contributions(self):
        for scenario_number in self.SUPPORTED_SCENARIOS:
            with self.subTest(scenario=scenario_number):
                _employee, contract = self.scenarios[scenario_number]
                payslip = self._create_payslip(contract)
                payslip.compute_payslip()

                gross = self.to_decimal(contract.wage)
                ppk_er = Decimal("0.00")
                if contract.ppk_participation != "opt_out":
                    ppk_er = self.percent_of(gross, "PPK_ER", payslip.date_to, contract.company_id)

                self.assertDecimalEqual(
                    payslip.zus_emerytalne_er,
                    self.percent_of(gross, "ZUS_EMERY_ER", payslip.date_to),
                )
                self.assertDecimalEqual(
                    payslip.zus_rentowe_er,
                    self.percent_of(gross, "ZUS_RENT_ER", payslip.date_to),
                )
                self.assertDecimalEqual(
                    payslip.zus_wypadkowe_er,
                    self.percent_of(gross, "ZUS_WYPAD_ER", payslip.date_to, contract.company_id),
                )
                self.assertDecimalEqual(
                    payslip.zus_fp,
                    self.percent_of(gross, "ZUS_FP", payslip.date_to),
                )
                self.assertDecimalEqual(
                    payslip.zus_fgsp,
                    self.percent_of(gross, "ZUS_FGSP", payslip.date_to),
                )
                self.assertDecimalEqual(payslip.ppk_er, ppk_er)
                self.assertDecimalEqual(
                    payslip.total_employer_cost,
                    gross
                    + self.to_decimal(payslip.zus_emerytalne_er)
                    + self.to_decimal(payslip.zus_rentowe_er)
                    + self.to_decimal(payslip.zus_wypadkowe_er)
                    + self.to_decimal(payslip.zus_fp)
                    + self.to_decimal(payslip.zus_fgsp)
                    + self.to_decimal(payslip.ppk_er),
                )

    def test_gross_is_snapshotted_after_compute(self):
        _employee, contract = self.scenarios[1]
        original_wage = contract.wage
        payslip = self._create_payslip(contract)

        payslip.compute_payslip()
        payslip.action_confirm()
        contract.write({"wage": original_wage + 500.0})

        self.assertEqual(payslip.state, "confirmed")
        self.assertDecimalEqual(payslip.gross, original_wage)

    def test_compute_overtime_150_percent(self):
        _employee, contract = self.scenarios[1]
        payslip = self._create_payslip(contract, overtime_hours_150=10.0)

        payslip.compute_payslip()
        expected = self._expected_amounts_with_overtime(contract, payslip.date_to, overtime_hours_150=Decimal("10.0"))

        self.assertEqual(payslip.state, "computed")
        self.assertDecimalEqual(payslip.overtime_amount, expected["overtime_amount"])
        self.assertDecimalEqual(payslip.gross, expected["gross"])
        self.assertDecimalEqual(payslip.net, expected["net"])

    def test_compute_overtime_200_percent(self):
        _employee, contract = self.scenarios[1]
        payslip = self._create_payslip(contract, overtime_hours_200=5.0)

        payslip.compute_payslip()
        expected = self._expected_amounts_with_overtime(contract, payslip.date_to, overtime_hours_200=Decimal("5.0"))

        self.assertEqual(payslip.state, "computed")
        self.assertDecimalEqual(payslip.overtime_amount, expected["overtime_amount"])
        self.assertDecimalEqual(payslip.gross, expected["gross"])
        self.assertDecimalEqual(payslip.net, expected["net"])

    def _create_payslip(self, contract, overtime_hours_150=0.0, overtime_hours_200=0.0):
        target_date = date(2026, 1, 1)
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": target_date.replace(day=1),
                "date_to": target_date.replace(day=monthrange(target_date.year, target_date.month)[1]),
                "overtime_hours_150": overtime_hours_150,
                "overtime_hours_200": overtime_hours_200,
            }
        )

    def _expected_amounts_with_overtime(
        self,
        contract,
        target_date,
        overtime_hours_150=Decimal("0.0"),
        overtime_hours_200=Decimal("0.0"),
    ):
        base_gross = self.to_decimal(contract.wage)
        standard_monthly_hours = self.to_decimal(self.Parameter.get_value("STANDARD_MONTHLY_HOURS", target_date))
        hourly_rate = base_gross / standard_monthly_hours
        overtime_amount = self.round_amount(
            overtime_hours_150 * hourly_rate * Decimal("1.5")
            + overtime_hours_200 * hourly_rate * Decimal("2.0")
        )
        gross = self.round_amount(base_gross + overtime_amount)

        zus_emerytalne_ee = self.percent_of(gross, "ZUS_EMERY_EE", target_date)
        zus_rentowe_ee = self.percent_of(gross, "ZUS_RENT_EE", target_date)
        zus_chorobowe_ee = self.percent_of(gross, "ZUS_CHOR_EE", target_date)
        zus_total_ee = self.round_amount(zus_emerytalne_ee + zus_rentowe_ee + zus_chorobowe_ee)
        health_basis = self.round_amount(gross - zus_total_ee)
        health_rate = self.to_decimal(self.Parameter.get_value("HEALTH", target_date))
        health = self.round_amount(health_basis * health_rate / Decimal("100"))

        kup_amount = self.to_decimal(self.Parameter.get_value("KUP_STANDARD", target_date))
        ppk_er = self.round_amount(gross * self.to_decimal(self.Parameter.get_value("PPK_ER", target_date)) / Decimal("100"))
        taxable_income = self.to_decimal(health_basis - kup_amount + ppk_er).quantize(Decimal("1"), rounding=ROUND_DOWN)
        pit_rate = self.to_decimal(self.Parameter.get_value("PIT_RATE_1", target_date))
        pit_advance = self.round_amount(taxable_income * pit_rate / Decimal("100"))
        pit_reducing = Decimal("0.00")
        if contract.pit2_filed and contract.contract_type_id.name.strip().lower() != "umowa zlecenie":
            pit_reducing = self.round_amount(self.Parameter.get_value("PIT_REDUCING", target_date))
        pit_due = max(Decimal("0.00"), pit_advance - pit_reducing).quantize(Decimal("1"), rounding=ROUND_DOWN)

        ppk_ee_rate = self.to_decimal(contract.ppk_ee_rate) + self.to_decimal(contract.ppk_additional)
        ppk_ee = self.round_amount(gross * ppk_ee_rate / Decimal("100"))
        net = self.round_amount(gross - zus_total_ee - health - pit_due - ppk_ee)

        return {
            "overtime_amount": overtime_amount,
            "gross": gross,
            "net": net,
        }

    def percent_of(self, amount, code, target_date, company_id=False):
        value = self.Parameter.get_value(code, target_date, company_id.id if company_id else False)
        return self.round_amount(amount * self.to_decimal(value) / Decimal("100"))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
