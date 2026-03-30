from collections import defaultdict
from pathlib import Path

from odoo import api, models
from odoo.tools.translate import PoFileReader


class PlPayrollTranslationLoader(models.AbstractModel):
    _name = "pl.payroll.translation.loader"
    _description = "PL Payroll translation loader"

    @api.model
    def apply_en_us_translations(self):
        po_path = Path(__file__).resolve().parents[1] / "i18n" / "en_US.po"
        if not po_path.exists():
            return True

        direct_updates = []
        term_updates = defaultdict(dict)

        with po_path.open("rb") as po_file:
            for entry in PoFileReader(po_file):
                if entry["module"] != "l10n_pl_payroll" or not entry["value"]:
                    continue
                if entry["type"] == "code":
                    continue

                record = self.env.ref("%s.%s" % (entry["module"], entry["imd_name"]), raise_if_not_found=False)
                if not record:
                    continue

                field_name = entry["name"].split(",", 1)[1]
                if entry["type"] == "model_terms":
                    term_updates[(record._name, record.id, field_name)][entry["src"]] = entry["value"]
                else:
                    direct_updates.append((record, field_name, entry["value"]))

        for record, field_name, value in direct_updates:
            record.update_field_translations(field_name, {"en_US": value})

        for model_name, record_id, field_name in term_updates:
            record = self.env[model_name].browse(record_id)
            if record.exists():
                record.update_field_translations(field_name, {"en_US": term_updates[(model_name, record_id, field_name)]})

        return True
