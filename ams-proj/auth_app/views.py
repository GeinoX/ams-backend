from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from .models import (
    Student,
    Lecturer,
    Staff,
)


from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer,
)

from notifications.services.notification_service import (
    NotificationService,
)

from .serializers import (
    StudentTokenObtainPairSerializer,
    LecturerTokenObtainPairSerializer,
    StaffTokenObtainPairSerializer,

    StudentRegisterSerializer,
    LecturerRegisterSerializer,
    StaffRegisterSerializer,

    StudentInfoSerializer,
    LecturerInfoSerializer,
    StaffInfoSerializer,

    AdminCreateLecturerSerializer,
    ChangePasswordSerializer,
)

from .permissions import (
    IsAdmin,
    IsLecturer,
    MustNotChangePassword,
)
from rest_framework.permissions import AllowAny


User = get_user_model()


# ============================================================
# LOGIN
# ============================================================

class StudentLoginView(TokenObtainPairView):
    serializer_class = StudentTokenObtainPairSerializer


class LecturerLoginView(TokenObtainPairView):
    serializer_class = LecturerTokenObtainPairSerializer


class StaffLoginView(TokenObtainPairView):
    serializer_class = StaffTokenObtainPairSerializer


# ============================================================
# REGISTRATION
# ============================================================

class StudentRegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentRegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Student account created successfully."
                )
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# LECTURER REGISTRATION
#
# DO NOT expose this endpoint.
#
# Lecturer accounts are created by administrators.
# ============================================================

# class LecturerRegisterView(APIView):
#     ...


# ============================================================
# STAFF REGISTRATION
#
# Keep/remove depending on your business rules.
# ============================================================

# class StaffRegisterView(APIView):
#     ...


# ============================================================
# STUDENT INFO
# ============================================================

class StudentInfoView(RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = StudentInfoSerializer

    def get_object(self):
        return Student.objects.select_related(
            "user"
        ).get(
            user=self.request.user
        )


# ============================================================
# LECTURER INFO
# ============================================================

class LecturerInfoView(RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
        IsLecturer,
        MustNotChangePassword,
    ]

    serializer_class = LecturerInfoSerializer

    def get_object(self):
        return Lecturer.objects.select_related(
            "user"
        ).get(
            user=self.request.user
        )


# ============================================================
# STAFF INFO
# ============================================================

class StaffInfoView(RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = StaffInfoSerializer

    def get_object(self):
        return Staff.objects.select_related(
            "user"
        ).get(
            user=self.request.user
        )


# ============================================================
# ADMIN CREATE LECTURER
# ============================================================

class AdminCreateLecturerView(APIView):
    permission_classes = [
        # IsAuthenticated,
        # IsAdmin,
    ]

    def post(self, request):
        serializer = AdminCreateLecturerSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        lecturer = serializer.save()

        temporary_password = (
            lecturer._temporary_password
        )

        # Send credentials to lecturer.
        #
        # Replace this import/path with the exact
        # NotificationService location in your project.
        from notifications.services.notification_service import (
            NotificationService,
        )

        NotificationService.account_credentials(
            user=lecturer,
            temporary_password=temporary_password,
        )

        return Response(
            {
                "message": (
                    "Lecturer account created successfully. "
                    "Login credentials have been sent to "
                    "the lecturer's email."
                )
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": "Logged out successfully."
            },
            status=status.HTTP_205_RESET_CONTENT,
        )


class PasswordResetRequestView(APIView):
    """
    Request a password-reset OTP.

    POST:
    {
        "school_email": "lecturer@university.com"
    }
    """

    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        reset_otp = serializer.save()

        NotificationService.password_reset_otp(
            user=reset_otp.user,
            otp=reset_otp.otp,
        )

        return Response(
            {
                "message": (
                    "A password reset OTP has been "
                    "sent to your email address."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetVerifyView(APIView):
    """
    Verify a password-reset OTP.

    POST:
    {
        "school_email": "lecturer@university.com",
        "otp": "123456"
    }
    """

    permission_classes = []

    def post(self, request):
        serializer = PasswordResetVerifySerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        return Response(
            {
                "message": "OTP verified successfully.",
                "verified": True,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Set a new password using a valid OTP.

    POST:
    {
        "school_email": "lecturer@university.com",
        "otp": "123456",
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }
    """

    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        NotificationService.password_reset(
            user=user
        )

        return Response(
            {
                "message": (
                    "Your password has been reset successfully."
                ),
                "must_change_password": False,
            },
            status=status.HTTP_200_OK,
        )
# ============================================================
# CHANGE PASSWORD
# ============================================================

class ChangePasswordView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Password changed successfully."
                ),
                "must_change_password": False,
            },
            status=status.HTTP_200_OK,
        )