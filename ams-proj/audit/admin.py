from django.contrib import admin
from auditlog.models import LogEntry


# Register your models here.

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp", "get_actor", "action",
        "content_type", "object_repr", "get_changes"
    ]
    list_filter = ["action", "content_type", "timestamp"]
    search_fields = ["actor__school_email", "object_repr", "content_type__model"]
    readonly_fields = [
        "timestamp", "actor", "action", "content_type",
        "object_id", "object_repr", "changes", "remote_addr"
    ]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"

    def get_actor(self, obj):
        return obj.actor.get_full_name() if obj.actor else "System"
    get_actor.short_description = "Actor"

    def get_changes(self, obj):
        return obj.changes if obj.changes else "-"
    get_changes.short_description = "Changes"

    def has_add_permission(self, request):
        return False  # no one can add audit logs

    def has_change_permission(self, request, obj=None):
        return False  # no one can edit audit logs

    def has_delete_permission(self, request, obj=None):
        return False  # no one can delete audit logs