from django.contrib import admin
from .models import Notification, DeviceToken

# Register your models her.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "recipient", "title", "type",
        "is_read", "created_at", "read_at"
    ]
    list_filter = ["type", "is_read"]
    search_fields = ["recipient__school_email", "title", "body"]
    readonly_fields = ["id", "created_at", "read_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False  # notifications should only be created by the system


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = [
        "user", "platform", "ip_address",
        "is_active", "created_at", "last_used_at"
    ]
    list_filter = ["is_active", "platform"]
    search_fields = ["user__school_email", "token", "ip_address"]
    readonly_fields = ["token", "created_at", "last_used_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False  # tokens should only be created by the system