# Lessons — Mistakes That Must Not Repeat

> Read this at the start of every session, right after STATE.md.

## Entries

[payroll]: Polish PIT is calculated cumulatively over the year, not per-month independently. Each month's PIT must account for all previous months' income in that tax year. Getting this wrong = every payslip after January is incorrect.

[payroll]: ZUS basis cap (roczna podstawa wymiaru skladek) resets annually. After exceeding the cap (282,600 PLN in 2026), pension + disability contributions stop but health insurance continues. Must track cumulative gross per employee per year.

[payroll]: PPK employer contribution is taxable income for the employee (PIT). PPK employee contribution is NOT a tax-deductible cost. These are asymmetric — don't treat them the same.

[compliance]: Autorskie koszty (50% KUP) cannot be applied automatically. Requires explicit documentation in employment contract specifying the % of creative work. Without contract proof, KAS will disallow and impose penalties.

[data]: Never put real employee data (PESEL, names, salaries) in test files, commits, or GitHub. Use fictional data with valid-format-but-invalid-checksum PESEL numbers.

[odoo]: Don't assume Odoo Enterprise features are available. Verify the exact version and edition before using any payroll-related API.

[process]: Авторські koszty (50% KUP) потребують не лише прапорця в контракті, а й щомісячного звіту працівника про творчу діяльність. Це документальне підтвердження для KAS. Модуль має це враховувати (хоча б поле для зберігання/відстеження звіту).

[workflow]: Повідомлення для Асі = блокер. Розробку вести повністю автономно на фіктивних даних. Не створювати залежностей від зовнішньої агенції чи CFO під час development phase.

[payroll]: КРИТИЧНО — формула авторських KUP: **KUP = 50% × creative_share% × health_basis**. Поле `kup_autorskie_pct` — це відсоток творчої роботи (50%, 80%), а НЕ ставка KUP. Ставка авторських KUP завжди = 50% (фіксована законом). Помилка: якщо сплутати creative_share зі ставкою KUP, результат подвоюється. Виявлено 2026-03-28 під час рев'ю TASK-004.

[process]: Перед тим як «виправляти» розрахунки Codex — верифікуй СВОЮ формулу спочатку. PR #5 вніс неправильні дані через помилку оркестратора, а не кодера.
