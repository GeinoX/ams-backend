from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers

from .models import PasswordResetOTP


User = get_user_model()
from .models import (
    Faculty,
    Student,
    Lecturer,
    Staff,
)

User = get_user_model()


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            "id",
            "name",
        ]


# ============================================================
# LOGIN SERIALIZERS
# ============================================================

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class StudentTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            self.user.student_profile
        except Student.DoesNotExist:
            raise serializers.ValidationError(
                "This account is not registered as a student."
            )

        data["must_change_password"] = self.user.must_change_password

        return data


class LecturerTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            self.user.lecturer_profile
        except Lecturer.DoesNotExist:
            raise serializers.ValidationError(
                "This account is not registered as a lecturer."
            )

        data["must_change_password"] = self.user.must_change_password

        return data


class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            self.user.staff_profile
        except Staff.DoesNotExist:
            raise serializers.ValidationError(
                "This account is not registered as staff."
            )

        data["must_change_password"] = self.user.must_change_password

        return data


# ============================================================
# USER INFO SERIALIZERS
# ============================================================

class StudentInfoSerializer(serializers.ModelSerializer):
    matricule = serializers.CharField(
        source="matricule",
        read_only=True,
    )

    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "matricule",
            "name",
            "image",
        ]

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url

        return None


class LecturerInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Lecturer
        fields = [
            "employee_id",
            "name",
            "image",
        ]

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url

        return None


class StaffInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = [
            "position",
            "name",
            "image",
        ]

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url

        return None


# ============================================================
# BASE REGISTRATION SERIALIZER
# ============================================================

class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    profile_image_url = serializers.URLField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

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

    def create_user(self, validated_data):
        profile_image_url = validated_data.pop(
            "profile_image_url",
            None,
        )

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        if profile_image_url:
            # Keep your existing Cloudinary/profile-image
            # handling here if you already have one.
            pass

        return user


# ============================================================
# STUDENT REGISTRATION
# ============================================================

class StudentRegisterSerializer(BaseRegisterSerializer):
    matricule = serializers.CharField(
        max_length=15,
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "matricule",
        ]

    def validate_matricule(self, value):
        if Student.objects.filter(matricule=value).exists():
            raise serializers.ValidationError(
                "A student with this matricule already exists."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        matricule = validated_data.pop("matricule")

        user = self.create_user(validated_data)

        Student.objects.create(
            user=user,
            matricule=matricule,
        )

        return user


# ============================================================
# LECTURER SELF-REGISTRATION
# ============================================================

class LecturerRegisterSerializer(BaseRegisterSerializer):
    employee_id = serializers.CharField(
        max_length=50,
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "employee_id",
        ]

    def validate_employee_id(self, value):
        if Lecturer.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                "A lecturer with this employee ID already exists."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        employee_id = validated_data.pop("employee_id")

        user = self.create_user(validated_data)

        Lecturer.objects.create(
            user=user,
            employee_id=employee_id,
        )

        return user


# ============================================================
# STAFF REGISTRATION
# ============================================================

class StaffRegisterSerializer(BaseRegisterSerializer):
    position = serializers.CharField(
        max_length=100,
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "position",
        ]

    @transaction.atomic
    def create(self, validated_data):
        position = validated_data.pop("position")

        user = self.create_user(validated_data)

        Staff.objects.create(
            user=user,
            position=position,
        )

        return user


# ============================================================
# ADMIN CREATE LECTURER
# ============================================================

import secrets
import string


class AdminCreateLecturerSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=150,
    )

    last_name = serializers.CharField(
        max_length=150,
    )

    school_email = serializers.EmailField()

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    gender = serializers.ChoiceField(
        choices=User.GenderChoices.choices,
    )

    phone = serializers.CharField(
        max_length=20,
    )

    # faculty = serializers.PrimaryKeyRelatedField(
    #     queryset=Faculty.objects.all(),
    #     required=False,
    #     allow_null=True,
    # )

    employee_id = serializers.CharField(
        max_length=50,
    )

    def validate_school_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(
            school_email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this school email already exists."
            )

        return value

    def validate_employee_id(self, value):
        value = value.strip()

        if Lecturer.objects.filter(
            employee_id=value
        ).exists():
            raise serializers.ValidationError(
                "A lecturer with this employee ID already exists."
            )

        return value

    @staticmethod
    def generate_temporary_password(length=12):
        alphabet = (
            string.ascii_letters
            + string.digits
            + "!@#$%^&*"
        )

        return "".join(
            secrets.choice(alphabet)
            for _ in range(length)
        )

    @transaction.atomic
    def create(self, validated_data):
        employee_id = validated_data.pop(
            "employee_id"
        )

        temporary_password = (
            self.generate_temporary_password()
        )

        user = User.objects.create_user(
            password=temporary_password,
            **validated_data,
        )

        user.must_change_password = True

        user.save(
            update_fields=[
                "must_change_password",
            ]
        )

        lecturer = Lecturer.objects.create(
            user=user,
            employee_id=employee_id,
        )

        # Temporary internal attribute.
        # This is NOT returned to the client.
        lecturer._temporary_password = temporary_password

        return lecturer


# ============================================================
# CHANGE PASSWORD
# ============================================================

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.check_password(
            attrs["old_password"]
        ):
            raise serializers.ValidationError({
                "old_password": (
                    "Current password is incorrect."
                )
            })

        if (
            attrs["new_password"]
            != attrs["confirm_password"]
        ):
            raise serializers.ValidationError({
                "confirm_password": (
                    "Passwords do not match."
                )
            })

        if (
            attrs["old_password"]
            == attrs["new_password"]
        ):
            raise serializers.ValidationError({
                "new_password": (
                    "New password must be different "
                    "from the current password."
                )
            })

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user

        user.set_password(
            self.validated_data["new_password"]
        )

        user.must_change_password = False

        user.save(
            update_fields=[
                "password",
                "must_change_password",
            ]
        )

        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    school_email = serializers.EmailField()

    def validate_school_email(self, value):
        value = value.lower().strip()

        try:
            user = User.objects.get(
                school_email__iexact=value
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account exists with this email address."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        self.user = user

        return value

    def save(self, **kwargs):
        from datetime import timedelta
        import secrets

        user = self.user

        # Generate a 6-digit OTP
        otp = f"{secrets.randbelow(1_000_000):06d}"

        now = timezone.now()

        # Invalidate any previous OTP
        PasswordResetOTP.objects.filter(
            user=user,
            is_used=False,
        ).update(
            is_used=True
        )

        # Create new OTP
        reset_otp = PasswordResetOTP.objects.create(
            user=user,
            otp=otp,
            expires_at=now + timedelta(minutes=10),
        )

        return reset_otp


class PasswordResetVerifySerializer(serializers.Serializer):
    school_email = serializers.EmailField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate(self, attrs):
        school_email = (
            attrs["school_email"]
            .lower()
            .strip()
        )

        otp = attrs["otp"].strip()

        try:
            user = User.objects.get(
                school_email__iexact=school_email
            )
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "school_email": (
                    "No account exists with this email address."
                )
            })

        try:
            reset_otp = PasswordResetOTP.objects.get(
                user=user,
                otp=otp,
                is_used=False,
            )
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({
                "otp": "Invalid OTP."
            })

        if not reset_otp.is_valid():
            raise serializers.ValidationError({
                "otp": "This OTP has expired or has already been used."
            })

        attrs["user"] = user
        attrs["reset_otp"] = reset_otp

        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    school_email = serializers.EmailField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate(self, attrs):
        school_email = (
            attrs["school_email"]
            .lower()
            .strip()
        )

        otp = attrs["otp"].strip()

        try:
            user = User.objects.get(
                school_email__iexact=school_email
            )
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "school_email": (
                    "No account exists with this email address."
                )
            })

        try:
            reset_otp = PasswordResetOTP.objects.get(
                user=user,
                otp=otp,
                is_used=False,
            )
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({
                "otp": "Invalid OTP."
            })

        if not reset_otp.is_valid():
            raise serializers.ValidationError({
                "otp": (
                    "This OTP has expired or "
                    "has already been used."
                )
            })

        if (
            attrs["new_password"]
            != attrs["confirm_password"]
        ):
            raise serializers.ValidationError({
                "confirm_password": (
                    "Passwords do not match."
                )
            })

        if user.check_password(
            attrs["new_password"]
        ):
            raise serializers.ValidationError({
                "new_password": (
                    "New password must be different "
                    "from your current password."
                )
            })

        attrs["user"] = user
        attrs["reset_otp"] = reset_otp

        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        reset_otp = self.validated_data["reset_otp"]
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)

        # If the user was using a temporary password,
        # successfully resetting the password also means
        # they no longer need to change it.
        user.must_change_password = False

        user.save(
            update_fields=[
                "password",
                "must_change_password",
            ]
        )

        reset_otp.is_used = True

        reset_otp.save(
            update_fields=[
                "is_used",
            ]
        )

        return user