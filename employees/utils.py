from datetime import date, timedelta

def get_last_seven_dates():
    today = date.today()
    dates = set()
    for shift in range(8):
        current_date = str(today - timedelta(days=shift))
        dates.add(current_date)
    return dates


def get_missing_registrations(employees, site = None):
    from .models import EmployeeSiteAssignment
    result = []
    number_of_missing_registrations = 0

    for employee in employees:
        if number_of_missing_registrations > 20:
            break

        assignments = EmployeeSiteAssignment.objects.filter(employee=employee, daily_rate__lt = 0)

        if site is not None:
            assignments = assignments.filter(site = site)

        employee_missing_registrations = list(employee.missing_registrations())

        missing_site = ""

        if assignments:
            missing_site = assignments.first().site.name

        employee_missing_registrations.sort(reverse=True)
        number_of_missing_registrations += len(employee_missing_registrations)
        if len(employee_missing_registrations) > 0:
            result.append((employee, employee_missing_registrations, missing_site))

    return result
