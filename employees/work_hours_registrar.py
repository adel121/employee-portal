from .models import *
from .utils import *


class WorkHourRegistrar:
    def __init__(self, employees, date, overtime):
        self.employees = employees
        self.date = date
        self.overtime = overtime
        self.workslots_to_update = []
        self.workslots_to_create = []

        for employee in employees:
            if employee.hourly_rate < 0:
                continue
            workslot = WorkSlot()
            if WorkSlot.objects.filter(employee=employee, date=self.date).exists():
                workslot = WorkSlot.objects.filter(
                    employee=employee, date=self.date
                ).first()
                workslot.overtime = overtime
                self.workslots_to_update.append(workslot)
            else:
                workslot.employee = employee
                workslot.hourly_rate = employee.hourly_rate
                workslot.overtime_factor = employee.overtime_factor
                workslot.date = date
                workslot.overtime = overtime
                self.workslots_to_create.append(workslot)

    def register_checkin(self, time):
        for workslot in self.workslots_to_update:
            if workslot.employee.hourly_rate < 0:
                continue
            workslot.start_time = time
            workslot.is_holiday = False
        for workslot in self.workslots_to_create:
            if workslot.employee.hourly_rate < 0:
                continue
            workslot.start_time = time
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["start_time", "overtime", "is_holiday"],
            batch_size=1000,
        )

    def register_checkout(self, time):
        for workslot in self.workslots_to_update:
            if workslot.employee.hourly_rate < 0:
                continue
            workslot.end_time = time
            workslot.is_holiday = False
        for workslot in self.workslots_to_create:
            if workslot.employee.hourly_rate < 0:
                continue
            workslot.end_time = time
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["end_time", "overtime", "is_holiday"],
            batch_size=1000,
        )

    def register_holiday(self):
        for workslot in self.workslots_to_update:
            if workslot.employee.hourly_rate < 0:
                continue
            workslot.is_holiday = True
            workslot.start_time = None
            workslot.end_time = None
            workslot.overtime = 0
        for workslot in self.workslots_to_create:
            if workslot.employee.hourly_rate < 0:
                continue
            workslot.is_holiday = True
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["start_time","end_time", "overtime", "is_holiday"],
            batch_size=1000,
        )
