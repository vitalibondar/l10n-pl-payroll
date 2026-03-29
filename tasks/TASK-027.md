# TASK-027: UX — Polish professional naming + tooltips for non-experts

**Status:** done
**Branch:** task/027-ux-tooltips
**Created:** 2026-03-29
**Depends on:** none

## Goal

Two audiences use this module:
1. **Experienced Polish bookkeeper (księgowa)** — primary user. Interface must feel native: correct Polish terminology, logical grouping matching how a ksiegowa thinks about payroll.
2. **Non-expert (CKO, CFO, foreign accountant)** — occasional user. Needs help text explaining what each field means.

This task has two parts: (A) research + naming audit, (B) implementation.

Write your completion report to `tasks/TASK-027-report.md`.

## Part A: Research

### A1. Audit all user-facing strings

Go through every view XML file and every model field `string=` attribute. List ALL user-facing labels in the module. For each one, assess:
- Is the current label what a Polish księgowa would expect?
- Is it consistent with Polish payroll software conventions (Płatnik, Optima, Enova, Sage Symfonia)?
- If the label is in English or uses non-standard Polish — propose the correct term.

Write findings to `tasks/TASK-027-naming-audit.md`.

### A2. Research Odoo tooltip mechanism

Odoo supports `help=` attribute on fields, which renders as a tooltip (ⓘ icon next to the field label). Research:
- Does `help=` work in Odoo 18 form views?
- Does it work in list views?
- Does it work in notebook page headers?
- Any limitations or gotchas?
- Is there a way to add tooltips to page/group headers (not just fields)?

Write findings to `tasks/TASK-027-tooltip-research.md`.

### A3. Research Polish payroll software UI conventions

Look at screenshots/docs of:
- Comarch Optima (moduł Płace i Kadry)
- Enova365 (moduł Kadry i Płace)
- Sage Symfonia (moduł Kadry i Płace)

Focus on:
- How do they group payslip fields? (tabs, sections)
- What terminology do they use for: gross, net, ZUS contributions, health, PIT, KUP, PPK?
- How do they present employer costs vs employee deductions?
- Menu structure?

Write findings to `tasks/TASK-027-competitor-research.md`.

## Part B: Implementation

Based on research from Part A, implement:

### B1. Rename fields

Update `string=` attribute on all model fields to match professional Polish terminology. Examples of likely changes:
- "Brutto" is correct
- "Netto" is correct
- ZUS field labels — should match Płatnik terminology
- "Fundusz Pracy" → might need full "Składka na Fundusz Pracy"
- Check if "Zaliczka PIT" is better than "PIT advance"
- KUP labels — "Koszty uzyskania przychodu" vs abbreviated

### B2. Add help= tooltips

Add `help=` to every payroll-specific field on payslip, contract, and employee models. Each tooltip should:
- Be in Polish
- Explain what the field means in plain language (not just repeat the label)
- Include the legal basis or rate where relevant
- Be useful to a non-accountant

Example:
```python
zus_emerytalne_ee = fields.Float(
    string="Składka emerytalna (pracownik)",
    help="Składka na ubezpieczenie emerytalne potrącana z wynagrodzenia pracownika. "
         "Stawka: 9,76% podstawy wymiaru. Podstawa prawna: art. 22 ust. 1 pkt 1 "
         "ustawy o systemie ubezpieczeń społecznych.",
)
```

### B3. Rename view elements

- Notebook page titles should be in professional Polish
- Menu items should match Polish payroll conventions
- Button labels
- Wizard titles and descriptions

### B4. Organize form layout

Review and reorganize payslip form to match how a księgowa thinks:
1. Dane podstawowe (header: employee, contract, period, state)
2. Wynagrodzenie brutto (gross, overtime, bonuses/deductions)
3. Składki ZUS pracownika
4. Składka zdrowotna
5. Koszty uzyskania przychodu
6. Zaliczka na podatek dochodowy
7. PPK
8. Wynagrodzenie netto
9. Składki ZUS pracodawcy (separate tab/section)
10. Chorobowe (if applicable)
11. Raport twórczy (if applicable)

## Localization strategy

This module MUST support full i18n localization via Odoo's standard `i18n/` mechanism (.po files). BUT because this is a Polish payroll module, the BASE language of all field labels is POLISH — not English.

### Languages: PL, EN, UK, RU

Four .po files: `pl.po`, `en_US.po`, `uk.po`, `ru.po`.

### Persona-based approach

Each language has TWO target personas. When writing labels and tooltips, imagine BOTH personas reading your text. The label must be comfortable for the expert; the tooltip must rescue the non-expert.

**PL — Polish**
- **(a) Experienced Polish księgowa.** This is her full-time workplace. She's spent 20 years reading PITs, ZUS DRAs, and Płatnik exports. The interface must feel like a fighter pilot's cockpit — scary to outsiders, but perfectly natural and efficient for her. Use correct Płatnik/Optima terminology without dumbing it down.
- **(b) Non-accountant in a Polish company** (CEO, HR manager, developer). Knows roughly what PIT is, might have forgotten what PIT-2 means, definitely doesn't know what "kwota zmniejszająca" is. Needs tooltips that explain everything from scratch — but the label itself stays professional.

**EN — English**
- **(a) English-speaking accountant** working with Polish payslips (e.g., an auditor from a foreign parent company, or an expat CFO). Understands accounting concepts but doesn't know Polish tax law specifics. Needs Polish terms preserved in parentheses so they can cross-reference with Polish documents.
- **(b) English-speaking non-accountant** (developer, CEO, investor) who needs to use the module with no one to ask. Tooltips must explain not just the field but the Polish payroll concept behind it.

**UK — Ukrainian**
- **(a) Ukrainian accountant** who knows accounting inside out (imagine someone who spent 20 years at Naftogaz). Doesn't know Polish law, but accounting is accounting — she'll understand "соціальне страхування" instantly. Needs Polish terms in parentheses to map to local documents.
- **(b) Ukrainian non-accountant** (manager, worker). Maybe knows what PESEL is, has heard of ZUS, but that's about it. Tooltips need to explain everything assuming zero Polish payroll knowledge.

**RU — Russian**
- **(a) Russian-speaking accountant** — same logic as Ukrainian accountant persona. Accounting concepts are universal, but Polish-specific terms need parenthetical originals.
- **(b) Russian-speaking non-accountant** — same approach as Ukrainian non-expert. Full explanations in tooltips, professional labels.

### Rules:

1. **Field `string=` attribute** = Polish. This is the source language. Example: `string="Składka emerytalna (pracownik)"`
2. **Labels** must be comfortable for the EXPERT persona of that language. Don't dumb down labels.
3. **Tooltips (`help=`)** must rescue the NON-EXPERT persona. Explain the concept, not just repeat the label.
4. **For Polish-specific terms that have no equivalent** (e.g., "kwota zmniejszająca podatek", "koszty uzyskania przychodu"): in EN/UK/RU translations, keep the original Polish term in parentheses. Example: `"Tax-reducing amount (kwota zmniejszająca podatek) — monthly PIT reduction of 300 PLN for employees who filed PIT-2."`
5. **For universal abbreviations** (PPK, ZUS, PIT, PESEL): keep as-is in all languages.
6. **Polish .po** — identity mapping for Odoo compatibility, BUT tooltips still matter (persona PL-b needs them).
7. **Don't over-explain obvious things** to the expert. "Brutto" doesn't need a tooltip in PL. But "Kwota zmniejszająca podatek" does — even for a Polish księgowa's assistant.

### What to generate:

- `i18n/pl.po` — identity mapping (Polish → Polish) for Odoo compatibility
- `i18n/en_US.po` — full English translation, Polish terms in parentheses for professional terms
- `i18n/uk.po` — Ukrainian translation, Polish terms in parentheses
- `i18n/ru.po` — Russian translation, Polish terms in parentheses

Use `python3 -c "from babel.messages.pofile import ..."` or manual .po format. Standard Odoo .po structure.

## Important

- Primary audience = Polish księgowa. All field labels default to Polish.
- Labels serve the EXPERT. Tooltips serve the NON-EXPERT.
- Keep field `name=` (Python names) in English — only change user-facing `string=` and `help=`.
- NEVER lose the original Polish term when translating. Always include Polish term in parentheses for professional terms in EN/UK/RU.

## Files to modify

- ALL files in `l10n_pl_payroll/models/` (field strings and help)
- ALL files in `l10n_pl_payroll/views/` (labels, page titles, menus)
- ALL files in `l10n_pl_payroll/wizard/` (wizard labels)
