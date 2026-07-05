from django.urls.conf import path
from .views import AttendanceCreateView, AttendanceLecturerInfoView, AttendanceStudentInfoView

urlpatterns = [
    path('student/checkin/', AttendanceCreateView.as_view(), name="Attendance Checkin"),
    path('student/info/', AttendanceStudentInfoView.as_view(), name="Attendance Student Info"),
    path('lecturer/info/', AttendanceLecturerInfoView.as_view(), name="Attendance Lecturer Info")
] 