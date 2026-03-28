from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from odoo.tests import tagged
from odoo.tests.common import SavepointCase

from .test_fixtures import EXPECTED_RESULTS, SCENARIO_XMLIDS


TWOPLACES = Decimal("0.01")


@tagged("post_install", "-at_install")
class TestPayrollPayslip(SavepointCase):
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

    def _create_payslip(self, contract):
        target_date = date(2026, 1, 1)
        return self.Payslip.create(
            {
                "employee_id": contract.employee_id.id,
                "contract_id": contract.id,
                "date_from": target_date.replace(day=1),
                "date_to": target_date.replace(day=monthrange(target_date.year, target_date.month)[1]),
            }
        )

    def percent_of(self, amount, code, target_date, company_id=False):
        value = self.Parameter.get_value(code, target_date, company_id.id if company_id else False)
        return self.round_amount(amount * self.to_decimal(value) / Decimal("100"))

    def round_amount(self, value):
        return self.to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def to_decimal(self, value):
        return Decimal(str(value or 0.0))

    def assertDecimalEqual(self, actual, expected):
        self.assertEqual(self.round_amount(actual), self.round_amount(expected))
