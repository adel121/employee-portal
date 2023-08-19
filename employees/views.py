from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.db import IntegrityError
from .models import *
from .work_hours_registrar import WorkHourRegistrar
from .payslip_generator import PayslipGenerator
from .constants import *
from .utils import *
from django.contrib.auth.decorators import login_required


#################################################################################
#                                                                               #
#                              Index Views                                      #
#                                                                               #
#################################################################################


def register_work_hours_as_manager(request):
    employee_pk = request.POST.get("employee")

    employees = Employee.objects.filter(site=request.user.manager.site)

    if employee_pk != ALL_EMPLOYEES:
        employee = Employee.objects.get(pk=employee_pk)
        employees = employees.filter(pk=employee_pk)

        if employee.site != request.user.manager.site:
            return HttpResponseNotAllowed("Unauthorized Access")

    registration_type = request.POST.get("registration_type")
    date = request.POST.get("date")
    time = request.POST.get("time", None)
    overtime = request.POST.get("overtime", 0)

    workslot_registrar = WorkHourRegistrar(employees, date, overtime)

    if registration_type == "Checkin":
        workslot_registrar.register_checkin(time)
    elif registration_type == "Checkout":
        workslot_registrar.register_checkout(time)
    else:
        workslot_registrar.register_holiday()

    employees = Employee.objects.all().filter(site=request.user.manager.site)
    missing_registrations = get_missing_registrations(employees)
    return render(
        request,
        "employees/index.html",
        {"employees": employees, "missing_registrations": missing_registrations},
    )


def register_work_hours_as_admin(request):
    employee_pk = request.POST.get("employee")
    registration_type = request.POST.get("registration_type")
    date = request.POST.get("date")
    time = request.POST.get("time", None)
    overtime = request.POST.get("overtime", 0)

    employees = Employee.objects.all()

    if employee_pk != ALL_EMPLOYEES:
        employees = employees.filter(pk=employee_pk)

    workslot_registrar = WorkHourRegistrar(employees, date, overtime)

    if registration_type == "Checkin":
        workslot_registrar.register_checkin(time)
    elif registration_type == "Checkout":
        workslot_registrar.register_checkout(time)
    else:
        workslot_registrar.register_holiday()

    employees = Employee.objects.all()
    missing_registrations = get_missing_registrations(employees)

    return render(
        request,
        "employees/index.html",
        {"employees": employees, "missing_registrations": missing_registrations},
    )


@login_required
def index(request):
    employees = Employee.objects.all()

    if request.method == "GET":
        if not request.user.is_admin():
            employees = employees.filter(site=request.user.manager.site)
        employee_pk = int(request.GET.get("emp_pk", -1))
        date = request.GET.get("date", "")

        missing_registrations = get_missing_registrations(employees)

        return render(
            request,
            "employees/index.html",
            {
                "employees": employees,
                "prefill_employee_pk": employee_pk,
                "prefill_date": date,
                "missing_registrations": missing_registrations,
            },
        )
    else:
        if request.user.is_admin():
            return register_work_hours_as_admin(request)
        else:
            return register_work_hours_as_manager(request)


#################################################################################
#                                                                               #
#                              Sites Views                                      #
#                                                                               #
#################################################################################


def save_site(site: Site):
    try:
        site.save()
        return ""
    except IntegrityError as e:
        print(e.args)
        if "UNIQUE constraint" in e.args[0]:
            return "Site name already exists, choose another name"
        else:
            return "Operation failed, contact the administrator"


@login_required
def sites(request):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")
    all_sites = Site.objects.all()
    return render(request, "employees/sites/sites.html", {"sites": all_sites})


@login_required
def create_site(request):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    if request.method == "GET":
        return render(request, "employees/sites/create-site.html", {"error": ""})
    else:
        site_name = request.POST.get("name")
        site_address = request.POST.get("address")
        new_site = Site()
        new_site.name = site_name
        new_site.address = site_address
        error = save_site(new_site)
        if error != "":
            return render(request, "employees/sites/create-site.html", {"error": error})
        return redirect(sites)


@login_required
def delete_site(request, site_pk):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    site = Site.objects.get(pk=site_pk)

    if request.method == "GET":
        return render(request, "employees/sites/delete-site.html", {"site": site})
    else:
        if request.POST.get("delete_confirmation", "NO") == "YES":
            related_employees = Employee.objects.filter(site=site)
            related_managers = Manager.objects.filter(site=site)
            print(related_managers)
            related_employees.delete()
            related_managers.delete()
            site.delete()
        return redirect(sites)


@login_required
def update_site(request, site_pk):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    site = Site.objects.get(pk=site_pk)

    if request.method == "GET":
        return render(
            request, "employees/sites/update-site.html", {"site": site, "error": ""}
        )
    else:
        site_name = request.POST.get("name")
        site_address = request.POST.get("address")
        site.name = site_name
        site.address = site_address
        error = save_site(site)
        if error != "":
            return render(
                request,
                "employees/sites/update-site.html",
                {"site": site, "error": error},
            )
        return redirect(sites)

#################################################################################
#                                                                               #
#                              Label Views                                      #
#                                                                               #
#################################################################################


def save_label(site: Site):
    try:
        site.save()
        return ""
    except IntegrityError as e:
        print(e.args)
        if "UNIQUE constraint" in e.args[0]:
            return "Label name already exists, choose another name"
        else:
            return "Operation failed, contact the administrator"


@login_required
def labels(request):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")
    all_labels = EmployeeLabel.objects.all()
    return render(request, "employees/labels/labels.html", {"labels": all_labels})


@login_required
def create_label(request):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    if request.method == "GET":
        return render(request, "employees/labels/create-label.html", {"error": ""})
    else:
        label_name = request.POST.get("name")
        label_normal_working_hours = request.POST.get("normal_working_hours")
        new_label = EmployeeLabel()
        new_label.name = label_name
        new_label.normal_working_hours = label_normal_working_hours
        error = save_label(new_label)
        if error != "":
            return render(request, "employees/labels/create-label.html", {"error": error})
        return redirect(labels)


@login_required
def delete_label(request, label_pk):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    label = EmployeeLabel.objects.get(pk=label_pk)

    if request.method == "GET":
        return render(request, "employees/labels/delete-label.html", {"label": label})
    else:
        if request.POST.get("delete_confirmation", "NO") == "YES":
            related_employees = Employee.objects.filter(label=label)
            related_employees.delete()
            label.delete()
        return redirect(labels)


@login_required
def update_label(request, label_pk):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    label = EmployeeLabel.objects.get(pk=label_pk)

    if request.method == "GET":
        return render(
            request, "employees/labels/update-label.html", {"label": label, "error": ""}
        )
    else:
        label_name = request.POST.get("name")
        label_normal_working_hours = request.POST.get("normal_working_hours")
        label.name = label_name
        label.normal_working_hours = label_normal_working_hours
        error = save_label(label)
        if error != "":
            return render(
                request,
                "employees/labels/update-label.html",
                {"label": label, "error": error},
            )
        return redirect(labels)

#################################################################################
#                                                                               #
#                              Managers Views                                   #
#                                                                               #
#################################################################################


def save_manager(manager: Manager):
    try:
        manager.account.save()
        manager.save()
        return ""
    except IntegrityError as e:
        print(e.args)
        if "UNIQUE constraint" in e.args[0]:
            return "Username already exists, choose another username"
        else:
            return "Operation failed, contact the administrator"


@login_required
def managers(request):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")
    all_managers = Manager.objects.all()
    return render(
        request, "employees/managers/managers.html", {"managers": all_managers}
    )


@login_required
def create_manager(request):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    sites = Site.objects.all()

    if request.method == "GET":
        return render(
            request,
            "employees/managers/create-manager.html",
            {"sites": sites, "error": ""},
        )
    else:
        manager_name = request.POST.get("name")
        manager_phone_number = request.POST.get("phone_number")
        manager_username = request.POST.get("username")
        manager_password = request.POST.get("password")
        manager_confirm_password = request.POST.get("confirm_password")
        manager_site_pk = request.POST.get("site")

        account = User()
        account.first_name = manager_name
        account.username = manager_username
        account.set_password(manager_password)

        manager = Manager()
        manager.account = account
        manager.site = Site.objects.get(pk=manager_site_pk)
        manager.phone_number = manager_phone_number

        if manager_password != manager_confirm_password:
            return render(
                request,
                "employees/managers/create-manager.html",
                {"sites": sites, "error": "Passwords don't match", "manager": manager},
            )

        error = save_manager(manager)
        if error != "":
            return render(
                request,
                "employees/managers/create-manager.html",
                {"sites": sites, "error": error, "manager": manager},
            )
        return redirect(managers)


@login_required
def update_manager(request, manager_pk):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    manager = Manager.objects.get(pk=manager_pk)
    sites = Site.objects.all()

    if request.method == "GET":
        return render(
            request,
            "employees/managers/update-manager.html",
            {"sites": sites, "manager": manager, "error": ""},
        )
    else:
        manager_name = request.POST.get("name")
        manager_phone_number = request.POST.get("phone_number")
        manager_username = request.POST.get("username")
        manager_password = request.POST.get("password")
        manager_confirm_password = request.POST.get("confirm_password")
        manager_site_pk = request.POST.get("site")

        account = manager.account
        account.first_name = manager_name
        account.username = manager_username
        account.set_password(manager_password)

        manager.site = Site.objects.get(pk=manager_site_pk)
        manager.phone_number = manager_phone_number

        if manager_password != manager_confirm_password:
            return render(
                request,
                "employees/managers/update-manager.html",
                {"sites": sites, "error": "Passwords don't match", "manager": manager},
            )

        error = save_manager(manager)
        if error != "":
            return render(
                request,
                "employees/managers/update-manager.html",
                {"sites": sites, "error": error, "manager": manager},
            )
        return redirect(managers)


@login_required
def delete_manager(request, manager_pk):
    if not request.user.is_admin():
        return HttpResponseNotAllowed("Unauthorized Access")

    manager = Manager.objects.get(pk=manager_pk)

    if request.method == "GET":
        return render(
            request, "employees/managers/delete-manager.html", {"manager": manager}
        )
    else:
        if request.POST.get("delete_confirmation", "NO") == "YES":
            manager.account.delete()
            manager.delete()
        return redirect(managers)


#################################################################################
#                                                                               #
#                              Employees Views                                  #
#                                                                               #
#################################################################################


def save_employee(employee: Employee):
    try:
        employee.save()
        return ""
    except IntegrityError as e:
        print(e.args)
        if "UNIQUE constraint" in e.args[0]:
            return "Employee phone number already exists, choose another phone number"
        else:
            return "Operation failed, contact the administrator"


@login_required
def employees(request):
    all_employees = Employee.objects.all()

    if not request.user.is_admin():
        site = request.user.manager.site
        all_employees = all_employees.filter(site=site)

    return render(
        request, "employees/employees/employees.html", {"employees": all_employees}
    )


@login_required
def create_employee_as_manager(request):
    employee_name = request.POST.get("name")
    employee_phone_number = request.POST.get("phone_number")
    employee_label= request.POST.get("label")
    employee_site = request.user.manager.site
    employee_daily_rate = -1

    employee = Employee()
    employee.name = employee_name
    employee.phone_number = employee_phone_number
    employee.site = employee_site
    employee.daily_rate = employee_daily_rate
    employee.label = EmployeeLabel.objects.get(pk=employee_label)

    labels = EmployeeLabel.objects.all()

    error = save_employee(employee)
    if error != "":
        return render(
            request,
            "employees/employees/create-employee.html",
            {"sites": sites, "error": error, "employee": employee, "labels": labels},
        )
    return redirect(employees)


@login_required
def create_employee_as_admin(request):
    employee_name = request.POST.get("name")
    employee_phone_number = request.POST.get("phone_number")
    employee_site_pk = request.POST.get("site")
    employee_daily_rate = request.POST.get("daily_rate")
    employee_label= request.POST.get("label")
    employee_overtime_factor = request.POST.get("overtime_factor")

    employee = Employee()
    employee.name = employee_name
    employee.phone_number = employee_phone_number
    employee.site = Site.objects.get(pk=employee_site_pk)
    employee.daily_rate = employee_daily_rate
    employee.overtime_factor = employee_overtime_factor
    employee.label = EmployeeLabel.objects.get(pk=employee_label)

    labels = EmployeeLabel.objects.all()

    error = save_employee(employee)
    if error != "":
        return render(
            request,
            "employees/employees/create-employee.html",
            {"sites": sites, "error": error, "employee": employee, "labels": labels},
        )
    return redirect(employees)


@login_required
def create_employee(request):
    sites = Site.objects.all()

    if request.method == "GET":
        labels = EmployeeLabel.objects.all()
        return render(
            request,
            "employees/employees/create-employee.html",
            {"sites": sites, "labels": labels, "error": ""},
        )
    else:
        user = request.user
        if user.is_admin():
            return create_employee_as_admin(request)
        else:
            return create_employee_as_manager(request)


@login_required
def update_employee_as_admin(request, employee_pk):
    employee = Employee.objects.get(pk=employee_pk)

    employee_name = request.POST.get("name")
    employee_phone_number = request.POST.get("phone_number")
    employee_site_pk = request.POST.get("site")
    employee_daily_rate = request.POST.get("daily_rate")
    employee_overtime_factor = request.POST.get("overtime_factor")
    employee_label= request.POST.get("label")

    employee.name = employee_name
    employee.phone_number = employee_phone_number
    employee.site = Site.objects.get(pk=employee_site_pk)
    employee.daily_rate = employee_daily_rate
    employee.overtime_factor = employee_overtime_factor
    employee.label = EmployeeLabel.objects.get(pk=employee_label)

    labels = EmployeeLabel.objects.all()

    error = save_employee(employee)

    if error != "":
        return render(
            request,
            "employees/employees/update_employee.html",
            {"error": employee, "sites": Site.objects.all(), "employee": employee, "labels": labels},
        )

    return redirect(employees)


@login_required
def update_employee_as_manager(request, employee_pk):
    employee = Employee.objects.get(pk=employee_pk)

    employee_name = request.POST.get("name")
    employee_phone_number = request.POST.get("phone_number")
    employee_label= request.POST.get("label")

    employee.name = employee_name
    employee.phone_number = employee_phone_number
    employee.site = request.user.manager.site
    employee.label = EmployeeLabel.objects.get(pk=employee_label)

    labels = EmployeeLabel.objects.all()
    error = save_employee(employee)

    if error != "":
        return render(
            request,
            "employees/employees/update_employee.html",
            {"error": employee, "sites": Site.objects.all(), "employee": employee, "labels": labels},
        )

    return redirect(employees)


@login_required
def update_employee(request, employee_pk):
    sites = Site.objects.all()
    labels = EmployeeLabel.objects.all()

    if request.method == "GET":
        return render(
            request,
            "employees/employees/update_employee.html",
            {
                "error": "",
                "sites": sites,
                "labels": labels,
                "employee": Employee.objects.get(pk=employee_pk),
            },
        )
    else:
        user = request.user
        if user.is_admin():
            return update_employee_as_admin(request, employee_pk)
        else:
            return update_employee_as_manager(request, employee_pk)


@login_required
def delete_employee(request, employee_pk):
    employee = Employee.objects.get(pk=employee_pk)

    if not request.user.is_admin():
        if request.user.manager.site.pk != employee.site.pk:
            return HttpResponseNotAllowed("Unauthorized Access")

    if request.method == "GET":
        return render(
            request, "employees/employees/delete-employee.html", {"employee": employee}
        )
    else:
        if request.POST.get("delete_confirmation", "NO") == "YES":
            employee.delete()
        return redirect(employees)


#################################################################################
#                                                                               #
#                              payslip Views                                    #
#                                                                               #
#################################################################################


@login_required
def payslips(request):
    employees = Employee.objects.all()

    user = request.user

    if not request.user.is_admin():
        employees = employees.filter(site=user.manager.site)

    if request.method == "GET":
        return render(
            request,
            "employees/payslips/payslips.html",
            {"employees": employees},
        )
    else:
        employee_pk = request.POST.get("employee")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        employee = Employee.objects.get(pk=employee_pk)

        if not user.is_admin():
            if employee.site != user.manager.site:
                return HttpResponseNotAllowed("Unauthorized Access")

        payslip_generator = PayslipGenerator(employee, from_date, to_date)
        return payslip_generator.generate_payslip()
