# STATE — Read This First

> After compaction or at the start of a new session, read this file FIRST.

## Now

- **Active task:** Phase 6 — Payroll Component Constructor (architecture ready, tasks TASK-038..044 defined)
- **Phase:** Phase 5 done (translations, fixes, audit). Phase 6 = component constructor + batch editing + attendance sync
- **Blockers:** None. Waiting for Vitalik approval of ARCHITECTURE-PHASE6.md before coding.

## Context

**Project:** Custom Odoo module `l10n_pl_payroll` for calculating Polish salaries (gross-to-net) and generating pay slips (pasek wynagrodzeń).

**Who:**
- Віталік (CKO) — project lead, works with Claude Cowork (this chat = main orchestrator)
- Ася (CFO, Анастасія) — business owner, validates calculations, liaison with accountant
- Claude Cowork (this chat) — architecture, planning, orchestration, compliance
- Claude Code (CLI) — coding tasks, commits to main, pushes to GitHub
- ChatGPT Codex — simpler/mechanical tasks only (complex tasks go to Claude Code per Vitalik's preference)

**Company:** Om Energy Solutions / Om Motors (manufacturing, Poland, 82 employees)

**Odoo:** Enterprise 18.0 on Odoo.sh (confirmed 2026-03-28 via session_info API)

**Two contract types supported:**
1. Umowa o pracę (employment contract) — full ZUS + PIT + PPK
2. Umowa zlecenie (civil contract) — reduced ZUS, different rules
3. Umowa o dzieło (contract for specific work) — no ZUS, flat PIT

**Key salary rules chain:** Gross → ZUS employee (13.71%) → Health (9%) → PIT (12%/32%, cumulative yearly) → PPK (2%) → Net

**Special features:**
- Autorskie koszty uzyskania przychodu (50% KUP for creative workers) — Віталік's salary uses this
- Ulga dla młodych (PIT exemption <26 years), na powrót, dla rodzin 4+, dla seniorów
- PPK (opt-in/out, reduced rate 0.5%, additional up to 4%)
- Cumulative PIT (year-to-date, not per-month)
- ZUS basis cap (282,600 PLN in 2026, pension+disability stop, health continues)
- Overtime: 150%/200% per Kodeks pracy
- Bonuses (gross/net) and penalties
- Scheduled reminder to check for law changes
- Creative work reports (raport twórczy) linked to payslips

**Architecture:** Standalone module (hr_payroll NOT installed). Parameterized rates with date-effective versioning. Product-grade quality.

## Git

- **Repo:** https://github.com/vitalibondar/l10n-pl-payroll.git
- **Local:** ~/l10n-pl-payroll
- **Branch strategy:** Claude Code commits directly to main and pushes
- **Recent commits:**
  - `79e5012` Fix: remove hr_attendance dep, disable translation loader
  - `0edcf51` Fix en_US.po: translate remaining 3 empty entries
  - `6d719d0` Parameterize hardcoded dzieło/KUP rates
  - `fd1123d` Fix pl.po: fill 293 empty identity translations

## Key Decisions (summary)

Full details in DECISIONS.md (DEC-001 through DEC-010):
1. Commercial-grade quality (DEC-001)
2. Parameterized rates with date-effective versioning (DEC-002)
3. Autorskie koszty = explicit flag, no silent 50% KUP (DEC-003)
4. RBAC from day one (DEC-004)
5. Fictional test data only (DEC-005)
6. Multi-agent workflow (DEC-006) — Claude Code for complex tasks
7. Product-grade universal Polish payroll, not company-specific (DEC-007)
8. Autonomous development on fictional data (DEC-008)
9. Component Constructor — user-definable types, not hardcoded templates (DEC-009) — NEW
10. Three editing modes: individual, batch wizard, grid view (DEC-010) — NEW

## Phase 6 Tasks

| Task | Description | Status | Depends on |
|---|---|---|---|
| TASK-038 | Component type model + seed data + views | ready | — |
| TASK-039 | Extend payslip lines with component type + PIT/ZUS flags | ready | TASK-038 |
| TASK-040 | Update salary engine for PIT/ZUS exemptions | ready | TASK-039 |
| TASK-041 | Batch wizard for adding components | ready | TASK-039 |
| TASK-042 | Grid list view for batch editing | ready | — |
| TASK-043 | hr_attendance overtime sync + traceability | ready | — |
| TASK-044 | UI: move NET to right, update form layout | ready | — |

Parallelizable: TASK-038, TASK-042, TASK-043, TASK-044.

## Previous Phases (completed)

| Phase | Tasks | Description |
|---|---|---|
| 1-3 | TASK-001..009 | Core engine: parameters, security, test data, salary computation, PDF |
| 4 | TASK-013..026 | UI redesign, PIT-11, ZUS DRA, creative reports, batch wizard |
| 5 | TASK-027..037 | Translations (PL/EN/UK/RU), Odoo.sh fixes, pl.po/en_US.po fixes |

## Known Debt

- Translation loader disabled in __manifest__ (Odoo.sh crash fix) — re-enable or switch to standard i18n
- `_is_mandate_contract()` uses string comparison — should use constant
- Multi-contract employee (Marek Jabłoński) added to seed data but payslip batch wizard doesn't handle contract selection automatically

## Don't

- Don't hardcode any tax rates — always use parameterized config
- Don't use real employee data — fictional only
- Don't assume hr_payroll or hr_holidays installed — they're NOT
- Don't import from odoo.addons.hr_payroll — doesn't exist
- Don't make hr_attendance a hard dependency — soft import only
- Don't waste orchestrator context on boilerplate — delegate to Claude Code
