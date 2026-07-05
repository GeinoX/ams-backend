from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
import secrets
import string
from .models import (
    CustomUser, Faculty, Student, Lecturer,
    Staff, PasswordResetOTP
)


# Register your models here.

# ------- Helpers -------
def generate_temporary_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ------- Faculty -------
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


# ------- CustomUser -------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "school_email", "get_full_name", "gender",
        "phone", "faculty", "is_active", "is_staff",
        "must_change_password", "date_joined"
    ]
    list_filter = ["is_active", "is_staff", "gender", "faculty", "must_change_password"]
    search_fields = ["school_email", "first_name", "last_name", "phone"]
    ordering = ["last_name", "first_name"]
    readonly_fields = ["date_joined", "last_login", "profile_image_preview"]

    fieldsets = (
        (_("Credentials"), {
            "fields": ("school_email", "password")
        }),
        (_("Personal Info"), {
            "fields": (
                "first_name", "last_name", "email",
                "gender", "phone", "faculty",
                "profile_image", "profile_image_preview"
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_active", "is_staff", "is_superuser",
                "must_change_password", "groups", "user_permissions"
            )
        }),
        (_("Important Dates"), {
            "fields": ("date_joined", "last_login")
        }),
    )

    add_fieldsets = (
        (_("Credentials"), {
            "classes": ("wide",),
            "fields": (
                "school_email", "first_name", "last_name",
                "gender", "phone", "faculty", "email",
                "password1", "password2"
            )
        }),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "No image"
    profile_image_preview.short_description = "Profile Image Preview"


# ------- Student -------
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = "Student Profile"
    fields = ["matricule"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["matricule", "get_full_name", "get_school_email", "get_faculty"]
    search_fields = ["matricule", "user__first_name", "user__last_name", "user__school_email"]
    ordering = ["matricule"]
    readonly_fields = ["matricule"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"

    def get_school_email(self, obj):
        return obj.user.school_email
    get_school_email.short_description = "School Email"

    def get_faculty(self, obj):
        return obj.user.faculty
    get_faculty.short_description = "Faculty"

    def save_model(self, request, obj, form, change):
        if not change:  # on creation only
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            from notifications.services.notification_service import NotificationService
            NotificationService.account_credentials(obj.user, temporary_password)
        super().save_model(request, obj, form, change)


# ------- Lecturer -------
@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "get_full_name", "get_school_email", "get_faculty"]
    search_fields = ["employee_id", "user__first_name", "user__last_name", "user__school_email"]
    ordering = ["employee_id"]
    readonly_fields = ["employee_id"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"

    def get_school_email(self, obj):
        return obj.user.school_email
    get_school_email.short_description = "School Email"

    def get_faculty(self, obj):
        return obj.user.faculty
    get_faculty.short_description = "Faculty"

    def save_model(self, request, obj, form, change):
        if not change:
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            from notifications.services.notification_service import NotificationService
            NotificationService.account_credentials(obj.user, temporary_password)
        super().save_model(request, obj, form, change)


# ------- Staff -------
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["get_full_name", "position", "get_school_email"]
    search_fields = ["user__first_name", "user__last_name", "user__school_email", "position"]
    ordering = ["user__last_name"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"

    def get_school_email(self, obj):
        return obj.user.school_email
    get_school_email.short_description = "School Email"

    def save_model(self, request, obj, form, change):
        if not change:
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            from notifications.services.notification_service import NotificationService
            NotificationService.account_credentials(obj.user, temporary_password)
        super().save_model(request, obj, form, change)


# ------- PasswordResetOTP -------
@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ["user", "otp", "created_at", "expires_at", "is_used", "is_valid"]
    list_filter = ["is_used"]
    search_fields = ["user__school_email"]
    readonly_fields = ["otp", "created_at", "expires_at", "is_used"]
    ordering = ["-created_at"]

    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = "Valid"

    def has_add_permission(self, request):
        return False  # OTPs should only be created by the system