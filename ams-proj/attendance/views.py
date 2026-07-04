from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView 
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsLecturer, IsEnrolled, IsStudent
from .models import Attendance, PendingAttendance
from .serializers import AttendanceCreateSerializer, PendingAttendanceCreateSerializer, AttendanceStudentInfoSerializer, AttendanceLecturerInfoSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from core.utils import get_sessions, get_enrollments

session = get_sessions()
enrollment = get_enrollments()


# Create your views here.

class AttendanceCreateView(APIView):

    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        session = request.data.get("session")

        att_serializer = AttendanceCreateSerializer(data={"session": session})
        pen_att_serializer = PendingAttendanceCreateSerializer(data=request.data)

        if att_serializer.is_valid() and pen_att_serializer.is_valid(raise_exception=True):

            with transaction.atomic():
                att_serializer.save()
                pen_att_serializer.save()

            return Response({"message": "The attendance was marked sucessfully"}, status=status.HTTP_201_CREATED)
        return Response(att_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AttendanceStudentInfoView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, course_offering):
        student = request.user.student_profile
        
        sessions = session.filter(sessions__course_offering=course_offering)
        attendances = Attendance.objects.filter(student=student, session__course_offering=course_offering, status="Present")
        misses = Attendance.objects.filter(student=student, session__course_offering=course_offering, status="Absent")


        total_sessions = sessions.count()
        total_attendances = attendances.count()
        total_missed = misses.count()

        serializer = AttendanceStudentInfoSerializer(attendances, many=True)

        return Response({
            "total_sessions": total_sessions,
            "total_attendances": total_attendances,
            "total_missed": total_missed,
            "attendances": serializer.data
        })
    
class AttendanceTeacherInfoView(APIView):

    permission_classes = [IsAuthenticated, IsLecturer]

    def get(selfm, request, course_offering):
        lecturer = request.user.lecturer_profile

        sessions = session.filter(session__course_offering=course_offering)
        enrolled_students = enrollment.filter(course_offering_id=course_offering)
        attendance = Attendance.objects.filter(session__course_offering= course_offering)

        total_sessions = sessions.count()
        total_enrolled_students = enrolled_students.count()

        serializer = AttendanceLecturerInfoSerializer(attendance, many=True)

        return Response({
            "total_session": total_sessions,
            "total_enrolled_students": total_enrolled_students,
            "attendances": serializer.data
        })


        
