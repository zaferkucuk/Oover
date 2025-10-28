"""
Country Serializers for Django REST Framework

This module provides serializers for the Country model, enabling
API endpoints for country data in the Oover sport prediction application.

Author: Oover Development Team
Date: October 2025
"""

from rest_framework import serializers
from typing import Dict, Any


class CountrySerializer(serializers.Serializer):
    """Base serializer for Country model"""
    
    id = serializers.CharField(max_length=10, required=True)
    name = serializers.CharField(max_length=100, required=True)
    code = serializers.CharField(max_length=10, required=True)
    flag = serializers.CharField(max_length=50, required=True)
    is_international = serializers.BooleanField(default=False, required=False)
    is_active = serializers.BooleanField(default=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_id(self, value: str) -> str:
        """Validate country ID format"""
        value = value.strip().lower()
        if len(value) < 2 or len(value) > 10:
            raise serializers.ValidationError(
                "Country ID must be between 2 and 10 characters"
            )
        if not value.isalnum():
            raise serializers.ValidationError(
                "Country ID must be alphanumeric"
            )
        return value
    
    def validate_code(self, value: str) -> str:
        """Validate country code format"""
        value = value.strip().upper()
        if len(value) < 2 or len(value) > 10:
            raise serializers.ValidationError(
                "Country code must be between 2 and 10 characters"
            )
        if not value.isalnum():
            raise serializers.ValidationError(
                "Country code must be alphanumeric"
            )
        return value


class CountryCreateSerializer(CountrySerializer):
    """Serializer for creating new countries"""
    pass


class CountryUpdateSerializer(serializers.Serializer):
    """Serializer for updating existing countries"""
    
    id = serializers.CharField(max_length=10, required=True)
    name = serializers.CharField(max_length=100, required=False)
    code = serializers.CharField(max_length=10, required=False)
    flag = serializers.CharField(max_length=50, required=False)
    is_international = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        update_fields = {k: v for k, v in attrs.items() if k != 'id'}
        if not update_fields:
            raise serializers.ValidationError(
                "At least one field must be provided for update"
            )
        return attrs


class MinimalLeagueSerializer(serializers.Serializer):
    """Minimal league representation"""
    id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    logo = serializers.CharField(max_length=500, allow_null=True)
    is_active = serializers.BooleanField()


class MinimalTeamSerializer(serializers.Serializer):
    """Minimal team representation"""
    id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    logo = serializers.CharField(max_length=500, allow_null=True)
    is_active = serializers.BooleanField()


class CountryWithRelationsSerializer(CountrySerializer):
    """Country serializer with relationships"""
    leagues = MinimalLeagueSerializer(many=True, read_only=True, required=False)
    teams = MinimalTeamSerializer(many=True, read_only=True, required=False)
    leagues_count = serializers.IntegerField(read_only=True, required=False)
    teams_count = serializers.IntegerField(read_only=True, required=False)


class CountryFilterSerializer(serializers.Serializer):
    """Serializer for country query filters"""
    is_active = serializers.BooleanField(required=False)
    is_international = serializers.BooleanField(required=False)
    name_contains = serializers.CharField(max_length=100, required=False)
    ids = serializers.ListField(child=serializers.CharField(), required=False)
    codes = serializers.ListField(child=serializers.CharField(), required=False)
    sort_by = serializers.ChoiceField(
        choices=['name', 'code', 'created_at', 'updated_at'],
        default='name',
        required=False
    )
    sort_order = serializers.ChoiceField(
        choices=['asc', 'desc'],
        default='asc',
        required=False
    )
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=50,
        required=False
    )
    include_counts = serializers.BooleanField(default=False, required=False)
    include_relations = serializers.BooleanField(default=False, required=False)


class CountryListResponseSerializer(serializers.Serializer):
    """Paginated country list response"""
    data = CountrySerializer(many=True)
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class CountryResponseSerializer(serializers.Serializer):
    """Single country response"""
    data = CountryWithRelationsSerializer()
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(required=False, allow_blank=True)


class CountryOperationResultSerializer(serializers.Serializer):
    """Country operation result"""
    success = serializers.BooleanField()
    data = CountrySerializer(required=False, allow_null=True)
    message = serializers.CharField()
    error = serializers.CharField(required=False, allow_blank=True)
