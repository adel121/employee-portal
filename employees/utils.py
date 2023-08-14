from datetime import date, timedelta
from .models import *


def get_last_seven_dates():
    today = date.today()
    dates = set()
    for shift in range(8):
        current_date = str(today - timedelta(days=shift))
        dates.add(current_date)
    return dates


def get_missing_registrations(employees):
    result = []
    number_of_missing_registrations = 0

    for employee in employees:
        if number_of_missing_registrations > 20:
            break
        employee_missing_registrations = employee.missing_registrations()
        number_of_missing_registrations += len(employee_missing_registrations)
        result.append((employee, employee_missing_registrations))

    return result
