from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import CourseOfferingListSerializer, CourseAssignmentSerializer, CourseEnrollmentCreateSerializer
from .models import CourseOffering, CourseAssignment, CourseEnrollment



# Create your views here.

class CourseOfferingListView(ListAPIView):
    serializer_class = CourseOfferingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CourseOffering.objects.select_related("course")
        level = self.request.query_params.get("level")
        if level:
            queryset = queryset.filter(course__level=level)
        return queryset

class CourseAssignmentListView(ListAPIView):
    serializer_class = CourseAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CourseAssignment.objects.select_related("course_offering")
        user = self.request.user
        queryset = queryset.filter(lecturer__user=user)
        return queryset
    
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


