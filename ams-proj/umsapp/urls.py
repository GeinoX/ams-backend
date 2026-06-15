from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # Auth
    MyTokenObtainPairView,
    StudentRegisterView,
    TeacherRegisterView,

    # Profile
    StudentInfoView,
    TeacherInfoView,

    # Courses & Enrollment
    CourseOfferingListView,
    CourseView,
    CourseFilterView,
    EnrollStudentView,
    MyEnrollmentsView,

    # Student Attendance
    VerifyAttendanceView,
    StudentCourseAttendanceDetailView,
    StudentAttendanceSummaryView,

    # Teacher — Courses & Sessions
    LecturerAssignedCoursesView,
    StartSessionView,
    StopSessionView,

    # Teacher — Attendance
    CourseSessionAttendanceView,
    PendingAttendanceListView,
    ApprovePendingAttendanceView,
    RejectPendingAttendanceView,
)

urlpatterns = [

    # ── Auth ──────────────────────────────────────────────────────────────
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ── Registration ──────────────────────────────────────────────────────
    path('students/register/', StudentRegisterView.as_view(), name='student-register'),
    path('teacher/register/', TeacherRegisterView.as_view(), name='teacher-register'),

    # ── Profile info ──────────────────────────────────────────────────────
    path('stud_info/', StudentInfoView.as_view(), name='stud-info'),
    path('teacher_info/', TeacherInfoView.as_view(), name='teacher-info'),

    # ── Courses ───────────────────────────────────────────────────────────
    path('courses/', CourseView.as_view(), name='all-courses'),
    path('courses/<str:level>/', CourseFilterView.as_view(), name='filter-courses'),
    path('course-offerings/', CourseOfferingListView.as_view(), name='course-offerings'),

    # ── Student enrollment ────────────────────────────────────────────────
    path('enrollments/', EnrollStudentView.as_view(), name='enroll-student'),
    path('enrollments/my/', MyEnrollmentsView.as_view(), name='my-enrollments'),

    # ── Student attendance ────────────────────────────────────────────────
    path('attendance/verify/', VerifyAttendanceView.as_view(), name='verify-attendance'),
    path('student/course/<str:course_id>/attendance/', StudentCourseAttendanceDetailView.as_view(), name='student-course-attendance-detail'),
    path('student/course/<str:course_id>/attendance/summary/', StudentAttendanceSummaryView.as_view(), name='student-course-attendance-summary'),

    # ── Teacher — courses ─────────────────────────────────────────────────
    path('lecturer/assigned-courses/', LecturerAssignedCoursesView.as_view(), name='lecturer-assigned-courses'),

    # ── Teacher — sessions ────────────────────────────────────────────────
    path('sessions/start/', StartSessionView.as_view(), name='start-session'),
    path('sessions/<uuid:session_id>/stop/', StopSessionView.as_view(), name='stop-session'),

    # ── Teacher — attendance ──────────────────────────────────────────────
    path('sessions/<uuid:session_id>/attendance/', CourseSessionAttendanceView.as_view(), name='session-attendance'),
    path('sessions/<uuid:session_id>/pending/', PendingAttendanceListView.as_view(), name='pending-attendance-list'),
    path('attendance/approve/', ApprovePendingAttendanceView.as_view(), name='approve-pending'),
    path('attendance/reject/', RejectPendingAttendanceView.as_view(), name='reject-pending'),
]