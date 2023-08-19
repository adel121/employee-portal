from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User, UserAdmin)
# Register your models here.

from .models import Employee, Site, WorkSlot, Administrator, Manager, EmployeeLabel

admin.site.register(Employee)
admin.site.register(Site)
admin.site.register(WorkSlot)
admin.site.register(Administrator)
admin.site.register(Manager)
admin.site.register(EmployeeLabel)
