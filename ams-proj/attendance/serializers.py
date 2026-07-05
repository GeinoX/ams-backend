from rest_framework import serializers
from .models import Attendance, PendingAttendance
from class_sessions.models import  Session
from django.db import IntegrityError



class AttendanceCreateSerializer(serializers.ModelSerializer):
    session = serializers.UUIDField()

    class Meta:
        model = Attendance
        fields = ["session"]

    def validate(self, attrs):
        session_id = attrs.get("session")

        try:
            session = Session.objects.select_related(
                "course_offering__course"
            ).get(session_id=session_id, active=True)
        except Session.DoesNotExist:
            raise serializers.ValidationError({"session": "Invalid or Inactive session"})

        attrs["session"] = session
        return attrs


    def create(self, validated_data):
        request = self.context["request"]
        student = request.user.student_profile
        session = validated_data.get("session")

        validated_data["student"] = student
        validated_data["status"] = Attendance.AttendanceChoices.PRESENT

        try:
            attendance = Attendance.objects.create(**validated_data)
        except IntegrityError:
         raise serializers.ValidationError(
                {"detail": "This student has already been marked for this session"}
            )

        return attendance

class PendingAttendanceCreateSerializer(serializers.ModelSerializer):
    added_student = serializers.CharField(required=False, allow_null=True)  # ← optional, accepts matricule
    session = serializers.UUIDField()  # ← consistent with AttendanceCreateSerializer

    class Meta:
        model = PendingAttendance
        fields = ["session", "added_student"]

    def validate(self, attrs):
        session_id = attrs.get("session")
        added_student_matricule = attrs.get("added_student")

        # validate session exists and is active
        try:
            session = Session.objects.get(session_id=session_id, active=True)
        except Session.DoesNotExist:
            raise serializers.ValidationError({"session": "Invalid or Inactive session"})

        attrs["session"] = session  # ← replace UUID with Session object

        # validate added_student only if provided
        if added_student_matricule:
            from auth_app.models import Student
            try:
                added_student = Student.objects.get(matricule=added_student_matricule)
            except Student.DoesNotExist:
                raise serializers.ValidationError({"added_student": "Student not found"})
            attrs["added_student"] = added_student  # ← replace matricule with Student object

        return attrs

    def create(self, validated_data):
        added_student = validated_data.get("added_student")

        if not added_student:
            return None  # ← no pending attendance needed if no added_student

        adder = self.context["request"].user.student_profile
        session = validated_data.get("session")

        obj = PendingAttendance.objects.create(
            session=session,
            adder=adder,
            added_student=added_student
        )
        return obj
          
class AttendanceStudentInfoSerializer(serializers.ModelSerializer):
        
     class Meta:
          model = Attendance
          fields = ["id", "session", "status", "created_at"]

class AttendanceLecturerInfoSerializer(serializers.ModelSerializer):
        
     class Meta:
          model = Attendance
          fields = ["id", "session", "status", "created_at"]