from rest_framework import serializers
from .models import *


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ["id", "name", "credit", "level"]

class CourseOfferingListSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    credits = serializers.CharField(source="course.credits", read_only=True)
    semester = serializers.CharField(source="semester.name", read_only=True)

    class Meta:
        model = CourseOffering
        fields = ["id", "course", "course_id", "course_name", "credits", "semester", "year"]

class CourseAssignmentSerializer(serializers.ModelSerializer):
    
    lecturer_name = serializers.CharField(source="lecturer.user.name", read_only=True)
    course_id = serializers.CharField(source="course_offering.course.course_id", read_only=True)
    course_name = serializers.CharField(source="course_offering.course.course_name", read_only=True)
    semester = serializers.CharField(source="course_offering.semester.name", read_only=True)
    year = serializers.IntegerField(source="course_offering.year", read_only=True)

    class Meta:
        model = CourseAssignment
        fields = [
            "id", "lecturer", "lecturer_name", "course_offering",
            "course_id", "course_name", "semester", "year",
        ]


class CourseEnrollmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseEnrollment
        fields = ["course_offering"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        try:
            student = user.student_profile
        except Exception:
            raise serializers.ValidationError("User does not have a student profile.")

        course_offering = attrs.get("course_offering")

        if CourseEnrollment.objects.filter(student=student, course_offering=course_offering).exists():
            raise serializers.ValidationError("Already enrolled in this course offering.")

        return attrs
    
    def create(self, validated_data):
        return CourseEnrollment.objects.create(**validated_data)
    

class CourseEnrollmentListSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source="course_offering.course.course_id", read_only=True)
    course_name = serializers.CharField(source="course_offering.course.course_name", read_only=True)
    credits = serializers.CharField(source="course_offering.course.credits", read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = ["course_offering", "course_id", "course_name", "credits "]
