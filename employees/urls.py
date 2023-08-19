from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sites", views.sites, name="sites"),
    path("create_site", views.create_site, name="create_site"),
    path("delete_site/<int:site_pk>/", views.delete_site, name="delete_site"),
    path("update_site/<int:site_pk>/", views.update_site, name="update_site"),
    path("managers", views.managers, name="managers"),
    path("create_manager", views.create_manager, name="create_manager"),
    path(
        "update_manager/<int:manager_pk>/", views.update_manager, name="update_manager"
    ),
    path(
        "delete_manager/<int:manager_pk>/", views.delete_manager, name="delete_manager"
    ),
    path("employees", views.employees, name="employees"),
    path("create_employee", views.create_employee, name="create_employee"),
    path(
        "update_employee/<int:employee_pk>/",
        views.update_employee,
        name="update_employee",
    ),
    path(
        "delete_employee/<int:employee_pk>/",
        views.delete_employee,
        name="delete_employee",
    ),
    path("payslips", views.payslips, name="payslips"),
    path("labels", views.labels, name="labels"),
    path("create_label", views.create_label, name="create_label"),
    path("delete_label/<int:label_pk>/", views.delete_label, name="delete_label"),
    path("update_label/<int:label_pk>/", views.update_label, name="update_label"),
]
