from rest_framework import serializers
from .models import Attendance, PendingAttendance
from class_sessions.models import  Session


class AttendanceCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Attendance
        fields = ["session"]
    
    def validate(self, attrs):
        session = attrs.get("session")

        try:
            Session.objects.select_related("course_offering__course").get(session_id=session, active=True)
        except Session.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Invalid or Inactive session"})
        
        return attrs
        
    def create(self, validated_data):
            request = self.context["request"]
            validated_data["student"] = request.user.student_profile

            attendance = Attendance.objects.create(**validated_data)
            
            return attendance


class PendingAttendanceCreateSerializer(serializers.ModelSerializer):
     
     
     class Meta:
          model = PendingAttendance
          fields = ["session", "adder", "added_students"]
        
     def create(self, data):
          added_students = data.get("added_students", [])
          session = data.get("session")
          adder = self.context["request"].user.student_profile

          created = []
          for student in added_students:
               obj = PendingAttendance.objects.create(session=session, adder=adder, added_students=student)
               created.append(obj)

               return created
          
class AttendanceStudentInfoSerializer(serializers.ModelSerializer):
        
     class Meta:
          model = Attendance
          fields = ["id", "session", "status", "create_at"]

class AttendanceLecturerInfoSerializer(serializers.ModelSerializer):
        
     class Meta:
          model = Attendance
          fields = ["id", "session", "status", "create_at"]