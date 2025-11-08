from django.contrib import admin
from .models import Notification
# Register your models here.
# CustomUser admin

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("sender", "message", "timestamp")
    search_fields = ("sender", "sender")
    list_filter = ("sender", "sender")
    ordering = ("sender", "sender")