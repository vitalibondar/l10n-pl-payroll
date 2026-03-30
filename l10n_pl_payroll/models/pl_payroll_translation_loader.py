from collections import defaultdict
from pathlib import Path

from odoo import api, models
from odoo.tools.translate import PoFileReader


class PlPayrollTranslationLoader(models.AbstractModel):
    _name = "pl.payroll.translation.loader"
    _description = "PL Payroll translation loader"

    _SOURCE_LANG = "pl_PL"
    _TRANSLATION_FILES = {
        "en_US": "en_US.po",
        "uk_UA": "uk.po",
        "ru_RU": "ru.po",
    }

    @api.model
    def _apply_po_translations(self, lang_code, po_filename):
        po_path = Path(__file__).resolve().parents[1] / "i18n" / po_filename
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
            record.update_field_translations(field_name, {lang_code: value})

        for model_name, record_id, field_name in term_updates:
            record = self.env[model_name].browse(record_id)
            if record.exists():
                record.update_field_translations(
                    field_name,
                    {lang_code: term_updates[(model_name, record_id, field_name)]},
                    source_lang=self._SOURCE_LANG,
                )

        return True

    @api.model
    def apply_en_us_translations(self):
        return self._apply_po_translations("en_US", "en_US.po")

    @api.model
    def apply_all_translations(self):
        for lang_code, po_filename in self._TRANSLATION_FILES.items():
            self._apply_po_translations(lang_code, po_filename)
        return True
