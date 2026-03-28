# Multi-Agent Communication Protocol

> Як агенти (Claude Cowork, Claude Code, ChatGPT Codex) працюють разом над цим проєктом.

## Принцип

Агенти не спілкуються напряму. Єдиний канал — **файли в Git-репозиторії**. Кожен агент, починаючи роботу, читає потрібні файли. Закінчуючи — оновлює їх і комітить.

## Файлова структура (в репо)

```
l10n_pl_payroll/
├── CLAUDE.md              ← Головна інструкція для КОЖНОГО Claude-агента
├── STATE.md               ← Поточний стан (breadcrumbs)
├── PLAN.md                ← План з розбивкою по фазах
├── DECISIONS.md           ← Архітектурні рішення
├── LESSONS.md             ← Помилки, які не повторювати
├── ODOO_RECON.md          ← Розвідка Odoo-середовища
│
├── tasks/                 ← Задачі для агентів
│   ├── TASK-001.md        ← Одна задача = один файл
│   ├── TASK-002.md
│   └── ...
│
├── l10n_pl_payroll/       ← Код модуля Odoo
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── models/
│   ├── views/
│   ├── data/
│   ├── security/
│   ├── report/
│   └── tests/
│
└── tools/                 ← Допоміжні скрипти
    ├── test_data_gen.py   ← Генератор фіктивних тестових даних
    └── verify_calc.py     ← Верифікація розрахунків
```

## Формат задачі (tasks/TASK-NNN.md)

```markdown
# TASK-NNN: [Короткий заголовок]

**Status:** open | in_progress | done | blocked
**Assignee:** codex | claude-code | cowork
**Depends on:** TASK-XXX (якщо є)
**Phase:** 1.3

## Контекст
[Що потрібно знати для виконання. Посилання на DECISIONS.md, ODOO_RECON.md якщо треба.]

## Задача
[Чітке формулювання: що зробити, які файли створити/змінити.]

## Input
[Вхідні дані, файли, приклади.]

## Expected Output
[Що має бути результатом. Конкретні файли, формат, критерії прийняття.]

## Acceptance Criteria
- [ ] Критерій 1
- [ ] Критерій 2
- [ ] Тести проходять

## Notes
[Додаткові нотатки, edge cases, посилання на LESSONS.md.]
```

## Протокол для кожного агента

### Claude Cowork (цей чат — Orchestrator)

**Читає завжди:** STATE.md, LESSONS.md
**Пише:** STATE.md, DECISIONS.md, PLAN.md, tasks/*.md
**Не робить:** Код модуля (делегує)
**Комітить:** Ні (не має доступу до git)

Створює задачі, рев'юїть результати, оновлює стан.

### ChatGPT Codex

**Читає перед роботою (ОБОВ'ЯЗКОВО):**
1. CLAUDE.md (правила проєкту)
2. LESSONS.md (помилки)
3. tasks/TASK-NNN.md (конкретна задача)
4. DECISIONS.md (якщо задача стосується архітектури)

**Пише:** Код в l10n_pl_payroll/, тести в tests/
**Комітить:** Так, в feature branch `task/NNN-short-desc`
**Після завершення:** Оновлює Status в TASK-NNN.md → `done`, пушить

### Claude Code (CLI)

**Читає:** CLAUDE.md, конкретний TASK-NNN.md
**Пише:** Код, конфігурації, git операції
**Комітить:** Так
**Використовується для:** Швидкі фікси, git ops, linting, тестування в Odoo shell

### Інший Claude Cowork (окремий чат)

**Читає:** STATE.md, LESSONS.md, конкретний TASK-NNN.md
**Пише:** Документацію, QWeb templates, compliance deep-dives
**Комітить:** Ні (через Claude Code або Codex)

## Git Protocol (обов'язковий для всіх агентів)

**Repo:** `https://github.com/vitalibondar/l10n-pl-payroll.git`
**Local path:** `~/l10n-pl-payroll`
**Main branch:** `main`

### Кожна задача — окремий branch і PR

```bash
# Перед початком будь-якої задачі:
cd ~/l10n-pl-payroll
git checkout main && git pull
git checkout -b task/NNN-short-desc

# Після завершення:
git add <конкретні файли>       # НЕ git add -A
git commit -m "[TASK-NNN] Описова назва"
git push -u origin task/NNN-short-desc
gh pr create --title "[TASK-NNN] Коротка назва" --body "Опис що зроблено"
```

### Правила
- **Не** робити `git add -A` — додавати конкретні файли
- **Не** пушити в `main` напряму — тільки через PR
- **Не** force push
- **Обов'язково** оновити Status в TASK-NNN.md → `done` перед комітом
- Кожен TASK-файл має секцію `## Git Workflow` з точними командами — дотримуйся їх

### Naming Conventions

- Branches: `task/NNN-short-desc` (напр. `task/002-payroll-parameters`)
- Commits: `[TASK-NNN] Опис` (напр. `[TASK-002] Add pl.payroll.parameter model with 2025-2026 data`)
- PR: один PR на задачу (або на логічну групу задач)

## Правило "Read Before Write"

**Кожен агент, перед тим як написати хоча б рядок коду, ЗОБОВ'ЯЗАНИЙ прочитати:**
1. `CLAUDE.md` — завжди
2. `LESSONS.md` — завжди
3. Свій `TASK-NNN.md` — завжди
4. `DECISIONS.md` — якщо задача стосується архітектури чи salary rules

Це не рекомендація, це вимога. Порушення = переробка.
