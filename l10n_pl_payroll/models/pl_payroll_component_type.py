from odoo import fields, models


class PlPayrollComponentType(models.Model):
    _name = "pl.payroll.component.type"
    _description = "Typ składnika wynagrodzenia"
    _order = "sequence, name"

    name = fields.Char(
        string="Nazwa",
        required=True,
    )
    code = fields.Char(
        string="Kod",
        required=True,
    )
    sequence = fields.Integer(
        string="Kolejność",
        default=10,
    )
    active = fields.Boolean(
        string="Aktywny",
        default=True,
    )

    category = fields.Selection(
        [
            ("bonus_gross", "Dodatek brutto"),
            ("deduction_gross", "Potrącenie brutto"),
            ("benefit_in_kind", "Świadczenie rzeczowe"),
            ("deduction_net", "Potrącenie netto"),
        ],
        string="Kategoria",
        required=True,
    )

    pit_taxable = fields.Boolean(
        string="Podlega PIT",
        default=True,
        help="Czy wartość tego składnika wchodzi do podstawy opodatkowania PIT?",
    )
    pit_exempt_article = fields.Char(
        string="Podstawa prawna zwolnienia PIT",
        help="Np. 'art. 21 ust. 1 pkt 11 ustawy o PIT'",
    )

    zus_included = fields.Boolean(
        string="Podlega składkom ZUS",
        default=True,
        help="Czy wartość tego składnika wchodzi do podstawy wymiaru składek ZUS?",
    )
    zus_exempt_limit = fields.Float(
        string="Limit zwolnienia ZUS (PLN/mies.)",
        default=0.0,
        help="Kwota zwolniona ze składek ZUS miesięcznie. 0 = brak limitu (pełne zwolnienie jeśli zus_included=False).",
    )
    zus_exempt_article = fields.Char(
        string="Podstawa prawna zwolnienia ZUS",
        help="Np. '§ 2 ust. 1 pkt 11 rozp. składkowego'",
    )

    default_amount = fields.Float(
        string="Domyślna kwota",
        help="Podpowiadana kwota przy dodawaniu składnika do listy płac.",
    )
    requires_documentation = fields.Boolean(
        string="Wymaga dokumentacji",
        help="Np. ekwiwalent za pranie wymaga kalkulacji kosztów rzeczywistych.",
    )
    documentation_hint = fields.Char(
        string="Podpowiedź dokumentacji",
        help="Wyświetlana jako hint w polu 'note' na linii payslip.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        default=lambda self: self.env.company,
        help="Puste = dostępny dla wszystkich firm.",
    )

    note = fields.Text(
        string="Opis / uwagi prawne",
    )

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique(code, company_id)",
            "Kod składnika musi być unikalny w ramach firmy.",
        ),
    ]
