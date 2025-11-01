"""
League Serializers for Core App

This module contains Django REST Framework serializers for the League model.
Provides serialization/deserialization for API endpoints.

Author: Oover Development Team
Date: October 2025
Updated: November 2025 - Added tier and confederation fields
"""

from rest_framework import serializers
from apps.core.models import League, Country, Sport


class LeagueListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for league list views
    
    Used for:
    - GET /api/v1/leagues/ (list all leagues)
    - Dropdown selections
    - Quick reference data
    
    Includes:
    - Basic league info (id, name, logo, external_id)
    - Nested country name (for display)
    - Nested sport name (for filtering)
    - League tier and confederation
    - Status flags (is_active)
    """
    
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True, allow_null=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    
    class Meta:
        model = League
        fields = [
            'id',
            'name',
            'country_name',
            'country_code',
            'sport_name',
            'logo',
            'external_id',
            'tier',
            'confederation',
            'is_active',
        ]
        read_only_fields = ['id']


class LeagueDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for league detail views
    
    Used for:
    - GET /api/v1/leagues/{id}/ (retrieve single league)
    - POST /api/v1/leagues/ (create new league)
    - PUT /api/v1/leagues/{id}/ (update league)
    - PATCH /api/v1/leagues/{id}/ (partial update)
    
    Includes:
    - All league fields
    - Nested country details (full object)
    - Nested sport details (full object)
    - Tier and confederation information
    - Timestamps
    """
    
    # Nested serializers for related objects
    country_details = serializers.SerializerMethodField()
    sport_details = serializers.SerializerMethodField()
    
    class Meta:
        model = League
        fields = [
            'id',
            'name',
            'country',
            'country_details',
            'sport',
            'sport_details',
            'logo',
            'external_id',
            'tier',
            'confederation',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_country_details(self, obj):
        """
        Get nested country information
        
        Returns:
            dict: Country details or None if no country assigned
        """
        if obj.country:
            return {
                'id': str(obj.country.id),
                'name': obj.country.name,
                'code': obj.country.code,
                'flag': obj.country.flag,
                'flag_url': obj.country.flag_url,
            }
        return None
    
    def get_sport_details(self, obj):
        """
        Get nested sport information
        
        Returns:
            dict: Sport details
        """
        return {
            'id': str(obj.sport.id),  # Consistent string conversion with country_details
            'name': obj.sport.name,
            'slug': obj.sport.slug,
            'icon': obj.sport.icon,
        }


class LeagueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new leagues
    
    Used for:
    - POST /api/v1/leagues/ (create new league)
    
    Validation:
    - Ensures sport_id exists
    - Ensures country_id exists (if provided)
    - Validates external_id format
    - Validates tier is positive integer (if provided)
    - Validates confederation format (if provided)
    """
    
    class Meta:
        model = League
        fields = [
            'name',
            'sport',
            'country',
            'logo',
            'external_id',
            'tier',
            'confederation',
            'is_active',
        ]
    
    def validate_name(self, value):
        """
        Validate league name
        
        Rules:
        - Must not be empty
        - Must be at least 2 characters
        - Should be unique per country (soft validation)
        
        Args:
            value: League name to validate
            
        Returns:
            str: Validated league name
            
        Raises:
            ValidationError: If validation fails
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "League name must be at least 2 characters long"
            )
        return value.strip()
    
    def validate_tier(self, value):
        """
        Validate league tier
        
        Rules:
        - Must be positive integer if provided
        - Typically 1-4 for major leagues
        
        Args:
            value: League tier to validate
            
        Returns:
            int: Validated tier
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            return value
        
        if value < 1:
            raise serializers.ValidationError(
                "League tier must be a positive integer"
            )
        
        return value
    
    def validate_confederation(self, value):
        """
        Validate confederation name
        
        Rules:
        - Optional field
        - Trim whitespace
        - Common values: UEFA, CONMEBOL, AFC, CAF, CONCACAF, OFC
        
        Args:
            value: Confederation name to validate
            
        Returns:
            str: Validated confederation name
        """
        if not value:
            return value
        
        return value.strip()
    
    def validate(self, attrs):
        """
        Validate entire league object
        
        Rules:
        - Check for duplicate league names in same country
        - Ensure external_id is unique if provided
        
        Args:
            attrs: Dictionary of all league attributes
            
        Returns:
            dict: Validated attributes
            
        Raises:
            ValidationError: If validation fails
        """
        name = attrs.get('name')
        country = attrs.get('country')
        external_id = attrs.get('external_id')
        
        # Check for duplicate name in same country
        if country:
            if League.objects.filter(name=name, country=country).exists():
                raise serializers.ValidationError({
                    'name': f"A league named '{name}' already exists in {country.name}"
                })
        
        # Check for duplicate external_id
        if external_id:
            if League.objects.filter(external_id=external_id).exists():
                raise serializers.ValidationError({
                    'external_id': f"A league with external_id '{external_id}' already exists"
                })
        
        return attrs


class LeagueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing leagues
    
    Used for:
    - PUT /api/v1/leagues/{id}/ (full update)
    - PATCH /api/v1/leagues/{id}/ (partial update)
    
    Allows updating:
    - name, logo, external_id
    - country (can be changed)
    - tier, confederation
    - is_active status
    
    Does NOT allow updating:
    - id (immutable)
    - sport (immutable after creation)
    - created_at, updated_at (auto-managed)
    """
    
    class Meta:
        model = League
        fields = [
            'name',
            'country',
            'logo',
            'external_id',
            'tier',
            'confederation',
            'is_active',
        ]
    
    def validate_name(self, value):
        """Validate league name on update"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "League name must be at least 2 characters long"
            )
        return value.strip()
    
    def validate_tier(self, value):
        """Validate league tier on update"""
        if value is None:
            return value
        
        if value < 1:
            raise serializers.ValidationError(
                "League tier must be a positive integer"
            )
        
        return value
    
    def validate_confederation(self, value):
        """Validate confederation name on update"""
        if not value:
            return value
        
        return value.strip()
    
    def validate(self, attrs):
        """
        Validate league update
        
        Rules:
        - Check for name conflicts (excluding current league)
        - Check for external_id conflicts (excluding current league)
        """
        name = attrs.get('name')
        country = attrs.get('country')
        external_id = attrs.get('external_id')
        instance = self.instance
        
        # Check for duplicate name (excluding self)
        if name and country:
            qs = League.objects.filter(name=name, country=country).exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({
                    'name': f"A league named '{name}' already exists in {country.name}"
                })
        
        # Check for duplicate external_id (excluding self)
        if external_id:
            qs = League.objects.filter(external_id=external_id).exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({
                    'external_id': f"A league with external_id '{external_id}' already exists"
                })
        
        return attrs
