# Decisions

---

### DEC-001: Build as commercial-grade
**Date:** 2026-03-28
**Context:** This is a "home project" but Віталік explicitly said to build it as if we'll sell it.
**Choice:** Commercial-grade quality: proper module structure, tests, security, compliance, documentation.
**Why:** Makes the module potentially sellable on Odoo Apps Store. Also forces discipline that prevents bugs in payroll (where bugs = wrong salaries = legal liability).

---

### DEC-002: Parameterized rates with date-effective versioning
**Date:** 2026-03-28
**Context:** Polish tax/ZUS rates change yearly (sometimes mid-year). Hardcoded values would break historical calculations when rates change.
**Choice:** All rates, thresholds, and limits stored as parameters with `date_from` / `date_to` fields. Salary rules reference parameters, not literals.
**Why:** When minimum wage changes from 4806 to X in 2027, we add a new parameter record — old payslips still calculate correctly with old values.

---

### DEC-003: Autorskie koszty require explicit flag
**Date:** 2026-03-28
**Context:** 50% KUP for creative workers is a major tax benefit but KAS scrutinizes it heavily. Must be documented in the employment contract with % of creative work.
**Choice:** Module requires explicit checkbox + percentage field on employee contract. Without it, standard 250 PLN/month KUP applies.
**Why:** Prevents accidental application of 50% KUP (which would be a tax violation). Compliance review flagged this as 🔴 blocking.

---

### DEC-004: RBAC on payroll data from day one
**Date:** 2026-03-28
**Context:** Payroll data (salaries, PESEL, ZUS) is among the most sensitive employee data. GDPR requires access limitation.
**Choice:** Custom Odoo security groups: `payroll_officer` (full access), `payroll_manager` (read + approve), `employee_self` (own payslip only).
**Why:** UODO compliance. Also good practice — not every HR person should see all salaries.

---

### DEC-005: Fictional test data only
**Date:** 2026-03-28
**Context:** Module code may end up on GitHub (open-source potential). Test data with real PESEL/names = GDPR breach.
**Choice:** All test data uses fictional employees with generated PESEL-like numbers (valid format, invalid checksum). Build a test data generator.
**Why:** GDPR compliance + open-source readiness.

---

### DEC-007: Product-grade scope — full Polish payroll, not company-specific
**Date:** 2026-03-28
**Context:** Initially scoped to Om Energy's 82 employees. Віталік redirected: "не відштовхуватися від того, хто бере чи не бере, а від гіпотетичної функціональності. Створюй універсальне рішення, яке потенційно стане продуктом."
**Choice:** Build universal Polish payroll module supporting ALL standard Polish payroll features, not just the ones Om Energy currently uses. Goal = full independence from external payroll agency + potential Odoo Apps Store product.
**Why:** Company-specific solutions have zero resale value. Universal module serves Om Energy AND becomes a product. Also: employees join/leave, their situations change — the module must handle any Polish payroll scenario, not just today's 82 people.
**Scope includes:**
- All contract types (o pracę, zlecenie, B2B integration)
- All KUP variants (standard, autorskie with configurable %)
- All PIT ulgi (młodzi, powrót, rodziny 4+, seniorzy)
- PPK with all options (opt-in, opt-out, reduced, additional)
- Full cumulative PIT with year-to-date tracking
- ZUS with all codes and basis cap
- Overtime per Kodeks pracy
- PIT-2 handling
- Bonuses (gross/net), penalties, deductions
- Payslip PDF generation
- Public holidays calendar
- Time Off integration (when module installed)
- PIT-11 / PIT-4R generation (later phase, but architected from start)

---

### DEC-008: Fictional test data only — no external agency data during development
**Date:** 2026-03-28
**Context:** Initially planned to request data export from external payroll agency. Віталік redirected: fully autonomous development, no bothering Ася. Real contracts (PDFs) available later as reference.
**Choice:** Generate fictional test contracts covering ALL payroll scenarios (12+ variants). Develop and test entirely on fake data. Real data import = separate task when switching to production.
**Why:** (1) GDPR compliance from day one — no real data in code. (2) Covers edge cases that real data might not have (e.g., ulga na powrót). (3) No dependency on external agency timeline. (4) Авторські koszty reference — Віталік will show his own contract annex when ready.

---

### DEC-006: Multi-agent development workflow
**Date:** 2026-03-28
**Context:** Віталік is not a programmer. Team = Claude Cowork (orchestrator) + ChatGPT Codex (coder/thinker) + Claude Code CLI (integration).
**Choice:** This Cowork chat = main context, architecture, decisions. Codex gets atomized coding tasks with full specs. Claude Code CLI handles file ops and testing.
**Why:** Preserves expensive Cowork context for decisions. Codex is good at coding AND thinking — use it for more than boilerplate. Already proven workflow ("чудова звʼязка").

---
