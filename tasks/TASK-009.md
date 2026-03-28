# TASK-009: PDF pay slip (pasek wynagrodzeń) — QWeb report

**Status:** done
**Assignee:** Codex
**Branch:** task/009-pdf-payslip
**Depends on:** TASK-007 merged (does NOT depend on TASK-008, can run in parallel)

## Objective

Create a PDF pay slip (pasek wynagrodzeń / kwitek wypłaty) that employees receive monthly. This is NOT a boring accountant printout — it's a document people care about. Design it to be clear, readable, and informative for a regular employee who doesn't understand accounting terminology.

## Design Philosophy

The current industry standard for Polish pay slips is a cryptic table full of abbreviations like "PODST. ZDROW.", "ZAL. POD.", "ZANIECH. POD." that nobody understands. We're doing better.

Our pay slip should:
1. Start with what matters most: NET pay (big, prominent)
2. Show a clear visual flow: Gross → Deductions → Net (like a waterfall)
3. Explain every line in plain Polish — not accounting jargon
4. Group deductions logically with subtotals
5. Include YTD (narastająco) summaries
6. Be clean, professional, with good typography
7. Comply with PDF/UA accessibility standard (tagged PDF, proper reading order, alt text, language tag)
8. Include company logo placeholder

## Required Sections (in order)

### Header
- Company name and address (from res.company)
- "PASEK WYNAGRODZEŃ" title
- Period (miesiąc/rok)
- Employee name, PESEL (masked: ***********51), department, position
- Contract type (umowa o pracę / umowa zlecenie)

### NET PAY (hero section)
- Big, prominent net amount
- Payment method (przelew bankowy)
- "Do wypłaty" label

### Income Breakdown
- Wynagrodzenie zasadnicze (base salary)
- Future: overtime, bonuses, benefits (for now just gross from contract)
- Label: "Wynagrodzenie brutto" with total

### Deductions Waterfall
Show as a clear progression with explanations:

**Składki ZUS pracownika** (Your social security contributions)
- Emerytalne (pension) — X% of gross = amount
- Rentowe (disability) — X% of gross = amount
- Chorobowe (sickness) — X% of gross = amount
- Subtotal ZUS employee
- Small note: "Te składki budują Twój kapitał emerytalny i ubezpieczenie"

**Ubezpieczenie zdrowotne** (Health insurance)
- Basis (gross minus ZUS)
- 9% health contribution
- Note: "Składka na NFZ — daje Ci dostęp do publicznej opieki zdrowotnej"

**Koszty uzyskania przychodu** (Tax-deductible costs)
- Type and amount (250 PLN standard / 50% autorskie / 20% zlecenie)
- Note explaining what KUP means in plain language

**Zaliczka na podatek dochodowy** (Income tax advance)
- Taxable income (basis - KUP)
- Tax rate (12% or 32%)
- PIT reducing amount (kwota zmniejszająca) if applicable
- PIT due this month
- Note: "Zaliczka na PIT — rozliczysz ją w zeznaniu rocznym"

**PPK** (if applicable)
- Employee contribution
- Employer contribution (shown as benefit, not deduction)
- Note: "Pracownicze Plany Kapitałowe — Twoje dodatkowe oszczędności na emeryturę"

### Employer Cost (informational section)
- ZUS employer side (emerytalne, rentowe, wypadkowe, FP, FGŚP)
- PPK employer
- Total employer cost
- Note: "Tyle kosztuje Twoje zatrudnienie — te kwoty pracodawca płaci dodatkowo ponad Twoje wynagrodzenie"

### YTD Summary (Narastająco w roku)
- Cumulative gross
- Cumulative ZUS basis
- Cumulative PIT basis
- Cumulative PIT paid

### Footer
- Document symbol (e.g., E/2026/01/001)
- Date generated
- "Wygenerowano automatycznie w systemie Odoo"
- No signature required (electronic document)

## Technical Implementation

1. Create `report/pl_payroll_payslip_report.xml` — report action definition
2. Create `report/pl_payroll_payslip_template.xml` — QWeb template
3. Add report files to `__manifest__.py` data list
4. Report should work for single payslip and batch (multi-payslip, page break between each)
5. Use `t-call="web.html_container"` and `t-call="web.external_layout"` for standard Odoo report structure
6. CSS styling inline in the template (Odoo QWeb standard)
7. Paper format: A4
8. PDF/UA compliance: add `<meta name="pdf-ua" content="true"/>`, use semantic HTML (h1/h2/p, not just divs), proper lang="pl" attribute, meaningful structure

## Accessibility (PDF/UA)

- All text must be in tagged structure (headers, paragraphs, tables with proper headers)
- Use semantic HTML elements, not just styled divs
- Include lang="pl" on root element
- Tables must have proper <th> headers
- No purely decorative images without alt=""
- Reading order must follow visual order

## Files to create/modify

- `l10n_pl_payroll/report/__init__.py` (empty, for package)
- `l10n_pl_payroll/report/pl_payroll_payslip_report.xml` — report action
- `l10n_pl_payroll/report/pl_payroll_payslip_template.xml` — QWeb template
- `l10n_pl_payroll/__manifest__.py` — add report files to data
- `l10n_pl_payroll/__init__.py` — no change needed (reports are XML only)

## Do NOT

- Don't use abbreviations without explanation
- Don't make it look like a spreadsheet dump
- Don't skip the human-readable notes
- Don't forget PDF/UA accessibility tags
- Don't hardcode rates in the template — read from payslip fields

## Git Workflow

```
git checkout main && git pull
git checkout -b task/009-pdf-payslip
# ... implement ...
git add l10n_pl_payroll/report/ l10n_pl_payroll/__manifest__.py
git commit -m "[TASK-009] Add PDF pay slip report with human-readable design"
git push -u origin task/009-pdf-payslip
gh pr create --title "[TASK-009] PDF pay slip (pasek wynagrodzeń)" --body "QWeb report for pay slips. Human-readable design with explanations, PDF/UA accessible, YTD summaries."
```
