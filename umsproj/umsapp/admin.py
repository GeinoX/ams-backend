from django.contrib import admin
from .models import CustomUser, Student, Course, Enrollment, Timetable, Attendance, Session, Teacher, CourseAssignment, PendingAttendance, Semester

# CustomUser admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "gender", "phone", "is_staff", "is_teacher", "is_active")
    search_fields = ("email", "name", "phone")
    list_filter = ("is_teacher", "is_active", "gender")
    ordering = ("email",)

# Student admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("matricule", "user",  "school_email", "program") # "profile_image_tag"
    search_fields = ("matricule", "user__name", "school_email", "program")

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user") # "profile_image_tag"
    search_fields = ("employee_id", "name")

# Course admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "course_name", "credits", "status", "level")
    search_fields = ("course_id", "course_name")
    list_filter = ("status", "level")
    ordering = ("course_id",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrollment_date", "semester", "created_at", "updated_at")
    search_fields = ("student", "course")
    list_filter =  ("course", "enrollment_date")
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("course", "day", "start_time", "end_time", "hall")
    search_fields = ("course", "hall")
    list_filter =  ("course", "hall")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "timestamp")
    search_fields = ("session", "student")
    list_filter =  ("session", "student")

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "teacher", "course", 'start_time', 'end_time', 'active')
    search_fields = ("session_id", "teacher", "course")
    list_filter =  ("session_id", "teacher")


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "course", "semester", "timestamp", "year")
    search_fields = ("teacher", "course")
    list_filter = ("teacher", "course")
    ordering = ("course",)

@admin.register(PendingAttendance)
class PendingAttendanceAdmin(admin.ModelAdmin):
    list_display = ("session", "adder", "added_student", "timestamp", "approved")
    search_fields = ("session", "adder")
    list_filter = ("session", "adder")
    ordering = ("timestamp",)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("id", "period", "year", "status")
    search_fields = ("period", "year")
    list_filter = ("period", "status")
    ordering = ("period",)

    

