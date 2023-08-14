from employees.models import *

site = Site.objects.get(name="Beirut")


def create_employee(name):
    employee = Employee()
    employee.name = name
    employee.hourly_rate = 43342
    employee.site = site
    employee.phone_number = "1323"
    employee.save()


for i in range(600):
    create_employee("employee_" + str(i))
