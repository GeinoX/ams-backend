"""
from django.contrib import admin
from .models import Student, Lecturer, Staff, CustomUser
from notifications.services.notification_service import NotificationService
import secrets
import string

# Register your models here.

def generate_temporary_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class StudentAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # only on creation, not update
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            NotificationService.account_credentials(obj.user, temporary_password)  # ← called here
        super().save_model(request, obj, form, change)


class LecturerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # only on creation
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            NotificationService.account_credentials(obj.user, temporary_password)  # ← called here
        super().save_model(request, obj, form, change)


class StaffAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # only on creation
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            NotificationService.account_credentials(obj.user, temporary_password)  # ← called here
        super().save_model(request, obj, form, change)


admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Staff, StaffAdmin)
"""