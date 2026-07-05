from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import (CourseOfferingListSerializer, CourseAssignmentSerializer, 
                          CourseEnrollmentCreateSerializer, CourseEnrollmentListSerializer)
from .models import CourseOffering, CourseAssignment, CourseEnrollment
from rest_framework.generics import DestroyAPIView
from rest_framework.exceptions import NotFound, PermissionDenied



# Create your views here.
    
class CourseEnrollmentCreateView(CreateAPIView):
    serializer_class = CourseEnrollmentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

class CourseEnrollmentListView(ListAPIView):
    serializer_class = CourseEnrollmentCreateSerializer
    permission_classes = [IsAuthenticated ]

    def get_queryset(self):
        queryset = CourseEnrollment.objects.select_related("course_offering")
        user = self.request.user
        queryset = queryset.filter(student__user=user)
        return queryset


from courses.models import Semester

class CourseOfferingListView(ListAPIView):
    serializer_class = CourseOfferingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        active_semester = Semester.objects.filter(is_active=True).first()

        if not active_semester:
            return CourseOffering.objects.none()  # ← return empty if no active semester

        queryset = CourseOffering.objects.select_related(
            "course", "semester"
        ).filter(semester=active_semester)

        level = self.request.query_params.get("level")
        if level:
            queryset = queryset.filter(course__level=level)

        return queryset


class CourseAssignmentListView(ListAPIView):
    serializer_class = CourseAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        active_semester = Semester.objects.filter(is_active=True).first()

        if not active_semester:
            return CourseAssignment.objects.none()

        user = self.request.user
        return CourseAssignment.objects.select_related(
            "course_offering__course",
            "course_offering__semester",
            "lecturer__user"
        ).filter(
            lecturer__user=user,
            course_offering__semester=active_semester
        )


class CourseEnrollmentListView(ListAPIView):
    serializer_class = CourseEnrollmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        active_semester = Semester.objects.filter(is_active=True).first()

        if not active_semester:
            return CourseEnrollment.objects.none()

        user = self.request.user
        return CourseEnrollment.objects.select_related(
            "course_offering__course",
            "course_offering__semester"
        ).filter(
            student__user=user,
            course_offering__semester=active_semester
        )