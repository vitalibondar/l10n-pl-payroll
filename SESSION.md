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
- **Critical finding: 0 contracts filled in for 82 employees** (external payroll company handles data)
- Employee data sparse: no PESEL, no birthdays, no nationality
- Full report: ODOO_RECON.md

---

### 2026-03-28 (cont.) — Agent System & Task Atomization

- Designed multi-agent communication protocol (AGENTS.md)
- Created CLAUDE.md for repo root (instructions for every agent)
- Created SETUP.md with Git + plugin clone instructions
- Created 4 TASK files: research (001), parameters (002), security (003), test data (004)
- Vitalik: build universal product, not company-specific (DEC-007)
- Vitalik: work autonomously on fictional data, don't depend on external agency (DEC-008)
- Codex is good at thinking too, not just boilerplate — use for research tasks

---

### 2026-03-28 (cont.) — Contract Annex & Git Setup

- Read Vitalik's employment contract annex (CKO, autorskie koszty 50%, 12k PLN gross)
- Key findings: salary split into zasadnicze + honorarium autorskie, creative duties explicitly listed, monthly report required
- Answered git workflow question: Codex and Claude Code commit directly to feature branches, Cowork doesn't commit
- GitHub repo created: https://github.com/vitalibondar/l10n-pl-payroll.git (vitalibondar personal account)
- Initial commit with 19 files (project docs + module skeleton + 4 task files)
- Added git workflow instructions to all TASK files + updated AGENTS.md with full git protocol
- .DS_Store cleaned up

---

## What's Next

1. **Зараз:** Підготувати prompt для Codex → запустити TASK-001 + TASK-002 паралельно
2. **Codex:** TASK-003 (security) — після TASK-002
3. **Codex:** TASK-004 (test data) — після TASK-002
4. **Cowork:** Створити TASK-005+ (salary structure, contract fields, salary rules) після дослідження TASK-001
5. **Віталік:** Credentials тестової бази Odoo (коли буде готово, не блокує)
