# TASK-027 Competitor Research

## Sources

Reviewed on 2026-03-29:

- Comarch Optima: payroll list and payout form documentation
  - https://pomoc.comarch.pl/optima/pl/2026/dokumentacja/formularz-listy-plac/
  - https://pomoc.comarch.pl/optima/pl/2025/dokumentacja/formularz-wyplaty/
- enova365: Kadry i Płace product documentation
  - https://www.enova.pl/rozwiazania/kadry-place/
- Sage Symfonia: payroll list and Płatnik export documentation
  - https://pomoc.symfonia.pl/data/kd/ERP/2025_1/data/lista_plac.htm
  - https://pomoc.symfonia.pl/data/kd/ERP/2025_1/data/eksport_do_programu_platnik.htm

## Cross-System Patterns

### 1. Main object is the payroll list

All three systems center the workflow around `Lista płac`, period, company, and employee set. That validates using `Listy płac` as the main menu entry and `Lista płac` as the primary document label.

### 2. Basic data comes first

The form starts with employee, company, contract, department, period, and status. Optima and Symfonia both expose the context of the payroll document before detailed contributions and taxes.

### 3. Tax and insurance are grouped separately

Competitor UIs consistently separate:

- social contributions (`ZUS`)
- health insurance (`Składka zdrowotna`)
- income tax (`PIT`)
- employer-side costs

This mirrors how a Polish bookkeeper validates a payroll result.

### 4. Employer cost is a separate block

Comarch and Symfonia distinguish employee deductions from employer burden. That supports a separate `Składki pracodawcy` tab instead of mixing everything into one calculation sheet.

### 5. Professional abbreviations stay visible

Competitor UIs do not hide abbreviations from experts. They use `ZUS`, `PIT`, `PPK`, `KUP`, `FGŚP`, `Fundusz Pracy`, and payroll-specific document names directly. Non-expert guidance belongs in explanations, not in simplified labels.

### 6. Reporting/declarations live in their own menu group

PIT and ZUS declarations are typically not mixed with day-to-day payslip entry. Competitor products expose them as a reporting/declaration area. That supports the `Deklaracje i raporty` menu in this module.

## Terminology Takeaways

- `Wynagrodzenie brutto` / `Wynagrodzenie netto` are standard and should stay.
- Use full contribution labels in detail screens: `Składka emerytalna`, `Składka rentowa`, `Składka chorobowa`, `Składka wypadkowa`, `Składka zdrowotna`.
- Prefer `Koszty uzyskania przychodu` over vague `KUP` in the label itself; `KUP` works as a short section heading for expert context.
- Use `Zaliczka na podatek dochodowy` or `Zaliczka PIT`, depending on whether the screen is detailed or compact.
- `PPK` remains the visible professional label; long explanation belongs in tooltip/help.

## Layout Decisions Applied in TASK-027

Based on the competitor review, the payslip form was reorganized into:

1. `Dane podstawowe`
2. `Rozliczenie pracownika`
3. `Wynagrodzenie brutto`
4. `Chorobowe i nieobecności`
5. `Składki ZUS pracownika`
6. `Składka zdrowotna`
7. `Koszty uzyskania przychodu`
8. `Zaliczka na podatek dochodowy`
9. `PPK`
10. `Wynagrodzenie netto`
11. `Składki pracodawcy`
12. `Składniki dodatkowe`
13. `Raport twórczy`
14. `Uwagi`

## Conclusion

The implemented naming and layout now align much more closely with Polish payroll software conventions:

- document-first workflow
- accountant-friendly grouping
- explicit ZUS/PIT/PPK terminology
- separate declaration area
- separate employer-cost section
