from .models import *
from .utils import *


class WorkHourRegistrar:
    def __init__(self, employees, date, overtime, break_hours, site):
        self.employees = employees
        self.date = date
        self.break_hours = break_hours
        self.site = site
        self.overtime = overtime
        self.workslots_to_update = []
        self.workslots_to_create = []

        for employee in employees:
            assignment = EmployeeSiteAssignment.objects.filter(employee=employee, site= site)
            if not assignment:
                continue

            if assignment.first().hourly_rate < 0:
                continue
            workslot = WorkSlot()
            if WorkSlot.objects.filter(employee=employee, site=site, date=self.date).exists():
                workslot = WorkSlot.objects.filter(
                    employee=employee, date=self.date
                ).first()
                workslot.overtime = overtime
                workslot.is_paid = False
                workslot.break_hours = self.break_hours
                workslot.payment_date = None
                self.workslots_to_update.append(workslot)
            else:
                workslot.employee = employee
                assignment = assignment.first()
                workslot.hourly_rate = assignment.hourly_rate
                workslot.overtime_factor = employee.overtime_factor
                workslot.date = date
                workslot.site = site
                workslot.overtime = overtime
                workslot.break_hours = self.break_hours
                self.workslots_to_create.append(workslot)

    def register_checkin(self, time):
        for workslot in self.workslots_to_update:
            workslot.start_time = time
            workslot.is_holiday = False
        for workslot in self.workslots_to_create:
            workslot.start_time = time
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["start_time", "overtime", "is_holiday", "is_paid", "break_hours", "payment_date"],
            batch_size=1000,
        )

    def register_checkout(self, time):
        for workslot in self.workslots_to_update:
            workslot.end_time = time
            workslot.is_holiday = False
        for workslot in self.workslots_to_create:
            workslot.end_time = time
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["end_time", "overtime", "is_holiday", "is_paid", "break_hours", "payment_date"],
            batch_size=1000,
        )

    def register_checkin_checkout(self, start_time, end_time):
        for workslot in self.workslots_to_update:
            workslot.start_time = start_time
            workslot.end_time = end_time
            workslot.is_holiday = False
        for workslot in self.workslots_to_create:
            workslot.start_time = start_time
            workslot.end_time = end_time
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["start_time", "end_time", "overtime", "is_holiday", "is_paid", "break_hours", "payment_date"],
            batch_size=1000,
        )        

    def register_holiday(self):
        for workslot in self.workslots_to_update:
            if workslot.hourly_rate < 0:
                continue
            workslot.is_holiday = True
            workslot.start_time = None
            workslot.end_time = None
            workslot.overtime = 0
        for workslot in self.workslots_to_create:
            if workslot.hourly_rate < 0:
                continue
            workslot.is_holiday = True
        WorkSlot.objects.bulk_create(self.workslots_to_create, batch_size=1000)
        WorkSlot.objects.bulk_update(
            self.workslots_to_update,
            ["start_time","end_time", "overtime", "is_holiday", "is_paid", "break_hours", "payment_date"],
            batch_size=1000,
        )
