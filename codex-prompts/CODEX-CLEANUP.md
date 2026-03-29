# Codex: очистка робочого дерева і мердж тасків

Робоче дерево брудне: є неіндексовані файли від нових тасків (TASK-018..026, codex-prompts, RUNBOOK.md). Їх потрібно закомітити в main, а потім продовжити роботу над тасками.

## Крок 1: очистити робоче дерево

```bash
cd /Users/vb/l10n-pl-payroll
git checkout main
git pull origin main
```

Якщо git скаже про untracked files або unstaged changes — це нормально. Це нові файли тасків. Додай їх:

```bash
git add tasks/TASK-018.md tasks/TASK-019.md tasks/TASK-020.md tasks/TASK-021.md tasks/TASK-022.md tasks/TASK-023.md tasks/TASK-024.md tasks/TASK-025.md tasks/TASK-026.md
git add codex-prompts/CODEX-018.md codex-prompts/CODEX-019.md codex-prompts/CODEX-020.md codex-prompts/CODEX-021.md codex-prompts/CODEX-022.md codex-prompts/CODEX-023.md codex-prompts/CODEX-024.md codex-prompts/CODEX-025.md codex-prompts/CODEX-026.md
git add RUNBOOK.md
git add LESSONS.md
git add codex-prompts/CODEX-CLEANUP.md
```

Також додай будь-які інші змінені або нові файли, якщо вони стосуються проєкту (наприклад tasks/*-report.md). Не додавай .DS_Store та інше сміття.

```bash
git status
```

Переконайся що все потрібне додано. Потім:

```bash
git commit -m "Add task specs 018-026, codex prompts, and runbook"
git push origin main
```

## Крок 2: змерджити відкриті PR

Перевір які PR відкриті:

```bash
gh pr list
```

Для кожного відкритого PR по черзі (якщо є):

```bash
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

Якщо merge conflict — зроби rebase:

```bash
gh pr checkout <НОМЕР>
git fetch origin main
git rebase origin/main
# Якщо конфлікт: git checkout --theirs <файл> && git add <файл> && GIT_EDITOR="true" git rebase --continue
git push --force-with-lease
gh pr merge <НОМЕР> --merge
```

## Крок 3: виконати таски по порядку

Після того як робоче дерево чисте і main актуальний, виконуй таски строго в такому порядку:

019 → 020 → 021 → 022 → 023 → 024 → 025 → 026

(018 вже done)
(019 може бути вже done — перевір tasks/TASK-019.md, якщо Status: done — пропусти)

Для КОЖНОГО таску:

1. `git checkout main && git pull origin main` — ОБОВ'ЯЗКОВО перед кожним таском
2. Прочитай `CLAUDE.md`, потім `LESSONS.md`, потім `tasks/TASK-NNN.md`
3. Створи гілку: `git checkout -b task/NNN-назва`
4. Зроби роботу згідно з таском
5. Закоміть: `git add ... && git commit -m "[TASK-NNN] Опис"`
6. Запуш: `git push -u origin task/NNN-назва`
7. Створи PR: `gh pr create --title "[TASK-NNN] Опис" --body "See tasks/TASK-NNN.md"`
8. Відразу змерджи: `gh pr merge --merge`
9. Напиши звіт у `tasks/TASK-NNN-report.md`
10. Переходь до наступного таску (починай з пункту 1)

## ВАЖЛИВО

- ЗАВЖДИ починай з `git checkout main && git pull origin main`
- Не працюй на брудному дереві
- Не пропускай pull перед створенням нової гілки
- Якщо бачиш untracked files від інших тасків — це нормально, не чіпай їх, просто працюй над своїм таском
- Кожен таск = окрема гілка від СВІЖОГО main
