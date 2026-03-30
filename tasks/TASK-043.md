# TASK-043: hr_attendance overtime sync + traceability

**Status:** done
**Phase:** 6 — Component Constructor
**Depends on:** —
**Architecture:** ARCHITECTURE-PHASE6.md § 5

## What

Add a "Synchronize with attendance" button on the payslip that pulls overtime hours from `hr.attendance` records. Maintain traceability: track when sync happened, flag manual overrides.

## Deliverables

### 1. New fields on `pl.payroll.payslip`

```python
attendance_synced = fields.Boolean("Zsynchronizowano z ewidencją", default=False)
attendance_sync_date = fields.Datetime("Data ostatniej synchronizacji")
overtime_manual_override = fields.Boolean("Ręczna korekta nadgodzin", default=False)
attendance_worked_hours = fields.Float("Godziny z ewidencji", readonly=True,
    help="Suma godzin przepracowanych wg ewidencji czasu pracy.")
attendance_scheduled_hours = fields.Float("Godziny planowane", readonly=True,
    help="Suma godzin wg harmonogramu pracy w okresie listy płac.")
```

### 2. Method: `action_sync_attendance()`

1. Check if `hr.attendance` model exists (soft dependency)
2. Search attendances for employee + period (check_in between date_from and date_to)
3. Calculate total worked hours from attendance
4. Calculate scheduled hours from employee's resource calendar
5. Calculate overtime = worked - scheduled (min 0)
6. Split overtime into 150% and 200%:
   - 200% = hours worked on Sundays, public holidays, night hours (22:00-06:00)
   - 150% = all other overtime
   - For MVP: put all overtime as 150% and let user split manually. Flag with TODO for future enhancement.
7. Write overtime_hours_150, overtime_hours_200
8. Set attendance_synced=True, attendance_sync_date=now

### 3. Onchange for manual override detection

When user changes `overtime_hours_150` or `overtime_hours_200` after sync:
- Set `overtime_manual_override = True`

### 4. Button in form view

Add "Synchronizuj nadgodziny" button in form header (visible when state=draft and hr_attendance installed).

Warning indicator when `overtime_manual_override = True`: "Nadgodziny zmienione ręcznie po synchronizacji"

### 5. Batch sync

Add method `action_batch_sync_attendance()` that works on recordset.
Add server action for list/grid view: "Synchronizuj nadgodziny" on selected payslips.

### 6. __manifest__.py

DO NOT add hr_attendance to `depends`. Use soft import:
```python
try:
    from odoo.addons.hr_attendance.models.hr_attendance import HrAttendance
    HAS_ATTENDANCE = True
except ImportError:
    HAS_ATTENDANCE = False
```

Or better: check `self.env.registry.get('hr.attendance')` at runtime.

## Overtime split rules (Polish law)

Per Kodeks pracy art. 151¹:
- 100% additional (= 200% total): night hours, Sundays, holidays, days off given for Sunday work
- 50% additional (= 150% total): all other overtime

For MVP, calculating night/holiday hours from attendance requires more data (public holiday calendar, night shift definition). **Start with total overtime only, let user split manually. Log this as future enhancement.**

## Don't

- Don't make hr_attendance a hard dependency
- Don't auto-compute payslip after sync (user triggers manually)
- Don't try to implement full 150/200 split algorithm in MVP — manual split is fine
