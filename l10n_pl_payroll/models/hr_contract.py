from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    kup_type = fields.Selection(
        [
            ("standard", "Pracownicze KUP 250,00 zł"),
            ("standard_20", "KUP 20% dla umów cywilnoprawnych"),
            ("autorskie", "KUP autorskie 50%"),
        ],
        string="Koszty uzyskania przychodu",
        default="standard",
        help="Wybierz sposób naliczania kosztów uzyskania przychodu dla tej umowy. "
             "To ustawienie wpływa na podstawę opodatkowania PIT.",
    )
    kup_autorskie_pct = fields.Float(
        string="Udział pracy twórczej (%)",
        default=0.0,
        help="Procent wynagrodzenia przypisany do pracy twórczej. "
             "Dla tej części stosuje się 50% kosztów autorskich. "
             "To nie jest stawka KUP, tylko udział pracy twórczej.",
    )
    ppk_participation = fields.Selection(
        [
            ("default", "PPK standard"),
            ("opt_out", "Rezygnacja z PPK"),
            ("reduced", "PPK obniżone"),
            ("additional", "PPK z wpłatą dodatkową"),
        ],
        string="Wariant PPK",
        default="default",
        help="Określa, czy pracownik uczestniczy w PPK i według jakiego wariantu "
             "naliczać wpłaty po stronie pracownika.",
    )
    ppk_ee_rate = fields.Float(
        string="Wpłata pracownika do PPK (%)",
        default=2.0,
        help="Podstawowa albo obniżona wpłata finansowana przez pracownika. "
             "Typowo 2,00% albo 0,50% podstawy PPK.",
    )
    ppk_additional = fields.Float(
        string="Wpłata dodatkowa pracownika do PPK (%)",
        default=0.0,
        help="Dobrowolna dodatkowa wpłata pracownika do PPK ponad wpłatę podstawową.",
    )
    pit2_filed = fields.Boolean(
        string="Złożono PIT-2",
        default=True,
        help="Jeżeli pracownik złożył PIT-2, przy obliczaniu zaliczki PIT można "
             "zastosować miesięczną kwotę zmniejszającą podatek.",
    )
    ulga_type = fields.Selection(
        [
            ("none", "Brak"),
            ("mlodzi", "Ulga dla młodych"),
            ("na_powrot", "Ulga na powrót"),
            ("rodzina_4_plus", "Ulga dla rodzin 4+"),
            ("senior", "Ulga dla seniorów"),
        ],
        string="Ulga podatkowa",
        default="none",
        help="Wskaż ulgę podatkową, która wyłącza przychód z opodatkowania PIT "
             "do ustawowego limitu rocznego.",
    )
    zus_code = fields.Char(
        string="Kod tytułu ubezpieczenia ZUS",
        default="0110",
        help="Kod używany w dokumentach ZUS do identyfikacji rodzaju ubezpieczenia "
             "i statusu pracownika.",
    )
