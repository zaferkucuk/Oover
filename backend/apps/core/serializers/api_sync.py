"""
API Sync Serializers

Serializers for API sync operation tracking.
"""

from rest_framework import serializers
from api_integrations.models import APISync


class APISyncListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for API sync list view
    
    Used in paginated lists for performance.
    """
    
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = APISync
        fields = [
            'id',
            'provider',
            'resource_type',
            'status',
            'started_at',
            'completed_at',
            'duration',
            'records_processed',
            'records_created',
            'records_updated',
            'records_failed',
        ]
        read_only_fields = fields
    
    def get_duration(self, obj):
        """Get sync duration in seconds"""
        return obj.duration


class APISyncDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for API sync detail view
    
    Includes all fields including errors and metadata.
    """
    
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = APISync
        fields = [
            'id',
            'provider',
            'resource_type',
            'status',
            'started_at',
            'completed_at',
            'duration',
            'records_processed',
            'records_created',
            'records_updated',
            'records_failed',
            'errors',
            'error_message',
            'metadata',
        ]
        read_only_fields = fields
    
    def get_duration(self, obj):
        """Get sync duration in seconds"""
        return obj.duration
