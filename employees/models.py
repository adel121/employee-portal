from django.db import models
from django.core import validators
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from .utils import get_last_seven_dates
from django.db.models import Q
from datetime import date, timedelta, datetime


class Site(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name + " : " + self.address


class Employee(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING)
    hourly_rate = models.DecimalField(
        decimal_places=2,
        max_digits=12,
    )
    overtime_factor = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=1,
        validators=[validators.MinValueValidator(Decimal("0.00"))],
    )

    def __str__(self) -> str:
        return self.name + " : " + self.phone_number

    def missing_registrations(self):
        today = date.today()
        last_week = today - timedelta(days=7)
        missing_registrations = get_last_seven_dates()

        workslots = WorkSlot.objects.filter(
            Q(employee=self) & Q(date__lte=today) & Q(date__gte=last_week)
        )
        for workslot in workslots:
            if workslot.is_closed:
                missing_registrations.remove(str(workslot.date))

        return missing_registrations
    
    @property
    def expected_daily_amount(self):
        return 9 * self.hourly_rate


class WorkSlot(models.Model):
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(
        decimal_places=2,
        max_digits=12,
    )
    overtime = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[validators.MinValueValidator(Decimal("0.00"))],
    )

    overtime_factor = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=1,
        validators=[validators.MinValueValidator(Decimal("0.00"))],
    )

    is_holiday = models.BooleanField(default=False)

    @property
    def is_closed(self):
        if self.is_holiday:
            return True
        if self.start_time is not None and self.end_time is not None:
            return True
        return False

    @property
    def total_hours(self):
        if not self.is_closed or self.is_holiday:
            return 0

    @property
    def normal_hours(self):
        if not self.is_closed or self.is_holiday:
            return 0
        start_datetime = datetime.combine(date.today(), self.start_time)
        end_datetime = datetime.combine(date.today(), self.end_time)
        total_working_hours = Decimal(
            (end_datetime - start_datetime).total_seconds() / 3600
        )
        return total_working_hours - self.break_hours - self.overtime

    @property
    def break_hours(self):
        if not self.is_closed or self.is_holiday:
            return 0
        return 1

    @property
    def amount(self):
        if not self.is_closed or self.is_holiday:
            return 0
        normal_pay = self.normal_hours * self.hourly_rate
        overtime_pay = self.overtime * self.hourly_rate * self.overtime_factor
        return normal_pay + overtime_pay

    def __str__(self) -> str:
        return self.date.__str__() + " : " + self.employee.name


class User(AbstractUser):
    def is_admin(self):
        return hasattr(self, "administrator")


class Administrator(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.account.username + " : " + self.phone_number


class Manager(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=200)
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.account.username + " : " + self.phone_number
