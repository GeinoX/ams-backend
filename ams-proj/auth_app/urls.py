from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    StudentRegisterView,
    LecturerRegisterView,
    StaffRegisterView,
    StudentLoginView,
    LecturerLoginView,
    StaffLoginView,
    LogoutView,
    StudentInfoView,
    LecturerInfoView,
    StaffInfoView,
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView

)

urlpatterns = [

    # ------- Student -------
    path("student/login/", StudentLoginView.as_view(), name="student-login"),
    path("student/register/", StudentRegisterView.as_view(), name="student-register"),

    # ------- Lecturer -------
    path("lecturer/login/", LecturerLoginView.as_view(), name="lecturer-login"),
    #path("lecturer/register/", LecturerRegisterView.as_view(), name="lecturer-register"),

    # ------- Staff -------
    path("staff/login/", StaffLoginView.as_view(), name="staff-login"),
    #path("staff/register/", StaffRegisterView.as_view(), name="staff-register"),

    # ------- Token -------
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),  # ← added

    # ------- Logout -------
    path("logout/", LogoutView.as_view(), name="logout"),

    # ------- Info -------
    path("student/info/", StudentInfoView.as_view(), name="student-info"),
    path("lecturer/info/", LecturerInfoView.as_view(), name="lecturer-info"),
    path("staff/info/", StaffInfoView.as_view(), name="staff-info"),

    # ------- Password Reset -------
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/verify/", PasswordResetVerifyView.as_view(), name="password-reset-verify"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
"""
attendance.save()

notification = Notification.objects.create(...)

PushService.send(notification)

return Response({"success": True})

"""