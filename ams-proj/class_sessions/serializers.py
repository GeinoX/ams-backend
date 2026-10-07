from rest_framework import serializers
from .models import Session
from courses.models import CourseAssignment

class CreateSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ["session_id", "course_offering"]
        read_only_fields = ["session_id"]

    def validate_course_offering(self, offering):
        lecturer = self.context["request"].user.lecturer_profile

        # Adjust CourseAssignment and its field names to your project
        if not CourseAssignment.objects.filter(
            lecturer=lecturer,
            course_offering=offering,
        ).exists():
            raise serializers.ValidationError(
                "You are not assigned to this course offering."
            )

        if Session.objects.filter(course_offering=offering, active=True).exists():
            raise serializers.ValidationError(
                "A session is already active for this course offering."
            )

        return offering