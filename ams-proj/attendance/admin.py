from django.contrib import admin
from .models import Attendance, PendingAttendance

# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        "get_student_name", "get_matricule", "get_course_name",
        "status", "created_at"
    ]
    list_filter = ["status", "session__course_offering__semester"]
    search_fields = [
        "student__matricule",
        "student__user__first_name",
        "student__user__last_name",
        "session__course_offering__course__name"
    ]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student else "Unknown"
    get_student_name.short_description = "Student"

    def get_matricule(self, obj):
        return obj.student.matricule if obj.student else "Unknown"
    get_matricule.short_description = "Matricule"

    def get_course_name(self, obj):
        return obj.session.course_offering.course.name
    get_course_name.short_description = "Course"


@admin.register(PendingAttendance)
class PendingAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        "get_added_student", "get_adder", "get_course_name",
        "approved", "rejected", "timestamp"
    ]
    list_filter = ["approved", "rejected", "session__course_offering__semester"]
    search_fields = [
        "added_student__matricule",
        "added_student__user__first_name",
        "adder__matricule",
        "session__course_offering__course__name"
    ]
    readonly_fields = ["timestamp"]
    ordering = ["-timestamp"]

    def get_added_student(self, obj):
        return obj.added_student.user.get_full_name()
    get_added_student.short_description = "Added Student"

    def get_adder(self, obj):
        return obj.adder.user.get_full_name()
    get_adder.short_description = "Added By"

    def get_course_name(self, obj):
        return obj.session.course_offering.course.name
    get_course_name.short_description = "Course"