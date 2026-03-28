# STATE — Read This First

> After compaction or at the start of a new session, read this file FIRST.

## Now

- **Active task:** Planning & architecture for Polish Payroll Odoo module
- **Phase:** planning
- **Blockers:** None yet. Need Ася's validation of salary rules before any code goes to production.

## Context

**Project:** Custom Odoo module `l10n_pl_payroll` for calculating Polish salaries (gross-to-net) and generating pay slips (pasek wynagrodzeń).

**Who:**
- Віталік (CKO) — project lead, works with Claude Cowork (this chat = main orchestrator)
- Ася (CFO, Анастасія) — business owner, validates calculations, liaison with accountant
- Claude Cowork (this chat) — architecture, planning, orchestration, compliance
- ChatGPT Codex — heavy coding, unit tests, boilerplate, can also think/design
- Claude Code (CLI) — coding tasks, integration, testing in console

**Company:** Om Energy Solutions / Om Motors (manufacturing, Poland)

**Odoo:** Enterprise 17+ on Odoo.sh (confirmed by recon 2026-03-28, see ODOO_RECON.md)

**Two contract types supported:**
1. Umowa o pracę (employment contract) — full ZUS + PIT + PPK
2. Umowa zlecenie (civil contract) — reduced ZUS, different rules

**Key salary rules chain:** Gross → ZUS employee (13.71%) → Health (9%) → PIT (12%/32%, cumulative yearly) → PPK (2%) → Net

**Special features:**
- Autorskie koszty uzyskania przychodu (50% KUP for creative workers) — Віталік's salary uses this
- Ulga dla młodych (PIT exemption <26 years)
- Overtime: 150%/200% per Kodeks pracy
- Bonuses (gross/net) and penalties
- Public holidays calendar
- Leave verification (integration with Time Off module)
- Scheduled reminder to check for law changes (not AI monitoring — just a prompt)

**Architecture:** Odoo salary structures + salary rules (Python code). QWeb template for pay slip PDF. Parameterized rates (not hardcoded) with date-effective versioning.

## Key Decisions (summary)

- Build as if commercial, even though it's a home project (DEC-001)
- Parameterized rates with date-effective versioning, not hardcoded values (DEC-002)
- Autorskie koszty require explicit flag in employee contract — no silent application (DEC-003)
- Role-based access control on payroll data from day one (DEC-004)
- Test data must be fictional only — no real PESEL/names/salaries (DEC-005)

## Open Questions

- [x] ~~Which Odoo version?~~ → **Enterprise 17+ on Odoo.sh** (recon 2026-03-28)
- [x] ~~Does the company already use a payroll base module?~~ → **No. hr_payroll NOT installed** (recon)
- [x] ~~Where is Odoo hosted?~~ → **Odoo.sh** (traceback path confirmed)
- [x] ~~Which Odoo version?~~ → **Enterprise 17+ on Odoo.sh** (recon 2026-03-28)
- [x] ~~Does the company already use a payroll base module?~~ → **No. hr_payroll NOT installed** (recon)
- [x] ~~Where is Odoo hosted?~~ → **Odoo.sh** (traceback path confirmed)
- [x] ~~Why are contracts empty?~~ → External payroll company handles everything in their own system. Contracts will be filled when switching to our module. (2026-03-28)
- [x] ~~When does accountant start?~~ → **May 2026**. Until then, external firm does payroll. We build & test now, debug with accountant in May, then full switch. (2026-03-28)
- [x] ~~Who fills contracts?~~ → Alena Hrytsanchuk (primary), with PDF extraction to reduce manual work. (2026-03-28)
- [x] ~~Test Odoo base?~~ → Clone existing Odoo plugin to point at test DB. Віталік has access. (2026-03-28)
- [x] ~~PPK, autorskie, PIT-11 scope~~ → Build universal: ALL Polish payroll features regardless of current usage. Product-grade. (DEC-007)
- [x] ~~Data from external agency~~ → НЕ потрібно. Працюємо на фіктивних даних. Генеруємо тестові контракти на всі варіанти. (2026-03-28)
- [ ] **Віталік:** Credentials тестової бази Odoo (назва DB на Odoo.sh)
- [ ] **Віталік:** Покаже свій анекс до умови (авторські koszty + звіт) — як reference

## Don't

- Don't hardcode any tax rates, ZUS rates, or thresholds — always use parameterized config
- Don't use real employee data in tests or examples — fictional only
- Don't implement salary rules without Ася/accountant validation
- Don't start coding before architecture is agreed upon in this chat
- Don't waste this chat's context on boilerplate — delegate to Codex/Claude Code
- Enterprise confirmed — but don't assume Enterprise Payroll (hr_payroll) is installed, it's NOT
- hr_holidays (Time Off) is also NOT installed — don't reference hr.leave models until it's installed

## Agents & Delegation

| Agent | Role | What to delegate |
|---|---|---|
| This chat (Cowork) | Orchestrator | Architecture, compliance, decisions, planning |
| ChatGPT Codex | Heavy coder + thinker | Salary rules Python code, unit tests, module structure, research subtasks |
| Claude Code (CLI) | Integration & testing | File operations, Odoo shell testing, linting, git |
| Other Cowork instances | Specialized subtasks | Compliance deep-dives, documentation, QWeb templates |
