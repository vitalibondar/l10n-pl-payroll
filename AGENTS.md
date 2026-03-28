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

## Naming Conventions

- Branches: `task/NNN-short-desc` (напр. `task/002-salary-structure`)
- Commits: `[TASK-NNN] Опис` (напр. `[TASK-002] Add salary structure for umowa o pracę`)
- PR: один PR на задачу (або на логічну групу задач)

## Правило "Read Before Write"

**Кожен агент, перед тим як написати хоча б рядок коду, ЗОБОВ'ЯЗАНИЙ прочитати:**
1. `CLAUDE.md` — завжди
2. `LESSONS.md` — завжди
3. Свій `TASK-NNN.md` — завжди
4. `DECISIONS.md` — якщо задача стосується архітектури чи salary rules

Це не рекомендація, це вимога. Порушення = переробка.
