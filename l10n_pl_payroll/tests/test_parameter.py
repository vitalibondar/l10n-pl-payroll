from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPayrollParameter(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Parameter = self.env["pl.payroll.parameter"]

    def test_get_value_for_2025(self):
        self.Parameter.create(
            {
                "name": "ZUS emerytalne employee 2025",
                "code": "ZUS_EMERY_EE",
                "value": 9.76,
                "date_from": date(2025, 1, 1),
                "date_to": date(2025, 12, 31),
                "value_type": "percent",
            }
        )

        value = self.Parameter.get_value("ZUS_EMERY_EE", date(2025, 6, 1))

        self.assertEqual(value, 9.76)

    def test_get_value_for_2026(self):
        self.Parameter.create(
            {
                "name": "Minimalne wynagrodzenie 2026",
                "code": "MIN_WAGE",
                "value": 4806,
                "date_from": date(2026, 1, 1),
                "value_type": "amount",
            }
        )

        value = self.Parameter.get_value("MIN_WAGE", date(2026, 1, 1))

        self.assertEqual(value, 4806)

    def test_get_value_for_basis_cap(self):
        self.Parameter.create(
            {
                "name": "ZUS basis cap 2025",
                "code": "ZUS_BASIS_CAP",
                "value": 260190,
                "date_from": date(2025, 1, 1),
                "date_to": date(2025, 12, 31),
                "value_type": "amount",
            }
        )

        value = self.Parameter.get_value("ZUS_BASIS_CAP", date(2025, 12, 31))

        self.assertEqual(value, 260190)

    def test_overlap_is_blocked(self):
        self.Parameter.create(
            {
                "name": "PIT threshold 2025",
                "code": "PIT_THRESHOLD",
                "value": 120000,
                "date_from": date(2025, 1, 1),
                "date_to": date(2025, 12, 31),
                "value_type": "amount",
            }
        )

        with self.assertRaises(ValidationError):
            self.Parameter.create(
                {
                    "name": "PIT threshold overlapping",
                    "code": "PIT_THRESHOLD",
                    "value": 120000,
                    "date_from": date(2025, 6, 1),
                    "date_to": date(2026, 5, 31),
                    "value_type": "amount",
                }
            )

    def test_company_specific_value_falls_back_to_global(self):
        company = self.env.company
        self.Parameter.create(
            {
                "name": "Default wypadkowe",
                "code": "ZUS_WYPAD_ER",
                "value": 1.67,
                "date_from": date(2026, 1, 1),
                "value_type": "percent",
            }
        )

        value = self.Parameter.get_value("ZUS_WYPAD_ER", date(2026, 3, 1), company.id)

        self.assertEqual(value, 1.67)
