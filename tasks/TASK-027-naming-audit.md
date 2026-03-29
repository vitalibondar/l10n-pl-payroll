# TASK-027 Naming Audit

## Scope

Audit covered all user-facing strings in:

- `l10n_pl_payroll/models/*.py`
- `l10n_pl_payroll/views/*.xml`
- `l10n_pl_payroll/wizard/*.py`
- `l10n_pl_payroll/wizard/*_views.xml`
- `l10n_pl_payroll/report/*.xml`
- payroll parameter record names in `data/pl_payroll_parameters_2025.xml` and `data/pl_payroll_parameters_2026.xml`

Excluded from the audit:

- technical XML IDs and internal view names
- test code
- demo fixture names such as `TASK-004/...`

## Result Summary

- Base UI language is now Polish across models, menus, wizards, reports, and payroll parameter names.
- Terminology was normalized toward Polish payroll/accounting usage: `ZUS`, `PIT`, `KUP`, `PPK`, `Lista płac`, `Deklaracja ZUS DRA`, `Informacja PIT-11`.
- Short or colloquial labels were expanded to professional forms:
  - `Emerytalna` -> `Składka emerytalna`
  - `Rentowa` -> `Składka rentowa`
  - `Zdrowotna` -> `Składka zdrowotna`
  - `Fundusz Pracy` -> `Składka na Fundusz Pracy`
  - `FGŚP` -> `Składka na FGŚP`
- The payslip form now follows accountant flow instead of technical calculation order.

## Current Label Inventory

### Contract and Employee

- `hr.contract`: `Koszty uzyskania przychodu`, `Udział pracy twórczej (%)`, `Wariant PPK`, `Wpłata pracownika do PPK (%)`, `Wpłata dodatkowa pracownika do PPK (%)`, `Złożono PIT-2`, `Ulga podatkowa`, `Kod tytułu ubezpieczenia ZUS`
- `hr.employee`: `Status ucznia / studenta`

### Payslip Core

- Header/basic fields: `Nazwa`, `Pracownik`, `Wydział`, `Umowa`, `Wariant KUP`, `Firma`, `Okres od`, `Okres do`, `Status`
- Employee settlement fields: `Wynagrodzenie brutto`, `Dni choroby 80%`, `Dni choroby 100%`, `Dni urlopu`, `Wynagrodzenie urlopowe`, `Wynagrodzenie chorobowe`, `Podstawa wynagrodzenia chorobowego`, `Dni robocze w miesiącu`, `Nadgodziny 150% (godz.)`, `Nadgodziny 200% (godz.)`, `Dodatek za nadgodziny`
- Social/health/tax/PPK fields: `Składka emerytalna (pracownik)`, `Składka rentowa (pracownik)`, `Składka chorobowa (pracownik)`, `Składki ZUS pracownika razem`, `Podstawa składki zdrowotnej`, `Składka zdrowotna`, `Koszty uzyskania przychodu`, `Dochód do opodatkowania`, `Naliczona zaliczka PIT`, `Kwota zmniejszająca podatek`, `Zaliczka PIT do urzędu`, `Wpłata PPK pracownika`, `Wynagrodzenie netto`
- Employer-side fields: `Składka emerytalna (pracodawca)`, `Składka rentowa (pracodawca)`, `Składka wypadkowa`, `Składka na Fundusz Pracy`, `Składka na FGŚP`, `Wpłata PPK pracodawcy`, `Łączny koszt pracodawcy`
- Creative and warning fields: `Zatwierdzony raport twórczy`, `Wymaga raportu twórczego`, `Brakuje raportu twórczego`, `Wymiar etatu`, `Poniżej minimalnego wynagrodzenia`, `Dni choroby od początku roku`, `Uwagi do listy płac`

### Secondary Models

- Payroll parameters: `Nazwa parametru`, `Kod parametru`, `Wartość`, `Data od`, `Data do`, `Typ wartości`, `Firma`, `Uwagi`
- Creative report: `Raport pracy twórczej`, `Pracownik`, `Miesiąc raportu`, `Opis pracy twórczej`, `Status`, `Zatwierdził`, `Data zatwierdzenia`, `Lista płac`, `Firma`
- PIT-11: `Informacja roczna PIT-11`, `Pracownik`, `Firma`, `Rok podatkowy`, `Status`, `Przychód łącznie`, `Składki ZUS pracownika łącznie`, `Składka zdrowotna łącznie`, `Składka zdrowotna odliczana (7,75%)`, `KUP łącznie`, `Dochód łącznie`, `Pobrane zaliczki PIT`, `Wpłata PPK pracodawcy jako przychód`, `Liczba list płac`
- ZUS DRA: `Deklaracja miesięczna ZUS DRA`, `Firma`, `Rok rozliczenia`, `Miesiąc rozliczenia`, `Status`, `Liczba pracowników`, `Liczba list płac`, `Składki pracownika razem`, `Składki pracodawcy razem`, `Łącznie do zapłaty`, `Pozycje pracowników`
- ZUS DRA lines: `Deklaracja ZUS DRA`, `Firma`, `Pracownik`, `Lista płac`, `Wynagrodzenie brutto`, `Składka emerytalna (pracownik)`, `Składka emerytalna (pracodawca)`, `Składka rentowa (pracownik)`, `Składka rentowa (pracodawca)`, `Składka chorobowa`, `Składka wypadkowa`, `Składka zdrowotna`, `Składka na Fundusz Pracy`, `Składka na FGŚP`
- Payslip lines: `Pozycja listy płac`, `Lista płac`, `Nazwa składnika`, `Rodzaj składnika`, `Kwota`, `Uwagi`

### Views, Menus, Wizards, Reports

- Menus: `Płace PL`, `Listy płac`, `Generowanie list płac`, `Raporty twórcze`, `Deklaracje i raporty`, `PIT-11`, `ZUS DRA`, `Konfiguracja`, `Parametry płacowe`
- Payslip sections: `Dane podstawowe`, `Rozliczenie pracownika`, `Wynagrodzenie brutto`, `Chorobowe i nieobecności`, `Składki ZUS pracownika`, `Składka zdrowotna`, `Koszty uzyskania przychodu`, `Zaliczka na podatek dochodowy`, `PPK`, `Wynagrodzenie netto`, `Składki pracodawcy`, `Składki ZUS pracodawcy`, `PPK i koszt zatrudnienia`, `Składniki dodatkowe`, `Raport twórczy`, `Uwagi`
- Contract section labels: `Rozliczenie podatkowo-składkowe PL`, `Podatek i KUP`, `PPK i ZUS`
- Wizard titles/buttons: `Zbiorcze przeliczanie list płac`, `Generowanie list płac`, `Generowanie PIT-11`, `Generowanie deklaracji ZUS DRA`, `Przelicz`, `Generuj`, `Generuj PIT-11`, `Generuj DRA`, `Anuluj`
- Reports: `Pasek wynagrodzeń`, `Pasek wynagrodzeń A4`, `Informacja PIT-11`, `Deklaracja ZUS DRA`

## Standardization Decisions

- Use full contribution labels when the field is financial and not just a heading.
- Keep statutory abbreviations unchanged: `ZUS`, `PIT`, `PPK`, `FGŚP`, `KUP`.
- Prefer `Lista płac` / `Listy płac` over generic `Payroll`.
- Separate employee deductions from employer costs in wording and layout.
- Keep annual declaration naming aligned with official documents: `PIT-11`, `ZUS DRA`.

## Remaining Non-Polish Strings

- Demo fixture weekdays (`Monday`, `Tuesday`, ...) and demo contract names are still English because they belong to test/demo data rather than user-facing production UI.
- Internal XML view names such as `pl.payroll.payslip.form` are technical identifiers and were intentionally left unchanged.
