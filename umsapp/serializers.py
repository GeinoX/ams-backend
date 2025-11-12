from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model, authenticate
from .models import Student, Course, Enrollment, Timetable, Session, Attendance, Teacher, Semester
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import uuid

User = get_user_model()




# serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import Student

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from .models import Student, Teacher

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # authenticate using email

    def validate(self, attrs):
        email = attrs.get(self.username_field)
        password = attrs.get('password')

        user = None

        # Try Student
        try:
            student = Student.objects.get(school_email=email)
            print(student)
            user = student.user
            print(user)
        except Student.DoesNotExist:
            pass

        # Try Teacher if not found
        if not user:
            try:
                user_obj = User.objects.get(email=email)
                print(user_obj.email)
                if hasattr(user_obj, 'teacher_profile'):
                    print("User is a teacher")
                    user = user_obj  # use the User object directly
                else:
                    print("User is not a teacher")
                    raise serializers.ValidationError(_("No teacher profile associated with this email."))
            except User.DoesNotExist:
                raise serializers.ValidationError(_("No student or teacher found with this email."))

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError(_("Incorrect password."))

        # Generate tokens
        refresh = super().get_token(user)

        # Add custom claims
        refresh['name'] = getattr(user, 'name', '')
        refresh['email'] = user.email
        refresh['user_type'] = getattr(user, 'user_type', 'Unknown')

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }




# ----------------------------
# Base User Registration Serializer
# ----------------------------
class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.CharField(write_only=True, required=False)  # extra field

    class Meta:
        model = User
        fields = ['name', 'email', 'gender', 'phone', 'password', 'profile_image', 'user_type']
        """
        serializer.initial_data
# {'email': 'john@example.com', 'name': 'John', 'password': 'secret'}

serializer.fields
# OrderedDict([('email', EmailField()), ('name', CharField()), ('password', CharField())])
        """

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        # Remove user_type before creating user
        validated_data.pop('user_type', None)
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user


# ----------------------------
# Student Registration Serializer
# ----------------------------
class StudentRegisterSerializer(BaseRegisterSerializer):
    matricule = serializers.CharField(write_only=True)
    school_email = serializers.EmailField(write_only=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ['matricule', 'school_email']

    def validate(self, data):
        if Student.objects.filter(matricule=data['matricule']).exists():
            raise serializers.ValidationError("Matricule already exists")
        if Student.objects.filter(school_email=data['school_email']).exists():
            raise serializers.ValidationError("School email already exists")
        return data

    def create(self, validated_data):
        matricule = validated_data.pop("matricule")
        school_email = validated_data.pop("school_email")
        user = super().create(validated_data)
        Student.objects.create(user=user, matricule=matricule, school_email=school_email)
        return user


class TeacherRegisterSerializer(BaseRegisterSerializer):
    employee_id = serializers.CharField(write_only=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ['employee_id']

    def validate(self, data):
        if Teacher.objects.filter(employee_id=data['employee_id']).exists():
            raise serializers.ValidationError("Employee already exists")
        return data

    def create(self, validated_data):
        employee_id = validated_data.pop("employee_id")
        user = super().create(validated_data)
        Teacher.objects.create(user=user, employee_id=employee_id)
        return user

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'credits', 'status', 'level']

class TimetableSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)

    class Meta:
        model = Timetable
        fields = ['course_name', 'day', 'start_time', 'end_time', 'hall']




class EnrollmentSerializer(serializers.ModelSerializer):
    # Write-only input fields for creating enrollment
    course_name = serializers.CharField(write_only=True)
    period = serializers.CharField(write_only=True)
    year = serializers.IntegerField(write_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'student', 'course', 'status', 'enrollment_date',
            'period', 'year', 'grade', 'course_name'
        ]
        read_only_fields = ['student', 'course', 'status', 'enrollment_date', 'grade']

    def validate(self, data):
        course_name = data.get("course_name")
        period = data.get('period')
        year = data.get('year')

        # Validate course existence
        try:
            course = Course.objects.get(course_id=course_name)
        except Course.DoesNotExist:
            raise serializers.ValidationError({"course_name": "Course not found."})

        # Validate semester existence and current status
        try:
            semester = Semester.objects.get(period=period, year=year, status="Current")
        except Semester.DoesNotExist:
            raise serializers.ValidationError({"semester": "Invalid semester or semester not available."})

        # Attach the resolved objects to validated_data to reuse in create()
        data['course_obj'] = course
        data['semester_obj'] = semester

        return data

    def create(self, validated_data):
        # Get the resolved objects from validate()
        course = validated_data.pop('course_obj')
        semester = validated_data.pop('semester_obj')

        # Get the logged-in student
        try:
            student = self.context['request'].user.student_profile
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student": "Logged-in user is not a student."})

        # Prevent duplicate enrollment
        if Enrollment.objects.filter(student=student, course=course, semester=semester).exists():
            raise serializers.ValidationError({"enrollment": "You are already enrolled in this course for this semester."})

        # Create the enrollment
        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            semester=semester,
            status='enrolled'
        )
        return enrollment


class EnrollmentView(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'status', 'enrollment_date', 'grade']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['session', 'student']

# attendance/serializers.py


from rest_framework import serializers
from .models import Session, Attendance

class AttendanceCheckInSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    course_id = serializers.CharField()
    added_students = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    def validate(self, data):
        session_id = data.get('session_id')
        course_id = data.get('course_id')
        added_students = data.get('added_students', [])

        # Check valid & active session
        try:
            session = Session.objects.select_related('course').get(session_id=session_id, active=True)
        except Session.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Invalid or inactive session."})

        # Ensure session course matches provided course_id
        if str(session.course.course_id) != str(course_id):
            raise serializers.ValidationError({
                "course_id": f"This session belongs to a different course: {session.course.course_name}."
            })

        # Check that each added student is enrolled in this course
        if added_students:
            enrolled_students = set(
                Enrollment.objects.filter(course=session.course).values_list('student__matricule', flat=True)
            )
            invalid_students = [sid for sid in added_students if sid not in enrolled_students]

            if invalid_students:
                raise serializers.ValidationError({
                    "added_students": f"Some students are not enrolled in this course: {', '.join(invalid_students)}."
                })

        #  Store session for later use
        self.context['session'] = session
        return data

    
class SessionSerializer(serializers.ModelSerializer):
    course = serializers.CharField(write_only=True)  # teacher enters by name
    course_name = serializers.CharField(source='course.course_name', read_only=True)  # display name
    teacher_name = serializers.CharField(source='teacher.user.username', read_only=True)

    class Meta:
        
        model = Session
        fields = [
            'session_id',
            'teacher',
            'teacher_name',
            'course',
            'course_name',
            'start_time',
            'end_time',
            'active',
        ]
        read_only_fields = ['session_id', 'teacher', 'start_time', 'end_time']

from rest_framework import serializers
from .models import CourseAssignment

class CourseAssignmentSerializer(serializers.ModelSerializer):
    # Display teacher and course names instead of just their IDs
    teacher_name = serializers.CharField(source="teacher.user.name", read_only=True)
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_id = serializers.CharField(source="course.course_id", read_only=True)

    class Meta:
        model = CourseAssignment
        fields = [
            "id",            
            "teacher",       
            "teacher_name", 
            "course",       
            "course_id",
            "course_name",
            "semester",
            "year",
            "timestamp",
        ]
        read_only_fields = ["timestamp"]


# serializers.py (append)
class CourseStudentSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    name = serializers.CharField()
    school_email = serializers.EmailField()
    attendance_count = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    last_attended = serializers.DateTimeField(allow_null=True)



class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'
