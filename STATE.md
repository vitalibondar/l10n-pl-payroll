# STATE — Read This First

> After compaction or at the start of a new session, read this file FIRST.

## Now

- **Active task:** Repo ready, preparing Codex prompts for TASK-001 + TASK-002
- **Phase:** infrastructure done → launching first coding tasks
- **Blockers:** None. Repo live at https://github.com/vitalibondar/l10n-pl-payroll.git

## Context

**Project:** Custom Odoo module `l10n_pl_payroll` for calculating Polish salaries (gross-to-net) and generating pay slips (pasek wynagrodzeń).

**Who:**
- Віталік (CKO) — project lead, works with Claude Cowork (this chat = main orchestrator)
- Ася (CFO, Анастасія) — business owner, validates calculations, liaison with accountant
- Claude Cowork (this chat) — architecture, planning, orchestration, compliance
- ChatGPT Codex — heavy coding, unit tests, research, can also think/design
- Claude Code (CLI) — coding tasks, integration, testing in console

**Company:** Om Energy Solutions / Om Motors (manufacturing, Poland, 82 employees)

**Odoo:** Enterprise 17+ on Odoo.sh (confirmed by recon 2026-03-28, see ODOO_RECON.md)

**Two contract types supported:**
1. Umowa o pracę (employment contract) — full ZUS + PIT + PPK
2. Umowa zlecenie (civil contract) — reduced ZUS, different rules

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

**Architecture:** Standalone module (hr_payroll NOT installed). Parameterized rates with date-effective versioning. Product-grade quality.

## Git

- **Repo:** https://github.com/vitalibondar/l10n-pl-payroll.git
- **Local:** ~/l10n-pl-payroll
- **Branch strategy:** task/NNN-short-desc → PR → main
- **Agents commit directly** to feature branches (see AGENTS.md)

## Key Decisions (summary)

Full details in DECISIONS.md (DEC-001 through DEC-008):
1. Commercial-grade quality (DEC-001)
2. Parameterized rates with date-effective versioning (DEC-002)
3. Autorskie koszty = explicit flag, no silent 50% KUP (DEC-003)
4. RBAC from day one (DEC-004)
5. Fictional test data only (DEC-005)
6. Multi-agent workflow: Cowork + Codex + Claude Code (DEC-006)
7. Product-grade universal Polish payroll, not company-specific (DEC-007)
8. Autonomous development on fictional data (DEC-008)

## Анекс Віталіка (прочитаний 2026-03-28)

Vitalik's contract annex (CKO, from 2026-01-01):
- Gross: 12,000 PLN
- Split: wynagrodzenie zasadnicze (admin) + honorarium autorskie (creative)
- Creative work: 50% of time
- Honorarium залежить від створення Створів + прийняття Рапорту
- Creative duties: IT architecture, cybersecurity, KM, training materials, system integration, technical docs
- Admin duties: team management, document supervision, company representation, budgeting

## Tasks Status

| Task | Description | Assignee | Status | Branch |
|---|---|---|---|---|
| TASK-001 | Research Odoo payroll localizations | Codex | open | task/001-research-localizations |
| TASK-002 | pl.payroll.parameter model + data | Codex | open | task/002-payroll-parameters |
| TASK-003 | Security groups and access rules | Codex | open (depends 002) | task/003-security |
| TASK-004 | Fictional test data (12 scenarios) | Codex | open (depends 002) | task/004-test-data |

## Open Questions

- [ ] **Віталік:** Credentials тестової бази Odoo (назва DB на Odoo.sh) — не блокує, потрібно для Phase 5
- [x] ~~Анекс до умови~~ → Прочитаний, параметри зафіксовані вище

## Don't

- Don't hardcode any tax rates — always use parameterized config
- Don't use real employee data — fictional only
- Don't assume hr_payroll or hr_holidays installed — they're NOT
- Don't waste orchestrator context on boilerplate — delegate
- Don't bother Asya with questions we can answer ourselves
- Don't import from odoo.addons.hr_payroll — doesn't exist

## Agents & Delegation

| Agent | Role | Commits? |
|---|---|---|
| This chat (Cowork) | Orchestrator: architecture, planning, compliance | No |
| ChatGPT Codex | Coder + thinker: salary rules, tests, research | Yes, feature branches |
| Claude Code (CLI) | Integration: git ops, linting, testing | Yes |
| Other Cowork instances | Specialized: docs, QWeb, compliance | No |
