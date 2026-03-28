# ⚠️ FICTIONAL TEST DATA — nie są to dane prawdziwych osób.
# Generated for testing purposes only. PESEL numbers have invalid checksums.

import importlib.util
from decimal import Decimal
from pathlib import Path

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_RESULTS_PATH = REPO_ROOT / "tools" / "expected_results.py"
SCENARIO_XMLIDS = {
    1: ("l10n_pl_payroll.demo_employee_jan_kowalski", "l10n_pl_payroll.demo_contract_jan_kowalski"),
    2: ("l10n_pl_payroll.demo_employee_anna_nowak", "l10n_pl_payroll.demo_contract_anna_nowak"),
    3: ("l10n_pl_payroll.demo_employee_piotr_wisniewski", "l10n_pl_payroll.demo_contract_piotr_wisniewski"),
    4: ("l10n_pl_payroll.demo_employee_maria_wojcik", "l10n_pl_payroll.demo_contract_maria_wojcik"),
    5: ("l10n_pl_payroll.demo_employee_jakub_kaminski", "l10n_pl_payroll.demo_contract_jakub_kaminski"),
    6: ("l10n_pl_payroll.demo_employee_oleg_shevchenko", "l10n_pl_payroll.demo_contract_oleg_shevchenko"),
    7: (
        "l10n_pl_payroll.demo_employee_katarzyna_lewandowska",
        "l10n_pl_payroll.demo_contract_katarzyna_lewandowska",
    ),
    8: (
        "l10n_pl_payroll.demo_employee_tomasz_zielinski",
        "l10n_pl_payroll.demo_contract_tomasz_zielinski",
    ),
    9: (
        "l10n_pl_payroll.demo_employee_natalia_kravchuk",
        "l10n_pl_payroll.demo_contract_natalia_kravchuk",
    ),
    10: (
        "l10n_pl_payroll.demo_employee_andrzej_dabrowski",
        "l10n_pl_payroll.demo_contract_andrzej_dabrowski",
    ),
    11: ("l10n_pl_payroll.demo_employee_ewa_majewska", "l10n_pl_payroll.demo_contract_ewa_majewska"),
    12: (
        "l10n_pl_payroll.demo_employee_olena_bondarenko",
        "l10n_pl_payroll.demo_contract_olena_bondarenko",
    ),
}


def _load_expected_results():
    spec = importlib.util.spec_from_file_location("task004_expected_results", EXPECTED_RESULTS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EXPECTED_RESULTS


def _pesel_checksum(first_ten_digits):
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    total = sum(int(digit) * weight for digit, weight in zip(first_ten_digits, weights))
    return (10 - total % 10) % 10


EXPECTED_RESULTS = _load_expected_results()


@tagged("post_install", "-at_install")
class TestPayrollFixtures(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scenarios = {
            number: (cls.env.ref(employee_xmlid), cls.env.ref(contract_xmlid))
            for number, (employee_xmlid, contract_xmlid) in SCENARIO_XMLIDS.items()
        }

    def test_demo_data_covers_twelve_scenarios(self):
        self.assertEqual(len(self.scenarios), 12)
        self.assertEqual(len(EXPECTED_RESULTS), 12)

    def test_invalid_pesel_checksum_for_all_demo_employees(self):
        for employee, _contract in self.scenarios.values():
            self.assertTrue(employee.ssnid)
            self.assertEqual(len(employee.ssnid), 11)
            self.assertNotEqual(_pesel_checksum(employee.ssnid[:10]), int(employee.ssnid[-1]))

    def test_contract_fields_match_key_scenarios(self):
        contract_1 = self.scenarios[1][1]
        self.assertEqual(contract_1.kup_type, "standard")
        self.assertEqual(contract_1.ppk_participation, "default")
        self.assertEqual(contract_1.ppk_ee_rate, 2.0)
        self.assertTrue(contract_1.pit2_filed)
        self.assertEqual(contract_1.ulga_type, "none")

        contract_5 = self.scenarios[5][1]
        self.assertEqual(contract_5.resource_calendar_id, self.env.ref("l10n_pl_payroll.demo_calendar_half_time"))

        contract_8 = self.scenarios[8][1]
        self.assertEqual(contract_8.contract_type_id, self.env.ref("l10n_pl_payroll.demo_contract_type_umowa_zlecenie"))
        self.assertEqual(contract_8.kup_type, "standard_20")
        self.assertEqual(contract_8.ppk_participation, "opt_out")

        contract_12 = self.scenarios[12][1]
        self.assertEqual(contract_12.kup_type, "autorskie")
        self.assertEqual(contract_12.kup_autorskie_pct, 80.0)
        self.assertEqual(contract_12.ulga_type, "na_powrot")

    def test_expected_results_cover_manual_checks(self):
        self.assertEqual(EXPECTED_RESULTS[1]["net"], EXPECTED_RESULTS[1]["gross"] - EXPECTED_RESULTS[1]["zus_emerytalne_ee"] - EXPECTED_RESULTS[1]["zus_rentowe_ee"] - EXPECTED_RESULTS[1]["zus_chorobowe_ee"] - EXPECTED_RESULTS[1]["health"] - EXPECTED_RESULTS[1]["pit_due"] - EXPECTED_RESULTS[1]["ppk_ee"])
        self.assertEqual(EXPECTED_RESULTS[2]["pit_due"], Decimal("891"))
        self.assertEqual(float(EXPECTED_RESULTS[4]["gross"]), self.scenarios[4][1].wage)
        self.assertEqual(EXPECTED_RESULTS[8]["hours"], Decimal("160.00"))
        self.assertEqual(EXPECTED_RESULTS[10]["pit_second_bracket_part"], EXPECTED_RESULTS[10]["taxable_income_rounded"] - EXPECTED_RESULTS[10]["pit_first_bracket_part"])
