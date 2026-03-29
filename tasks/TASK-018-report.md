# TASK-018 Report

- Додано поле `is_student` у `hr.employee` і чекбокс у формі працівника.
- У `pl.payroll.payslip` додано перевірку студента до 26 років на `umowa zlecenie`.
- Для таких payslip ZUS, zdrowotne і PPK обнулюються; `umowa o pracę` не змінюється.
- Додано 4 тести: студент на `zlecenie`, студент на `o pracę`, не студент на `zlecenie`, перехід через 26 років.
- Оновлено `scripts/seed_realistic_data.py`: додано Jakub Wiśniewski і Oliwia Kowalska як студентів на `zlecenie` та перевірку, що їхній ZUS = 0.
