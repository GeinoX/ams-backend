from django.urls.conf import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import StudentRegisterView, LecturerRegisterView, StaffRegisterView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="Login"),
    path("student/register/", StudentRegisterView.as_view(), name="Student Register"),
    path("lecturer/register/", LecturerRegisterView.as_view(), name="Lecturer Register"),
    path("staff/register/", StaffRegisterView.as_view(), name="Lecturer Register"),
]

