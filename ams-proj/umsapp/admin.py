from django.contrib import admin
from django.utils.html import format_html

from .models import (
    CustomUser, Student, Teacher,
    Course, Semester, CourseOffering,
    Enrollment, Session, Attendance,
    CourseAssignment, PendingAttendance
)

# ==============================
# CustomUser admin
# ==============================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email", "name", "gender", "phone",
        "profile_image_tag", "is_teacher",
        "is_staff", "is_active"
    )

    search_fields = ("email", "name", "phone")
    list_filter = ("gender", "is_teacher", "is_active")
    ordering = ("email",)

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.profile_image.url
            )
        return "No Image"

    profile_image_tag.short_description = "Profile Image"


# ==============================
# Student admin
# ==============================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("matricule", "user", "school_email", "program")
    search_fields = ("matricule", "user__name", "school_email", "program")


# ==============================
# Teacher admin
# ==============================
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user")
    search_fields = ("employee_id", "user__name")


# ==============================
# Course admin
# ==============================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "course_name", "credits", "level", "created_at")
    search_fields = ("course_id", "course_name")
    list_filter = ("level",)
    ordering = ("course_id",)


# ==============================
# Semester admin
# ==============================
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    ordering = ("start_date",)


# ==============================
# CourseOffering admin
# ==============================
@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):

    list_display = (
        "course_offering_id",
        "course_display",
        "semester_display",
        "year",
        "created_at"
    )

    search_fields = (
        "course__course_id",
        "course__course_name",
    )

    list_filter = (
        "semester",
        "year",
        "course__level"
    )

    def course_display(self, obj):
        return f"{obj.course.course_id} - {obj.course.course_name}"
    course_display.short_description = "Course"

    def semester_display(self, obj):
        return f"{obj.semester.name} {'(Active)' if obj.semester.is_active else ''}"
    semester_display.short_description = "Semester"


# ==============================
# Enrollment admin
# ==============================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "student_name",
        "course_display",
        "semester_display",
        "created_at"
    )

    search_fields = (
        "student__matricule",
        "student__user__name",
        "course_offering__course__course_id",
        "course_offering__course__course_name",
    )

    list_filter = (
        "course_offering__semester",
        "course_offering__year"
    )

    def student_name(self, obj):
        return obj.student.user.name
    student_name.short_description = "Student"

    def course_display(self, obj):
        return f"{obj.course_offering.course.course_id} - {obj.course_offering.course.course_name}"
    course_display.short_description = "Course"

    def semester_display(self, obj):
        sem = obj.course_offering.semester
        return f"{sem.name} {'(Active)' if sem.is_active else ''}"
    semester_display.short_description = "Semester"


# ==============================
# Session admin
# ==============================
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):

    list_display = (
        "session_id",
        "course_display",
        "semester_display",
        "start_time",
        "end_time",
        "active"
    )

    search_fields = (
        "session_id",
        "course_offering__course__course_name",
        "course_offering__course__course_id"
    )

    list_filter = (
        "active",
        "course_offering__semester",
        "course_offering__year"
    )

    def course_display(self, obj):
        return f"{obj.course_offering.course.course_id} - {obj.course_offering.course.course_name}"
    course_display.short_description = "Course"

    def semester_display(self, obj):
        sem = obj.course_offering.semester
        return f"{sem.name} {'(Active)' if sem.is_active else ''}"
    semester_display.short_description = "Semester"


# ==============================
# Attendance admin
# ==============================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "session",
        "student",
        "course_display",
        "created_at"
    )

    search_fields = (
        "session__session_id",
        "student__matricule",
        "student__user__name"
    )

    list_filter = (
        "session__course_offering__course",
        "session__course_offering__semester"
    )

    def course_display(self, obj):
        return obj.session.course_offering.course.course_name
    course_display.short_description = "Course"


# ==============================
# CourseAssignment admin
# ==============================
@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "lecturer_name",
        "course_display",
        "semester_display",
        "created_at"
    )

    search_fields = (
        "lecturer__user__name",
        "course_offering__course__course_name"
    )

    list_filter = (
        "course_offering__semester",
        "course_offering__year"
    )

    def lecturer_name(self, obj):
        return obj.lecturer.user.name
    lecturer_name.short_description = "Lecturer"

    def course_display(self, obj):
        return f"{obj.course_offering.course.course_id} - {obj.course_offering.course.course_name}"
    course_display.short_description = "Course"

    def semester_display(self, obj):
        sem = obj.course_offering.semester
        return f"{sem.name} {'(Active)' if sem.is_active else ''}"
    semester_display.short_description = "Semester"


# ==============================
# PendingAttendance admin
# ==============================
@admin.register(PendingAttendance)
class PendingAttendanceAdmin(admin.ModelAdmin):
    list_display = ("session_info", "adder_name", "added_student_name", "approved", "timestamp")
    search_fields = ("session__course_offering__course__course_name",
                     "adder__user__name",
                     "added_student__user__name")
    list_filter = ("approved", "session__course_offering__semester")
    ordering = ("-timestamp",)

    # Custom display for session info
    def session_info(self, obj):
        return f"{obj.session.course_offering.course.course_id} - {obj.session.course_offering.course.course_name} ({obj.session.course_offering.semester.name})"
    session_info.short_description = "Session"

    # Display the student who added
    def adder_name(self, obj):
        return obj.adder.user.name
    adder_name.short_description = "Added By"

    # Display the student who is pending
    def added_student_name(self, obj):
        return obj.added_student.user.name
    added_student_name.short_description = "Pending Student"
    
"""
# ==============================
# Enrollment admin
# ==============================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course_offering", "created_at")
    search_fields = ("student__matricule", "course_offering__course__course_id")
    list_filter = ("course_offering__semester", "course_offering__year")


# ==============================
# Timetable admin
# ==============================
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("course", "day", "start_time", "end_time", "hall")
    search_fields = ("course__course_name", "hall")
    list_filter = ("course__course_name", "hall")


# ==============================
# Attendance admin
# ==============================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "created_at")
    search_fields = ("session__session_id", "student__matricule")
    list_filter = ("session__course_offering__course__course_name",)


# ==============================
# Session admin
# ==============================
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "course_name", "start_time", "end_time", "active")
    search_fields = ("session_id", "course_offering__course__course_name")
    list_filter = ("active", "course_offering__semester")

    def course_name(self, obj):
        return f"{obj.course_offering.course.course_id} - {obj.course_offering.course.course_name}"
    course_name.short_description = "Course"


# ==============================
# CourseAssignment admin
# ==============================
@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ("lecturer_name", "course_offering_name", "created_at")
    search_fields = ("lecturer__user__name", "course_offering__course__course_name")
    list_filter = ("course_offering__semester", "course_offering__year")

    def lecturer_name(self, obj):
        return obj.lecturer.user.name
    lecturer_name.short_description = "Lecturer"

    def course_offering_name(self, obj):
        return f"{obj.course_offering.course.course_id} - {obj.course_offering.course.course_name}"
    course_offering_name.short_description = "Course Offering"


# ==============================
# PendingAttendance admin
# ==============================
@admin.register(PendingAttendance)
class PendingAttendanceAdmin(admin.ModelAdmin):
    list_display = ("session", "adder", "added_student", "approved", "timestamp")
    search_fields = ("session__session_id", "adder__matricule", "added_student__matricule")
    list_filter = ("approved",)
    ordering = ("timestamp",)


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
    list_display = ("session", "student", "semester", "timestamp")
    search_fields = ("session", "student", "semester")
    list_filter =  ("session", "student", "semester")

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



    """

