from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    StudentLoginView,
    LecturerLoginView,
    StaffLoginView,

    StudentRegisterView,

    StudentInfoView,
    LecturerInfoView,
    StaffInfoView,

    AdminCreateLecturerView,
    ChangePasswordView,

    LogoutView,

    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView,
)


urlpatterns = [
    # ========================================================
    # AUTHENTICATION
    # ========================================================

    path(
        "student/login/",
        StudentLoginView.as_view(),
        name="student-login",
    ),

    path(
        "student/register/",
        StudentRegisterView.as_view(),
        name="student-register",
    ),

    path(
        "lecturer/login/",
        LecturerLoginView.as_view(),
        name="lecturer-login",
    ),

    path(
        "staff/login/",
        StaffLoginView.as_view(),
        name="staff-login",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # ========================================================
    # PASSWORD
    # ========================================================

    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),

    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),

    path(
        "password-reset/verify/",
        PasswordResetVerifyView.as_view(),
        name="password-reset-verify",
    ),

    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),

    # ========================================================
    # USER INFORMATION
    # ========================================================

    path(
        "student/info/",
        StudentInfoView.as_view(),
        name="student-info",
    ),

    path(
        "lecturer/info/",
        LecturerInfoView.as_view(),
        name="lecturer-info",
    ),

    path(
        "staff/info/",
        StaffInfoView.as_view(),
        name="staff-info",
    ),

    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/lecturers/",
        AdminCreateLecturerView.as_view(),
        name="admin-create-lecturer",
    ),
]