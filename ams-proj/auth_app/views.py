from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .serializers import (StudentTokenObtainPairSerializer, LecturerTokenObtainPairSerializer, 
                          StaffTokenObtainPairSerializer, StudentRegisterSerializer, 
                          LecturerRegisterSerializer, StaffRegisterSerializer,  
                          PasswordResetRequestSerializer, PasswordResetVerifySerializer, 
                          PasswordResetConfirmSerializer, LogoutSerializer)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Logged out successfully"}, status=200)

# Create your views here.

class StudentLoginView(TokenObtainPairView):
    serializer_class = StudentTokenObtainPairSerializer

class LecturerLoginView(TokenObtainPairView):
    serializer_class = LecturerTokenObtainPairSerializer

class StaffLoginView(TokenObtainPairView):
    serializer_class = StaffTokenObtainPairSerializer
    
class StudentRegisterView(APIView):
    
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = StudentRegisterSerializer(user).data
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
            return Response({"message": "Registration Successful"})
        return Response(serializer.errors, status=400)
    

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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # ← pass user to save()
        return Response({"message": "Logged out successfully"}, status=200)
    

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