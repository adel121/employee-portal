from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, HttpResponse
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

    employees = Employee.objects.filter(sites__pk=request.user.manager.site.pk)

    if employee_pk != ALL_EMPLOYEES:
        employees = employees.filter(pk=employee_pk)

        if not employees or not EmployeeSiteAssignment.objects.filter(employee = employees.first(), site = request.user.manager.site).exists():
            return HttpResponseNotAllowed("Unauthorized Access")

    registration_type = request.POST.get("registration_type")
    date = request.POST.get("date")
    checkin_time = request.POST.get("checkin-time", None)
    checkout_time = request.POST.get("checkout-time", None)
    overtime = request.POST.get("overtime", 0)
    break_hours = request.POST.get("break_hours")
    site_pk = request.POST.get("site")
    site = Site.objects.get(pk = site_pk)

    workslot_registrar = WorkHourRegistrar(employees, date, overtime, break_hours, site)

    if registration_type == "Checkin":
        workslot_registrar.register_checkin(checkin_time)
    elif registration_type == "Checkout":
        workslot_registrar.register_checkout(checkout_time)
    elif registration_type == "Checkin-Checkout":
        workslot_registrar.register_checkin_checkout(checkin_time, checkout_time)
    else:
        workslot_registrar.register_holiday()

    employees = Employee.objects.filter(sites__pk=request.user.manager.site.pk)
    missing_registrations = get_missing_registrations(employees)

    return render(
        request,
        "employees/index.html",    
        {"employees": employees, "sites": [request.user.manager.site],"missing_registrations": missing_registrations},
    )


def register_work_hours_as_admin(request):
    employee_pk = request.POST.get("employee")
    registration_type = request.POST.get("registration_type")
    date = request.POST.get("date")
    checkin_time = request.POST.get("checkin-time", None)
    checkout_time = request.POST.get("checkout-time", None)
    overtime = request.POST.get("overtime", 0)
    break_hours = request.POST.get("break_hours")
    site_pk = request.POST.get("site")
    site = Site.objects.get(pk = site_pk)

    employees = Employee.objects.all()

    if employee_pk != ALL_EMPLOYEES:
        employees = employees.filter(pk=employee_pk)

    workslot_registrar = WorkHourRegistrar(employees, date, overtime, break_hours, site)

    if registration_type == "Checkin":
        workslot_registrar.register_checkin(checkin_time)
    elif registration_type == "Checkout":
        workslot_registrar.register_checkout(checkout_time)
    elif registration_type == "Checkin-Checkout":
        workslot_registrar.register_checkin_checkout(checkin_time, checkout_time)
    else:
        workslot_registrar.register_holiday()


    employees = Employee.objects.all()
    missing_registrations = get_missing_registrations(employees)

    return render(
        request,
        "employees/index.html",
        {"employees": employees,"sites": Site.objects.all(), "missing_registrations": missing_registrations},
    )


@login_required
def index(request):
    employees = Employee.objects.all()
    sites = Site.objects.all()

    if request.method == "GET":
        if not request.user.is_admin():
            sites = [request.user.manager.site]
            employees = employees.filter(sites__pk=request.user.manager.site.pk)
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
                "sites": sites
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
            related_managers = Manager.objects.filter(site=site)
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
        if "UNIQUE constraint" in e.args[0]:
            return "Employee phone number already exists, choose another phone number"
        else:
            return "Operation failed, contact the administrator"


@login_required
def employees(request):
    employees_with_salary = list()

    if not request.user.is_admin():
        site = request.user.manager.site
        all_assignments = EmployeeSiteAssignment.objects.filter(site__pk = site.pk)
        for assignment in all_assignments:
            employees_with_salary.append((assignment.employee, assignment.daily_rate))
    else:
        employees = Employee.objects.all()
        for employee in employees:
            employees_with_salary.append((employee, 0))

    return render(
        request, "employees/employees/employees.html", {"employees_with_salary": employees_with_salary}
    )



def attach_employee_to_site(employee, site, daily_rate = -1):
    """
    This function adds an existing employee to an existing site.
    """
    
    assignment = EmployeeSiteAssignment.objects.filter(employee=employee, site=site)
    if not assignment:
        assignment = EmployeeSiteAssignment()
    else:
        assignment = assignment.first()

    assignment.employee = employee
    assignment.site = site
    assignment.daily_rate = daily_rate
    
    error = ""
    try:
        assignment.save()
    except Exception as e:
        error = "Failed to add " + employee.name + " to " + site.name + " site."
    return error


@login_required
def create_employee_as_manager(request):
    # Parse post data
    employee_name = request.POST.get("name")
    employee_phone_number = request.POST.get("phone_number")
    employee_label= request.POST.get("label")
    
    
    # Check if employee phone_number already exists
    employee = Employee.objects.filter(phone_number = employee_phone_number)
    if employee:
        # phone_number already in use
        employee = employee.first()
        employee.name = employee_name
        employee.label = EmployeeLabel.objects.get(pk=employee_label)
        error = save_employee(employee)

        if error == "":
            error = attach_employee_to_site(employee, request.user.manager.site)

        if error != "":
            return render(
                request,
                "employees/employees/create-employee.html",
                {"sites": [request.user.manager.site], "error": error, "employee": employee, "labels": EmployeeLabel.objects.all()},
            )
        else:
            return redirect(employees)

    
    # phone_number doesn't exist yet
    employee = Employee()
    employee.name = employee_name
    employee.phone_number = employee_phone_number
    
    employee.label = EmployeeLabel.objects.get(pk=employee_label)
   
    labels = EmployeeLabel.objects.all()

    error = save_employee(employee)
    if error == "":
        attach_employee_to_site(employee, request.user.manager.site)

    if error != "":
        return render(
            request,
            "employees/employees/create-employee.html",
            {"sites": [request.user.manager.site], "error": error, "employee": employee, "labels": labels},
        )
    else:
        return redirect(employees)
        

@login_required
def create_employee_as_admin(request):
    employee_name = request.POST.get("name")
    employee_phone_number = request.POST.get("phone_number")
    employee_label= request.POST.get("label")
    employee_overtime_factor = request.POST.get("overtime_factor")

    daily_rates = list()

    for site in Site.objects.all():
        daily_rate = request.POST.get(site.name + ".daily-rate")
        if daily_rate == "":
            continue
        daily_rates.append((site, Decimal(daily_rate)))

    employee = Employee()
    employee.name = employee_name
    employee.phone_number = employee_phone_number
    employee.overtime_factor = employee_overtime_factor
    employee.label = EmployeeLabel.objects.get(pk=employee_label)

    labels = EmployeeLabel.objects.all()

    error = save_employee(employee)

    if error == "":
        for daily_rate in daily_rates:
            error = attach_employee_to_site(employee ,daily_rate[0], daily_rate[1])
            if error != "":
                break
    sites = Site.objects.all()
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
    employee_label= request.POST.get("label")
    employee_overtime_factor = request.POST.get("overtime_factor")

    daily_rates = list()

    for site in Site.objects.all():
        daily_rate = request.POST.get(site.name + ".daily-rate", "")
        if daily_rate == "":
            EmployeeSiteAssignment.objects.filter(employee = employee, site = site).delete()
            continue
        daily_rates.append((site, Decimal(daily_rate)))


    employee.name = employee_name
    employee.phone_number = employee_phone_number
    employee.overtime_factor = employee_overtime_factor
    employee.label = EmployeeLabel.objects.get(pk=employee_label)

    labels = EmployeeLabel.objects.all()

    error = save_employee(employee)

    if error == "":
        for daily_rate in daily_rates:
            error = attach_employee_to_site(employee ,daily_rate[0], daily_rate[1])
            if error != "":
                break
    if error != "":
        return render(
            request,
            "employees/employees/update-employee.html",
            {"sites_with_daily_rates": employee.get_sites_daily_rates(), "error": error, "employee": employee, "labels": labels},
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
            "employees/employees/update-employee.html",
            {"error": error, "sites_with_daily_rates": employee.get_sites_daily_rates(), "employee": employee, "labels": labels},
        )

    return redirect(employees)


@login_required
def update_employee(request, employee_pk):
    if request.method == "GET":
        labels = EmployeeLabel.objects.all()
        employee = Employee.objects.get(pk = employee_pk)
        return render(
            request,
            "employees/employees/update-employee.html",
            {
                "error": "",
                "sites_with_daily_rates": employee.get_sites_daily_rates(),
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
        if not EmployeeSiteAssignment.objects.filter(employee = employee, site = request.user.manager.site).exists():
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
        employees = employees.filter(sites__pk=user.manager.site.pk)

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
        mode = request.POST.get("mode")
        mark_as_paid = mode == MARK_AS_PAID

        if not user.is_admin():
            if not EmployeeSiteAssignment.objects.filter(employee= employee, site=user.manager.site).exists():
                return HttpResponseNotAllowed("Unauthorized Access")

        payslip_generator = PayslipGenerator(employee, from_date, to_date, mark_as_paid)
        return payslip_generator.generate_payslip()
