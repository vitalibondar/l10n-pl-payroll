# Session Log

---

### 2026-03-28 — Project Kickoff & Compliance Review

- Ася requested Polish Payroll module for Odoo (chat with Віталік)
- Research completed: Polish payroll rules (ZUS, PIT, PPK, overtime), Odoo payroll architecture, pay slip requirements, public holidays
- Feasibility assessed: YES, doable with Claude + Codex combo
- Compliance review completed (3 roles: Labor/PIP+ZUS, Tax/KAS, Data/UODO)
- Key compliance findings: autorskie koszty need contract documentation, RBAC required, DPIA recommended, fictional test data only
- Breadcrumbs initialized
- Vitalik confirmed: autorskie koszty applies to his salary (important test case)
- Vitalik clarified: "checking for law updates" = scheduled reminder, not AI monitoring

---

### 2026-03-28 (cont.) — Odoo Reconnaissance

- Connected to Odoo via MCP plugin, extracted environment data
- **Enterprise 17+ on Odoo.sh** confirmed
- 82 employees (mainly OM Poland), 2 companies relevant
- **hr_payroll NOT installed**, **hr_holidays NOT installed**
- hr_attendance actively used (10,980+ records) — good for overtime
- **Critical blocker discovered: 0 contracts filled in for 82 employees**
- Employee data sparse: no PESEL, no birthdays, no nationality
- Contract types are generic (Permanent, Temporary...) — need Polish types
- Full report: ODOO_RECON.md

---

### 2026-03-28 (cont.) — Agent System & Git Infrastructure

- Vitalik answered: external payroll company explains empty contracts, accountant in May, test DB available
- Designed multi-agent communication protocol (AGENTS.md)
- Created CLAUDE.md for repo root (instructions for every agent)
- Created SETUP.md with Git + plugin clone instructions
- Created first 3 TASK files for Codex (research, parameters, security)
- Decided: contract PDF extraction is a Phase 0 task for Codex/Cowork

---

## What's Next

1. **Віталік:** Створити GitHub-репо за інструкцією в SETUP.md (5 хвилин)
2. **Віталік:** Дати credentials тестової бази Odoo → інший Cowork створить плагін
3. **Codex:** TASK-001 (дослідження localizations) + TASK-002 (параметри) — паралельно
4. **Codex:** TASK-003 (security) — після TASK-002
5. **Cowork:** Створити TASK-004—006 (salary structure, contract extension, first salary rules)
6. **Віталік → Ася:** Уточнити PPK opt-outs, autorskie koszty employees, PIT-11 scope
