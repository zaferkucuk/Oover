"""
API Integration Serializers

DRF serializers for API endpoints.
"""

from rest_framework import serializers
from .models import APISync


class APISyncSerializer(serializers.ModelSerializer):
    """Serializer for APISync model."""
    
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = APISync
        fields = '__all__'
        read_only_fields = ['id', 'started_at', 'completed_at', 'duration']


class FetchTeamsSerializer(serializers.Serializer):
    """Serializer for fetch teams request."""
    
    country = serializers.CharField(
        required=False,
        max_length=2,
        help_text='Country code (e.g., GB, ES, IT)'
    )
    league = serializers.CharField(
        required=False,
        help_text='League ID'
    )
    all_european = serializers.BooleanField(
        default=False,
        help_text='Fetch all European teams'
    )
    dry_run = serializers.BooleanField(
        default=False,
        help_text='Test without saving to database'
    )
    
    def validate(self, data):
        """Validate that at least one option is provided."""
        if not any([data.get('country'), data.get('league'), data.get('all_european')]):
            raise serializers.ValidationError(
                "Must provide at least one of: country, league, or all_european"
            )
        return data


class SyncTeamsSerializer(serializers.Serializer):
    """Serializer for sync teams request."""
    
    fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='List of fields to update'
    )
    force = serializers.BooleanField(
        default=False,
        help_text='Force update even if recently updated'
    )