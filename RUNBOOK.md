# Що робити

Все виконуй з папки /Users/vb/l10n-pl-payroll

---

## TASK-018 (вже зроблений, треба змерджити)

```
cd /Users/vb/l10n-pl-payroll
git push --force-with-lease
gh pr merge 19 --merge
```

---

## TASK-019

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-019.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/019 і запамʼятай номер (перша колонка, наприклад #20)
6. В терміналі (замінивши 20 на свій номер):

```
gh pr ready 20 && gh pr merge 20 --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-020

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-020.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/020 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-021

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-021.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/021 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-022

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-022.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/022 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-023

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-023.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/023 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-024

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-024.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/024 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-025

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-025.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/025 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## TASK-026 (останній)

1. Відкрий Codex
2. Скопіюй вміст файлу /Users/vb/l10n-pl-payroll/codex-prompts/CODEX-026.md і вставь як промпт
3. Чекай поки Codex скаже що готово
4. В терміналі:

```
cd /Users/vb/l10n-pl-payroll
gh pr list
```

5. Знайди рядок з task/026 і запамʼятай номер
6. В терміналі:

```
gh pr ready <НОМЕР> && gh pr merge <НОМЕР> --merge
```

7. Має написати «Merged». Якщо помилка — зупинись, скопіюй помилку Claude.

---

## ВСЕ ГОТОВО

Коли всі 9 тасків змерджені, в терміналі:

```
cd /Users/vb/l10n-pl-payroll
git checkout main
git pull origin main
bash scripts/upgrade_module.sh
python3 scripts/seed_realistic_data.py
```

Напиши Claude: «все готово»

---

## ЯКЩО ПОМИЛКА

Зупинись. Скопіюй текст помилки. Напиши Claude.
