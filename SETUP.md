# Setup — покрокова інструкція

Копіюй і вставляй кожен блок у термінал по черзі.

## Крок 1: Створити репо на GitHub

```bash
gh repo create vitalibondar/l10n-pl-payroll --private --description "Polish Payroll module for Odoo 17+" --clone
cd l10n-pl-payroll
```

## Крок 2: Створити структуру

```bash
mkdir -p l10n_pl_payroll/{models,views,data,security,report,tests,wizard}
mkdir -p tasks tools
```

## Крок 3: .gitignore

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.idea/
.vscode/
*.egg-info/
dist/
build/
.env
*.log
EOF
```

## Крок 4: Заглушка модуля

```bash
cat > l10n_pl_payroll/__manifest__.py << 'EOF'
{
    "name": "Poland - Payroll",
    "version": "17.0.0.1.0",
    "category": "Human Resources/Payroll",
    "summary": "Polish payroll calculation and pay slip generation",
    "description": """
        Calculates gross-to-net salary for Polish employees.
        Supports umowa o pracę and umowa zlecenie.
        Generates pay slips (pasek wynagrodzeń).
    """,
    "author": "Om Energy Solutions",
    "website": "https://omenergysolutions.pl",
    "license": "LGPL-3",
    "depends": ["hr_contract", "hr_attendance"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
EOF

touch l10n_pl_payroll/__init__.py
touch l10n_pl_payroll/models/__init__.py
touch l10n_pl_payroll/tests/__init__.py
```

## Крок 5: Скопіювати проєктні файли

З папки, яку тобі дав Cowork (`odoo polish payroll/`), скопіюй у корінь репо:

```bash
# Шлях до файлів із Cowork — підстав свій, якщо відрізняється
COWORK_DIR="$HOME/odoo polish payroll"

cp "$COWORK_DIR/CLAUDE.md" .
cp "$COWORK_DIR/STATE.md" .
cp "$COWORK_DIR/PLAN.md" .
cp "$COWORK_DIR/DECISIONS.md" .
cp "$COWORK_DIR/LESSONS.md" .
cp "$COWORK_DIR/ODOO_RECON.md" .
cp "$COWORK_DIR/AGENTS.md" .
cp "$COWORK_DIR/SESSION.md" .
cp "$COWORK_DIR"/tasks/TASK-*.md tasks/
```

## Крок 6: Перший коміт і пуш

```bash
git add -A
git commit -m "Initial project structure with planning docs and module skeleton"
git push -u origin main
```

## Крок 7: Дати доступ Codex

Codex (ChatGPT) потребує доступу до репо:

```bash
# Якщо в тебе Codex через API/CLI — він вже бачить твої приватні репо
# Якщо потрібен доступ для іншого акаунта:
gh repo edit vitalibondar/l10n-pl-payroll --add-collaborator CODEX_USERNAME
```

## Крок 8: Повернись сюди й скинь посилання

Коли репо готове — скинь мені посилання:
`https://github.com/vitalibondar/l10n-pl-payroll`

Я перевірю структуру й дам Codex перше завдання.

---

## Тестова база Odoo (пізніше)

Для підключення до тестової бази знадобиться:
1. Назва бази (ODOO_DB) — зʼявиться після клонування на Odoo.sh
2. URL — зазвичай `https://DBNAME.odoo.com`
3. Логін/пароль

Це не блокує початок роботи — Codex почне з TASK-001 (дослідження) і TASK-002 (параметри), які не потребують Odoo.
