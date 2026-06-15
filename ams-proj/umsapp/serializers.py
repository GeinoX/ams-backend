from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Student, Teacher, Course, CourseOffering, Enrollment,
    Session, CourseAssignment, Attendance, PendingAttendance
)

User = get_user_model()


# ==============================
# JWT Token
# ==============================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get(self.username_field)
        password = attrs.get('password')
        user = self._get_user_by_email(email)
        self._check_password(user, password)
        return self._get_tokens_for_user(user)

    def _get_user_by_email(self, email):
        # Try student school_email first
        try:
            student = Student.objects.get(school_email=email)
            return student.user
        except Student.DoesNotExist:
            pass

        # Try teacher regular email
        try:
            user = User.objects.get(email=email)
            if hasattr(user, 'teacher_profile'):
                return user
            raise serializers.ValidationError(_("No teacher profile associated with this email."))
        except User.DoesNotExist:
            pass

        raise serializers.ValidationError(_("No account found with this email."))

    def _check_password(self, user, password):
        if not user.check_password(password):
            raise serializers.ValidationError(_("Incorrect password."))

    def _get_tokens_for_user(self, user):
        refresh = super().get_token(user)
        refresh['name'] = user.name
        refresh['email'] = user.email
        is_teacher = hasattr(user, 'teacher_profile')
        refresh['user_type'] = 'teacher' if is_teacher else 'student'
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# ==============================
# Registration
# ==============================
class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    profile_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'gender', 'phone', 'password', 'profile_image', 'profile_image_url']

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user


class StudentRegisterSerializer(BaseRegisterSerializer):
    matricule = serializers.CharField(write_only=True)
    school_email = serializers.EmailField(write_only=True)
    program = serializers.CharField(write_only=True, required=False, default="")

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ['matricule', 'school_email', 'program']

    def validate(self, data):
        if Student.objects.filter(matricule=data['matricule']).exists():
            raise serializers.ValidationError("Matricule already exists.")
        if Student.objects.filter(school_email=data['school_email']).exists():
            raise serializers.ValidationError("School email already exists.")
        return data

    def create(self, validated_data):
        matricule = validated_data.pop("matricule")
        school_email = validated_data.pop("school_email")
        program = validated_data.pop("program", "")
        user = super().create(validated_data)
        Student.objects.create(
            user=user,
            matricule=matricule,
            school_email=school_email,
            program=program,
        )
        return user


class TeacherRegisterSerializer(BaseRegisterSerializer):
    employee_id = serializers.CharField(write_only=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ['employee_id']

    def validate(self, data):
        if Teacher.objects.filter(employee_id=data['employee_id']).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return data

    def create(self, validated_data):
        employee_id = validated_data.pop("employee_id")
        user = super().create(validated_data)
        user.is_teacher = True
        user.save()
        Teacher.objects.create(user=user, employee_id=employee_id)
        return user


# ==============================
# Course & Offering
# ==============================
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["course_id", "course_name", "credits", "level"]


class CourseOfferingSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseOffering
        fields = ["course_offering_id", "course", "semester", "year"]


# ==============================
# Enrollment
# ==============================
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["course_offering"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        try:
            student = user.student_profile
        except Exception:
            raise serializers.ValidationError("User does not have a student profile.")

        course_offering = attrs.get("course_offering")

        if Enrollment.objects.filter(student=student, course_offering=course_offering).exists():
            raise serializers.ValidationError("Already enrolled in this course offering.")

        return attrs

    def create(self, validated_data):
        student = self.context["request"].user.student_profile
        validated_data["student"] = student
        return Enrollment.objects.create(**validated_data)


class EnrollmentViewSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source="course_offering.course.course_id", read_only=True)
    course_name = serializers.CharField(source="course_offering.course.course_name", read_only=True)
    semester = serializers.CharField(source="course_offering.semester.name", read_only=True)
    semester_is_active = serializers.BooleanField(source="course_offering.semester.is_active", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "course_id", "course_name", "semester", "semester_is_active"]
        read_only_fields = fields


# ==============================
# Attendance Check-In
# ==============================
class AttendanceCheckInSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    course_id = serializers.CharField()
    added_students = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    def validate(self, data):
        session_id = data.get("session_id")
        course_id = data.get("course_id")
        added_students = data.get("added_students", [])

        try:
            session = Session.objects.select_related(
                "course_offering__course"
            ).get(session_id=session_id, active=True)
        except Session.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Invalid or inactive session."})

        if str(session.course_offering.course.course_id) != str(course_id):
            raise serializers.ValidationError({
                "course_id": f"Session belongs to a different course: {session.course_offering.course.course_name}."
            })

        if added_students:
            enrolled_matricules = set(
                Enrollment.objects.filter(
                    course_offering=session.course_offering
                ).values_list("student__matricule", flat=True)
            )
            invalid = [m for m in added_students if m not in enrolled_matricules]
            if invalid:
                raise serializers.ValidationError({
                    "added_students": f"Not enrolled in this course: {', '.join(invalid)}."
                })

        self.context["session"] = session
        return data


# ==============================
# Session
# ==============================
class SessionSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source="course_offering.course.course_id", read_only=True)
    course_name = serializers.CharField(source="course_offering.course.course_name", read_only=True)
    semester = serializers.CharField(source="course_offering.semester.name", read_only=True)
    year = serializers.IntegerField(source="course_offering.year", read_only=True)

    class Meta:
        model = Session
        fields = [
            "session_id", "course_offering", "course_id", "course_name",
            "semester", "year", "start_time", "end_time", "active",
        ]
        read_only_fields = ["session_id", "start_time", "end_time"]


# ==============================
# Course Assignment
# ==============================
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
            "course_id", "course_name", "semester", "year", "created_at",
        ]
        read_only_fields = ["created_at"]


class LecturerCourseAssignmentSerializer(serializers.ModelSerializer):
    course_offering_id = serializers.CharField(source="course_offering.course_offering_id")
    course_id = serializers.CharField(source="course_offering.course.course_id")
    course_name = serializers.CharField(source="course_offering.course.course_name")
    semester = serializers.CharField(source="course_offering.semester.name")
    year = serializers.IntegerField(source="course_offering.year")

    class Meta:
        model = CourseAssignment
        fields = ["course_offering_id", "course_id", "course_name", "semester", "year", "created_at"]


# ==============================
# Student Attendance
# ==============================
class StudentSessionAttendanceSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    session_id = serializers.UUIDField()
    date = serializers.DateTimeField()
    status = serializers.CharField()


class StudentAttendanceSummarySerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    attended = serializers.IntegerField()
    missed = serializers.IntegerField()


# ==============================
# Teacher — Course Attendance Stats
# ==============================
class CourseAttendanceStatsSerializer(serializers.Serializer):
    matricule = serializers.CharField()
    name = serializers.CharField()
    image = serializers.CharField(allow_null=True)
    time = serializers.TimeField(allow_null=True)
    attended = serializers.IntegerField()
    missed = serializers.IntegerField()
    last_attended = serializers.DateField(allow_null=True)


# ==============================
# Pending Attendance
# ==============================
class PendingAttendanceSerializer(serializers.ModelSerializer):
    adder_name = serializers.CharField(source="adder.user.name", read_only=True)
    adder_matricule = serializers.CharField(source="adder.matricule", read_only=True)
    added_student_name = serializers.CharField(source="added_student.user.name", read_only=True)
    added_student_matricule = serializers.CharField(source="added_student.matricule", read_only=True)
    added_student_image = serializers.SerializerMethodField()

    class Meta:
        model = PendingAttendance
        fields = [
            "id", "session_id",
            "adder_name", "adder_matricule",
            "added_student_name", "added_student_matricule", "added_student_image",
            "approved", "rejected", "timestamp",
        ]

    def get_added_student_image(self, obj):
        img = obj.added_student.user.profile_image
        return img.url if img else None