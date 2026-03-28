# ⚠️ FICTIONAL TEST DATA — nie sa to dane prawdziwych osob.
# Generated for testing purposes only. PESEL numbers have invalid checksums.

from pathlib import Path
import runpy

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


TOOLS_NS = runpy.run_path(
    str(Path(__file__).resolve().parents[2] / "tools" / "test_data_gen.py")
)


@tagged("post_install", "-at_install")
class TestPayrollFixtures(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.ContractType = cls.env["hr.contract.type"]
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.scenarios = TOOLS_NS["build_scenarios"]()
        cls.contract_types = {
            "l10n_pl_payroll_demo_contract_type_uop": cls._get_or_create_contract_type(
                "Umowa o prace"
            ),
            "l10n_pl_payroll_demo_contract_type_uz": cls._get_or_create_contract_type(
                "Umowa zlecenie"
            ),
        }
        cls.records = {}
        for scenario in cls.scenarios:
            employee = cls._create_employee(scenario["employee"])
            contract = cls._create_contract(scenario["contract"], employee)
            cls.records[scenario["scenario_no"]] = {
                "employee": employee,
                "contract": contract,
                "scenario": scenario,
            }

    @classmethod
    def _get_or_create_contract_type(cls, name):
        contract_type = cls.ContractType.search([("name", "=", name)], limit=1)
        if contract_type:
            return contract_type
        return cls.ContractType.create({"name": name})

    @classmethod
    def _supported_vals(cls, model, values):
        return {key: value for key, value in values.items() if key in model._fields}

    @classmethod
    def _create_employee(cls, payload):
        country = cls.env.ref(payload["country_xmlid"])
        values = cls._supported_vals(
            cls.Employee,
            {
                "name": payload["name"],
                "ssnid": payload["pesel"],
                "birthday": payload["birthday"],
                "gender": payload["gender"],
                "country_id": country.id,
                "street": payload["street"],
                "city": payload["city"],
                "zip": payload["zip"],
                "company_id": cls.env.company.id,
                "work_email": payload["name"].lower().replace(" ", ".") + "@fiction.example",
            },
        )
        return cls.Employee.create(values)

    @classmethod
    def _create_contract(cls, payload, employee):
        contract_type = cls.contract_types[payload["contract_type_xmlid"]]
        values = cls._supported_vals(
            cls.Contract,
            {
                "name": payload["name"],
                "employee_id": employee.id,
                "company_id": cls.env.company.id,
                "contract_type_id": contract_type.id,
                "date_start": payload["date_start"],
                "resource_calendar_id": cls.calendar.id,
                "wage": payload["wage"],
                "kup_type": payload["kup_type"],
                "kup_autorskie_pct": payload["kup_autorskie_pct"],
                "ppk_participation": payload["ppk_participation"],
                "ppk_ee_rate": payload["ppk_ee_rate"],
                "ppk_additional": payload["ppk_additional"],
                "pit2_filed": payload["pit2_filed"],
                "ulga_type": payload["ulga_type"],
                "zus_code": payload["zus_code"],
            },
        )
        return cls.Contract.create(values)

    def test_generator_builds_twelve_scenarios(self):
        self.assertEqual(len(self.scenarios), 12)
        self.assertEqual(sorted(self.records), list(range(1, 13)))

    def test_generated_pesels_have_invalid_checksum(self):
        validate_checksum = TOOLS_NS["validate_pesel_checksum"]

        for scenario in self.scenarios:
            pesel = scenario["employee"]["pesel"]
            self.assertEqual(len(pesel), 11)
            self.assertTrue(pesel.isdigit())
            self.assertFalse(validate_checksum(pesel))

    def test_contract_custom_fields_are_loaded(self):
        anna_contract = self.records[2]["contract"]
        tomasz_contract = self.records[8]["contract"]
        olena_contract = self.records[12]["contract"]

        self.assertEqual(anna_contract.kup_type, "autorskie")
        self.assertEqual(anna_contract.kup_autorskie_pct, 50.0)
        self.assertEqual(tomasz_contract.kup_type, "standard_20")
        self.assertFalse(tomasz_contract.pit2_filed)
        self.assertEqual(olena_contract.ulga_type, "na_powrot")
        self.assertEqual(olena_contract.ppk_ee_rate, 2.0)
