from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GarbageReport, WorkerProfile

class WorkerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerProfile
        fields = ('id', 'zone', 'is_worker')

class UserSerializer(serializers.ModelSerializer):
    worker_profile = WorkerProfileSerializer(read_only=True)
    user_type = serializers.CharField(write_only=True, required=False)  # For login differentiation
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'worker_profile', 'user_type')
        extra_kwargs = {'password': {'write_only': True}}

class GarbageReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    worker_name = serializers.CharField(source='assigned_worker.user.username', read_only=True)
    worker_zone = serializers.IntegerField(source='assigned_worker.zone', read_only=True)
    
    class Meta:
        model = GarbageReport
        fields = (
            'id', 'image', 'description', 'latitude', 'longitude', 
            'reported_at', 'status', 'zone', 'user', 'username',
            'completion_image', 'completed_at', 'is_viewed',
            'worker_notes', 'worker_name', 'worker_zone', 'video'
        )
        read_only_fields = ('user', 'reported_at', 'zone', 'assigned_worker')
    username = serializers.CharField(source='user.username', read_only=True)
    worker_name = serializers.CharField(source='assigned_worker.user.username', read_only=True)
    worker_zone = serializers.IntegerField(source='assigned_worker.zone', read_only=True)
    
    class Meta:
        model = GarbageReport
        fields = (
            'id', 'image', 'description', 'latitude', 'longitude', 
            'reported_at', 'status', 'zone', 'user', 'username',
            'completion_image', 'completed_at', 'is_viewed',
            'worker_notes', 'worker_name', 'worker_zone', 'video'
        )
        read_only_fields = ('user', 'reported_at', 'zone', 'assigned_worker')
        