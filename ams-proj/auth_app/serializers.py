from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Student, Lecturer, Staff, Faculty
import random
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from .models import CustomUser, PasswordResetOTP
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from core.utils import get_enrollments, get_sessions

session = get_sessions()
course_enrollment = get_enrollments()
User = get_user_model()


class StudentTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, "student_profile"):
            raise serializers.ValidationError("You are not authorized to log in here")

        data["must_change_password"] = self.user.must_change_password
        return data

class LecturerTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, "lecturer_profile"):
            raise serializers.ValidationError("You are not authorized to log in here")

        data["must_change_password"] = self.user.must_change_password
        return data

class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, "staff_profile"):
            raise serializers.ValidationError("You are not authorized to log in here")

        data["must_change_password"] = self.user.must_change_password
        return data

class StudentInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ["matricule", "name", "image"]

    def get_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url
        return None


class LecturerInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Lecturer
        fields = ["employee_id", "name", "image"]

    def get_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url
        return None


class StaffInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ["position", "name", "image"]

    def get_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url
        return None

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ["id", "name"]


class BaseRegisterSerializer(serializers.ModelSerializer):
    """
    Shared registration serializer for all user types.
    Subclasses must implement `create()` to handle role-specific profile creation.
    """

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    profile_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "school_email",
            "email",
            "gender",
            "phone",
            "faculty",
            "password",
            "profile_image",
            "profile_image_url",
        ]
        extra_kwargs = {
            "profile_image": {"write_only": True, "required": False},
            "faculty": {"required": False},
            "email": {"required": False},
        }

    def get_profile_image_url(self, obj: User) -> str | None:
        if obj.profile_image:
            return obj.profile_image.url
        return None

    def validate_school_email(self, value: str) -> str:
        if User.objects.filter(school_email__iexact=value).exists():
            raise serializers.ValidationError("A user with this school email already exists.")
        return value.lower()

    def validate_email(self, value: str) -> str:
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower() if value else value

    @transaction.atomic
    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        return User.objects.create_user(**validated_data, password=password)


class StudentRegisterSerializer(BaseRegisterSerializer):
    matricule = serializers.CharField(max_length=15)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ["matricule"]

    def validate_matricule(self, value: str) -> str:
        if Student.objects.filter(matricule=value).exists():
            raise serializers.ValidationError("A student with this matricule already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data: dict) -> User:
        matricule = validated_data.pop("matricule")
        user = super().create(validated_data)
        Student.objects.create(user=user, matricule=matricule)
        return user


class LecturerRegisterSerializer(BaseRegisterSerializer):
    employee_id = serializers.CharField(max_length=50)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ["employee_id"]

    def validate_employee_id(self, value: str) -> str:
        if Lecturer.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("A lecturer with this employee ID already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data: dict) -> User:
        employee_id = validated_data.pop("employee_id")
        user = super().create(validated_data)
        Lecturer.objects.create(user=user, employee_id=employee_id)
        return user


class StaffRegisterSerializer(BaseRegisterSerializer):
    position = serializers.CharField(max_length=100)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ["position"]

    @transaction.atomic
    def create(self, validated_data: dict) -> User:
        position = validated_data.pop("position")
        user = super().create(validated_data)
        Staff.objects.create(user=user, position=position)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    school_email = serializers.EmailField()

    def validate_school_email(self, value):
        if not CustomUser.objects.filter(school_email=value).exists():
            raise serializers.ValidationError("No account found with this email")
        return value

    def save(self):
        school_email = self.validated_data["school_email"]
        user = CustomUser.objects.get(school_email=school_email)

        # generate 6 digit OTP
        otp = str(random.randint(100000, 999999))

        # delete any existing OTP for this user
        PasswordResetOTP.objects.filter(user=user).delete()

        # create new OTP valid for 10 minutes
        PasswordResetOTP.objects.create(
            user=user,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # send notification
        from notifications.services.notification_service import NotificationService
        NotificationService.password_reset_otp(user, otp)

        return user


class PasswordResetVerifySerializer(serializers.Serializer):
    school_email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        school_email = attrs.get("school_email")
        otp = attrs.get("otp")

        try:
            user = CustomUser.objects.get(school_email=school_email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"school_email": "No account found with this email"})

        try:
            otp_instance = PasswordResetOTP.objects.get(user=user, otp=otp)
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp": "Invalid OTP"})

        if not otp_instance.is_valid():
            raise serializers.ValidationError({"otp": "OTP has expired or already been used"})

        attrs["user"] = user
        attrs["otp_instance"] = otp_instance
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    school_email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        school_email = attrs.get("school_email")
        otp = attrs.get("otp")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        try:
            user = CustomUser.objects.get(school_email=school_email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"school_email": "No account found with this email"})

        try:
            otp_instance = PasswordResetOTP.objects.get(user=user, otp=otp)
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp": "Invalid OTP"})

        if not otp_instance.is_valid():
            raise serializers.ValidationError({"otp": "OTP has expired or already been used"})

        attrs["user"] = user
        attrs["otp_instance"] = otp_instance
        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp_instance = self.validated_data["otp_instance"]
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.must_change_password = False
        user.save()

        otp_instance.is_used = True
        otp_instance.save()

        from notifications.services.notification_service import NotificationService
        NotificationService.password_reset(user)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get("refresh")
        return attrs

    def save(self, user):
        # check if user is a student
        if hasattr(user, "student_profile"):
            student = user.student_profile

            # get all course offerings the student is enrolled in
            enrolled_offerings = course_enrollment.filter(
                student=student
            ).values_list("course_offering", flat=True)

            # check if any of those offerings have an active session
            active_session = session.filter(
                course_offering__in=enrolled_offerings,
                active=True
            ).exists()

            if active_session:
                raise serializers.ValidationError(
                    "You cannot logout while a session is active for your enrolled course. "
                    "Please wait until the session ends."
                )

        # no active session — proceed with blacklisting
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"refresh": "Token is invalid or already blacklisted"})


