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

# api/serializers.py
class GarbageReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GarbageReport
        fields = ('id', 'image', 'description', 'latitude', 'longitude', 
                 'reported_at', 'status', 'zone', 'user', 'username')
        read_only_fields = ('user', 'reported_at', 'zone', 'status')