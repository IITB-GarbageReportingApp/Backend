from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GarbageReport
import random

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class GarbageReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarbageReport
        fields = '__all__'
        read_only_fields = ('user', 'reported_at')