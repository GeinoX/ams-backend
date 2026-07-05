from django.contrib import admin
from .models import Course, Semester, CourseOffering, CourseAssignment, CourseEnrollment

# courses/admin.py

# ------- Course -------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "level", "credits", "created_at"]
    list_filter = ["level"]
    search_fields = ["id", "name"]
    ordering = ["level", "name"]
    readonly_fields = ["created_at", "updated_at"]


# ------- Semester -------
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    ordering = ["-start_date"]
    readonly_fields = ["is_active"]


# ------- CourseOffering -------
class CourseAssignmentInline(admin.TabularInline):
    model = CourseAssignment
    extra = 1
    fields = ["lecturer"]


class CourseEnrollmentInline(admin.TabularInline):
    model = CourseEnrollment
    extra = 0
    fields = ["student"]
    readonly_fields = ["student"]
    can_delete = True


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ["course", "semester", "year", "created_at"]
    list_filter = ["semester", "year", "course__level"]
    search_fields = ["course__name", "semester__name"]
    ordering = ["-year", "course__name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [CourseAssignmentInline, CourseEnrollmentInline]


# ------- CourseAssignment -------
@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ["get_lecturer_name", "get_course_name", "get_semester", "get_year", "created_at"]
    list_filter = ["course_offering__semester", "course_offering__year"]
    search_fields = [
        "lecturer__user__first_name",
        "lecturer__user__last_name",
        "course_offering__course__name"
    ]
    readonly_fields = ["created_at", "updated_at"]

    def get_lecturer_name(self, obj):
        return obj.lecturer.user.get_full_name() if obj.lecturer else "Unassigned"
    get_lecturer_name.short_description = "Lecturer"

    def get_course_name(self, obj):
        return obj.course_offering.course.name
    get_course_name.short_description = "Course"

    def get_semester(self, obj):
        return obj.course_offering.semester
    get_semester.short_description = "Semester"

    def get_year(self, obj):
        return obj.course_offering.year
    get_year.short_description = "Year"


# ------- CourseEnrollment -------
@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["get_student_name", "get_matricule", "get_course_name", "get_semester", "created_at"]
    list_filter = ["course_offering__semester", "course_offering__year"]
    search_fields = [
        "student__matricule",
        "student__user__first_name",
        "student__user__last_name",
        "course_offering__course__name"
    ]
    readonly_fields = ["created_at"]

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student else "Unknown"
    get_student_name.short_description = "Student"

    def get_matricule(self, obj):
        return obj.student.matricule if obj.student else "Unknown"
    get_matricule.short_description = "Matricule"

    def get_course_name(self, obj):
        return obj.course_offering.course.name
    get_course_name.short_description = "Course"

    def get_semester(self, obj):
        return obj.course_offering.semester
    get_semester.short_description = "Semester"

# Register your models here.
