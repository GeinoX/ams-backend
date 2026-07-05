from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    StudentTokenObtainPairSerializer,
    LecturerTokenObtainPairSerializer,
    StaffTokenObtainPairSerializer,
    StudentRegisterSerializer,
    LecturerRegisterSerializer,
    StaffRegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer,
    LogoutSerializer,
    StudentInfoSerializer,
    LecturerInfoSerializer,
    StaffInfoSerializer
)
from .models import Student, Lecturer, Staff
from core.permissions import IsStudent, IsLecturer


# ------- Login -------
class StudentLoginView(TokenObtainPairView):
    serializer_class = StudentTokenObtainPairSerializer


class LecturerLoginView(TokenObtainPairView):
    serializer_class = LecturerTokenObtainPairSerializer


class StaffLoginView(TokenObtainPairView):
    serializer_class = StaffTokenObtainPairSerializer


# ------- Register -------
class StudentRegisterView(APIView):

    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student registered successfully"}, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LecturerRegisterView(APIView):

    def post(self, request):
        serializer = LecturerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration Successful"}, status=201)
        return Response(serializer.errors, status=400)


class StaffRegisterView(APIView):

    def post(self, request):
        serializer = StaffRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # ✅ added
            return Response({"message": "Registration Successful"}, status=201)
        return Response(serializer.errors, status=400)


# ------- Info -------
class StudentInfoView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = StudentInfoSerializer

    def get_object(self):
        return Student.objects.select_related("user").get(user=self.request.user)


class LecturerInfoView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsLecturer]
    serializer_class = LecturerInfoSerializer

    def get_object(self):
        return Lecturer.objects.select_related("user").get(user=self.request.user)


class StaffInfoView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StaffInfoSerializer

    def get_object(self):
        return Staff.objects.select_related("user").get(user=self.request.user)


# ------- Logout -------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"message": "Logged out successfully"}, status=200)


# ------- Password Reset -------
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "OTP sent to your email"}, status=200)


class PasswordResetVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP verified successfully"}, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully"}, status=200)

"""
class RegisterView(APIView):

    @classmethod
    def func(cls):
        def post(self, request):
            class_serializer = cls.serializer
            serializer = class_serializer(data=request.data)
            if serializer.is_valid():
                return Response({"message": "Registration Successful"})
            return Response(serializer.errors, status=400)
        
        return post
    
class StudentRegisterView(RegisterView):
    serializer = StudentRegisterSerializer

class LecturerRegisterView(RegisterView):
    serializer = LecturerRegisterSerializer

class AdminRegisterView(RegisterView):
    serializer = StaffRegisterSerializer


StudentRegisterView.post = StudentRegisterView.func()

LecturerRegisterView.post = LecturerRegisterView.func()

AdminRegisterView.post = AdminRegisterView.func()
"""