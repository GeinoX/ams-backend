from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class BaseRegisterSerializer(serializers.Serializer):
    profile_image_url = serializers.ModelSerializer(read_only=True)

    class Meta:
        fields = ['first_name', 'last_name', 'school_email', 'email', 'gender', 'phone', 'faculty', 'password', 'profile_image', 'profile_image_url']
    

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None
    
    def validate(self, attrs):
        if User.objects.filter(school_email=attrs['school_email']).exists():
            raise serializers.ValidationError({"school_email" : "School email already exists"})
        if User.objects.filter(email=attrs['email']):
            raise serializers.ValidationError({"email" : "Email already exists"})
        
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user
    
class StudentRegisterSerializer(BaseRegisterSerializer):

    class Meta:
        fields = BaseRegisterSerializer.Meta.fields + ["matricule"]

    def validate(self, attrs):
        if Student.objects.filter(matricule=attrs["matricule"]).exists():
            return serializers.ValidationError({'matricule': 'User with this matricule already exists'})
        
    def create(self, validated_data):
        matricule = validated_data.pop("matricule")
        user = super().create(validated_data=validated_data)
        Student.objects.create(user=user, matricule=matricule)
        return user

class LecturerRegisterSerializer(BaseRegisterSerializer):

    class Meta:
        fields = BaseRegisterSerializer.Meta.fields + ["employee_id"]

    def validate(self, attrs):
        if Lecturer.objects.filter(employee_id=attrs["employee_id"]).exists():
            return serializers.ValidationError({"employee_id" : "Employee with this id already exists"})
        
    def create(self, validated_data):
        employee_id = validated_data.pop("employee_id")
        user = super().create(validated_data=validated_data)
        Lecturer.objects.create(employee_id=employee_id, user=user)
        return user
    
class StaffRegisterSerializer(BaseRegisterSerializer):

    class Meta:
        fields = BaseRegisterSerializer.Meta.fields + ["position"]

    def create(self, validated_data):
        position = validated_data.pop("position")
        user = super().create(validated_data=validated_data)
        Staff.objects.create(position=position, user=user)
        return user