from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django import forms
import secrets
import string
from .models import (
    CustomUser, Faculty, Student, Lecturer,
    Staff, PasswordResetOTP
)


# ------- Helpers -------
def generate_temporary_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_credentials(user, temporary_password):
    from notifications.services.notification_service import NotificationService
    NotificationService.account_credentials(user, temporary_password)


# ------- Custom Creation Form -------
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(required=False, widget=forms.HiddenInput)
    password2 = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = CustomUser
        fields = [
            "school_email", "first_name", "last_name",
            "gender", "phone", "faculty", "email"
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


# ------- Faculty -------
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


# ------- CustomUser -------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    list_display = [
        "school_email", "get_full_name", "gender",
        "phone", "faculty", "is_active", "is_staff",
        "must_change_password", "date_joined"
    ]
    list_filter = [
        "is_active", "is_staff", "gender",
        "faculty", "must_change_password"
    ]
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
        (_("Personal Info"), {
            "classes": ("wide",),
            "fields": (
                "school_email", "first_name", "last_name",
                "gender", "phone", "faculty", "email",
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

    def save_model(self, request, obj, form, change):
        if not change:  # on creation only
            temporary_password = generate_temporary_password()
            obj.set_password(temporary_password)
            obj.must_change_password = True
            obj.save()
            send_credentials(obj, temporary_password)
        else:
            super().save_model(request, obj, form, change)


# ------- Student -------
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = "Student Profile"
    fields = ["matricule"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        "matricule", "get_full_name",
        "get_school_email", "get_faculty"
    ]
    search_fields = [
        "matricule", "user__first_name",
        "user__last_name", "user__school_email"
    ]
    ordering = ["matricule"]
    readonly_fields = [
        "matricule", "get_full_name",
        "get_school_email", "get_faculty",
        "profile_image_preview"
    ]

    fieldsets = (
        (_("Student Info"), {
            "fields": ("matricule",)
        }),
        (_("User Info"), {
            "fields": (
                "get_full_name", "get_school_email",
                "get_faculty", "profile_image_preview"
            )
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"

    def get_school_email(self, obj):
        return obj.user.school_email
    get_school_email.short_description = "School Email"

    def get_faculty(self, obj):
        return obj.user.faculty
    get_faculty.short_description = "Faculty"

    def profile_image_preview(self, obj):
        if obj.user.profile_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius: 50%;" />',
                obj.user.profile_image.url
            )
        return "No image"
    profile_image_preview.short_description = "Profile Image"

    def save_model(self, request, obj, form, change):
        if not change:
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            send_credentials(obj.user, temporary_password)
        super().save_model(request, obj, form, change)


# ------- Lecturer -------
@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = [
        "employee_id", "get_full_name",
        "get_school_email", "get_faculty"
    ]
    search_fields = [
        "employee_id", "user__first_name",
        "user__last_name", "user__school_email"
    ]
    ordering = ["employee_id"]
    readonly_fields = [
        "employee_id", "get_full_name",
        "get_school_email", "get_faculty",
        "profile_image_preview"
    ]

    fieldsets = (
        (_("Lecturer Info"), {
            "fields": ("employee_id",)
        }),
        (_("User Info"), {
            "fields": (
                "get_full_name", "get_school_email",
                "get_faculty", "profile_image_preview"
            )
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"

    def get_school_email(self, obj):
        return obj.user.school_email
    get_school_email.short_description = "School Email"

    def get_faculty(self, obj):
        return obj.user.faculty
    get_faculty.short_description = "Faculty"

    def profile_image_preview(self, obj):
        if obj.user.profile_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius: 50%;" />',
                obj.user.profile_image.url
            )
        return "No image"
    profile_image_preview.short_description = "Profile Image"

    def save_model(self, request, obj, form, change):
        if not change:
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            send_credentials(obj.user, temporary_password)
        super().save_model(request, obj, form, change)


# ------- Staff -------
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        "get_full_name", "position", "get_school_email"
    ]
    search_fields = [
        "user__first_name", "user__last_name",
        "user__school_email", "position"
    ]
    ordering = ["user__last_name"]
    readonly_fields = [
        "get_full_name", "get_school_email",
        "profile_image_preview"
    ]

    fieldsets = (
        (_("Staff Info"), {
            "fields": ("position",)
        }),
        (_("User Info"), {
            "fields": (
                "get_full_name", "get_school_email",
                "profile_image_preview"
            )
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"

    def get_school_email(self, obj):
        return obj.user.school_email
    get_school_email.short_description = "School Email"

    def profile_image_preview(self, obj):
        if obj.user.profile_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius: 50%;" />',
                obj.user.profile_image.url
            )
        return "No image"
    profile_image_preview.short_description = "Profile Image"

    def save_model(self, request, obj, form, change):
        if not change:
            temporary_password = generate_temporary_password()
            obj.user.set_password(temporary_password)
            obj.user.must_change_password = True
            obj.user.save()
            send_credentials(obj.user, temporary_password)
        super().save_model(request, obj, form, change)


# ------- PasswordResetOTP -------
@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = [
        "user", "otp", "created_at",
        "expires_at", "is_used", "is_valid_display"
    ]
    list_filter = ["is_used"]
    search_fields = ["user__school_email"]
    readonly_fields = ["otp", "created_at", "expires_at", "is_used"]
    ordering = ["-created_at"]

    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = "Valid"

    def has_add_permission(self, request):
        return False  # OTPs should only be created by the system

    def has_change_permission(self, request, obj=None):
        return False  # OTPs should not be manually edited

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # only superuser can delete OTPs