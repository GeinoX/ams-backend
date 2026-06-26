from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Student, Lecturer, Staff, Faculty

User = get_user_model()


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