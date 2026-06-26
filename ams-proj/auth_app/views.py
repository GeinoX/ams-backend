from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import StudentRegisterSerializer, LecturerRegisterSerializer, StaffRegisterSerializer
from rest_framework import status

# Create your views here.

class StudentRegisterView(APIView):
    
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = StudentRegisterSerializer(user).data
            return Response({"message": "Student registered successfully"}, status=201)
        return Response(serializer.errors, status=status.HTTP_201_CREATED)
    
class LecturerRegisterView(APIView):

    def post(self, request):
        serializer = LecturerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration Successful"})
        return Response(serializer.errors, status=400)

class StaffRegisterView(APIView):

    def post(self, request):
        serializer = StaffRegisterSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Registration Successful"})
        return Response(serializer.errors, status=400)
    
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