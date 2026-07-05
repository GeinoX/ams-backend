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
    permission_classes = [IsAuthenticated, IsStudent, IsEnrolled]

    def post(self, request):
        session = request.data.get("session")
        added_student = request.data.get("added_student")

        att_serializer = AttendanceCreateSerializer(
            data={"session": session},
            context={"request": request}
        )

        att_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            att_serializer.save()

            # only create pending attendance if added_student is provided
            if added_student:
                pen_att_serializer = PendingAttendanceCreateSerializer(
                    data=request.data,
                    context={"request": request}
                )
                pen_att_serializer.is_valid(raise_exception=True)
                pen_att_serializer.save()

        return Response(
            {"message": "Attendance marked successfully"},
            status=status.HTTP_201_CREATED
        )
    
class AttendanceStudentInfoView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, course_offering):
        student = request.user.student_profile

        # ✅ correctly query sessions for this course offering
        sessions = session.filter(course_offering=course_offering)

        attendances = Attendance.objects.filter(
            student=student,
            session__course_offering=course_offering,
            status=Attendance.AttendanceChoices.PRESENT  
        )
        misses = Attendance.objects.filter(
            student=student,
            session__course_offering=course_offering,
            status=Attendance.AttendanceChoices.ABSENT  
        )

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
class AttendanceLecturerInfoView(APIView):

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


        
