# urls.py
from django.urls import path
from .views import StudentRegisterView, CourseView, CoursefilterView, TimetableView, EnrollView, MyTokenObtainPairView, EnrollFilterView, StartSessionView, StopSessionView, AttendanceCheckInView, TeacherRegisterView, StudentAttendanceView, TeacherCoursesView, GetCourseStudentsView, ReportDetectionView, ActiveSessionView, StudentInfoView, StudentAttView, PendingAttendanceView, ApprovePendingAttendanceView, LogoutView, GetCurrentSemesterView, TeacherTimetableView, TeacherInfoView

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('students/register/', StudentRegisterView.as_view(), name='student-register'),
    path('teacher/register/', TeacherRegisterView.as_view(), name='teacher-register'),
    path('attendance/student/<str:course_id>/', StudentAttendanceView.as_view(), name='student-attendance'),
    path('courses', CourseView.as_view(), name='all-courses'),
    path('courses/<str:level>', CoursefilterView.as_view(), name='filter-courses'),
    path('timetable', TimetableView.as_view(), name='all-timetable'),
    path('teacher/timetable/', TeacherTimetableView.as_view(), name='teacher-timetable'),
    path('enroll', EnrollView.as_view(), name='enroll'),
    path('enrollfilter', EnrollFilterView.as_view(), name='enroll-filter'),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('start_session/', StartSessionView.as_view(), name='start-session'),
    path('stop_session/<uuid:session_id>/', StopSessionView.as_view(), name='stop-session'),
    path('attendance/check_in/', AttendanceCheckInView.as_view(), name='attendance-check-in'),
    path('get_teacher_courses/', TeacherCoursesView.as_view(), name='get_teacher_courses'),
    path('get_course_students/<str:course_id>/', GetCourseStudentsView.as_view(), name='get_course_students'),
    path('get_student_att/<str:course_id>/', StudentAttView.as_view(), name='get_student_attendance'),
    path("report_detection/", ReportDetectionView.as_view()),
    path("report_detection/", ReportDetectionView.as_view()),
    path("active_session/", ActiveSessionView.as_view(), name="active-session"),
    path('stud_info/', StudentInfoView.as_view(), name='stud-info'),
    path('teacher_info/', TeacherInfoView.as_view(), name='teacher-info'),
    path('attendance/check_in/', AttendanceCheckInView.as_view(), name='attendance-check-in'),
    path('attendance/pending/<uuid:session_id>/', PendingAttendanceView.as_view(), name='pending-attendance'),
    path('attendance/approve/', ApprovePendingAttendanceView.as_view(), name='approve-attendance'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('currentsemester/', GetCurrentSemesterView.as_view(), name='current_serializer'),

]
