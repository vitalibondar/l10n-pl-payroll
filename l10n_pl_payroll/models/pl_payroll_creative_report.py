from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PlPayrollCreativeReport(models.Model):
    _name = "pl.payroll.creative.report"
    _description = "Raport pracy twórczej"
    _order = "date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True, string="Nazwa")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Pracownik",
        required=True,
        help="Pracownik, którego dotyczy miesięczny raport pracy twórczej.",
    )
    date = fields.Date(
        string="Miesiąc raportu",
        required=True,
        help="Wskaż miesiąc, za który pracownik rozlicza pracę twórczą objętą 50% KUP.",
    )
    description = fields.Text(
        string="Opis pracy twórczej",
        required=True,
        help="Opisz utwory, projekty albo inne rezultaty pracy twórczej wykonane w danym miesiącu. "
             "Ten opis stanowi dowód dla zastosowania kosztów autorskich.",
    )
    state = fields.Selection(
        [
            ("draft", "Szkic"),
            ("submitted", "Przekazany"),
            ("accepted", "Zatwierdzony"),
            ("rejected", "Odrzucony"),
        ],
        string="Status",
        default="draft",
        required=True,
        help="Etap obiegu raportu pracy twórczej. Tylko raport zatwierdzony można podpiąć "
             "do listy płac rozliczanej z 50% kosztami autorskimi.",
    )
    accepted_by = fields.Many2one(
        "res.users",
        string="Zatwierdził",
        readonly=True,
        help="Użytkownik, który zatwierdził raport twórczy.",
    )
    accepted_date = fields.Date(
        string="Data zatwierdzenia",
        readonly=True,
        help="Data zatwierdzenia raportu przez dział płac albo kadr.",
    )
    payslip_id = fields.Many2one(
        "pl.payroll.payslip",
        string="Lista płac",
        readonly=True,
        help="Lista płac, do której przypięto zatwierdzony raport twórczy.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Firma",
        default=lambda self: self.env.company,
        required=True,
        help="Firma, w której rozlicza się ten raport pracy twórczej.",
    )

    @api.depends("employee_id.name", "date")
    def _compute_name(self):
        for report in self:
            if report.employee_id and report.date:
                report.name = "%s - %s" % (
                    report.employee_id.name,
                    fields.Date.to_date(report.date).strftime("%Y-%m"),
                )
            else:
                report.name = False

    def action_submit(self):
        for report in self:
            if report.state != "draft":
                raise UserError(_("Raport można przekazać tylko ze statusu 'Szkic'."))
            report.write({"state": "submitted"})
        return True

    def action_accept(self):
        for report in self:
            if report.state != "submitted":
                raise UserError(_("Zatwierdzić można tylko raport przekazany do akceptacji."))
            report.write({
                "state": "accepted",
                "accepted_by": self.env.uid,
                "accepted_date": fields.Date.context_today(self),
            })
        return True

    def action_reject(self):
        for report in self:
            if report.state != "submitted":
                raise UserError(_("Odrzucić można tylko raport przekazany do akceptacji."))
            report.write({
                "state": "rejected",
                "accepted_by": False,
                "accepted_date": False,
            })
        return True

    def action_reset(self):
        for report in self:
            if report.state not in ("submitted", "accepted", "rejected"):
                raise UserError(_("Do szkicu można cofnąć tylko raport poza statusem 'Szkic'."))
            report.write({
                "state": "draft",
                "accepted_by": False,
                "accepted_date": False,
            })
        return True
