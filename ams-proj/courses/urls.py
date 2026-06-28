from django.urls.conf import path
from .views import CourseAssignmentListView, CourseEnrollmentCreateView, CourseOfferingListView, CourseEnrollmentListView



urlpatterns = [
    path("enroll/", CourseEnrollmentCreateView.as_view(), name="enroll"),
    path("enrollments/", CourseEnrollmentListView.as_view(), name="enrollments"),
    path("assignments/", CourseAssignmentListView.as_view(), name="assignments"),
    path("offerings/", CourseOfferingListView.as_view(), name="offerings")
]