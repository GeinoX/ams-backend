from django.urls.conf import path
from .views import (CourseAssignmentListView, CourseEnrollmentCreateView, 
                    CourseOfferingListView, CourseEnrollmentListView,
                    CourseEnrollmentDeleteView)



urlpatterns = [
    path("student/enroll/", CourseEnrollmentCreateView.as_view(), name="enroll"),
    path("student/enrollments/", CourseEnrollmentListView.as_view(), name="enrollments"),
    path("lecturer/assignments/", CourseAssignmentListView.as_view(), name="assignments"),
    path("student/offerings/", CourseOfferingListView.as_view(), name="offerings"),
    path("enrollments/<int:course_offering_id>/", CourseEnrollmentDeleteView.as_view(), name="course-enrollment-delete"),
]