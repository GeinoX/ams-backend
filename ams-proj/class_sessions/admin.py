from django.contrib import admin
from django.utils.html import format_html
from .models import Session


# Register your models here.

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        "session_id", "get_course_name", "get_semester",
        "start_time", "end_time", "active_badge"
    ]
    list_filter = ["active", "course_offering__semester"]
    search_fields = [
        "session_id",
        "course_offering__course__name"
    ]
    readonly_fields = ["session_id", "start_time"]
    ordering = ["-start_time"]

    def get_course_name(self, obj):
        return obj.course_offering.course.name
    get_course_name.short_description = "Course"

    def get_semester(self, obj):
        return obj.course_offering.semester
    get_semester.short_description = "Semester"

    def active_badge(self, obj):
        if obj.active:
            return format_html('<span style="color: green; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: red;">● Ended</span>')
    active_badge.short_description = "Status"