from rest_framework import serializers
from .models import Session


class CreateSessionSerializer(serializers.Serializer):

    class Meta:
        model = Session
        field = ["id", "course_offering"]


    def validate_id(self, value: str) -> str:
        if Session.objects.filter(id=value).exists():
            return serializers.ValidationError("This session already exists")
        return value
    
    def create(self, validated_data):
        return Session.objects.create(**validated_data)
    