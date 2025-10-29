"""
Team Serializers for Core App

This module contains Django REST Framework serializers for the Team model.
Provides serialization/deserialization for API endpoints.

Author: Oover Development Team
Date: October 2025
"""

from rest_framework import serializers
from apps.core.models import Team, Country


class TeamListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for team list views
    
    Used for:
    - GET /api/v1/teams/ (list all teams)
    - Dropdown selections
    - Quick reference data
    
    Includes:
    - Basic team info (id, code, name, logo)
    - Nested country name (for display)
    - Status flags (is_active)
    - Market value (formatted)
    """
    
    country_name = serializers.CharField(source='country.name', read_only=True, allow_null=True)
    country_code = serializers.CharField(source='country.code', read_only=True, allow_null=True)
    market_value_formatted = serializers.CharField(source='formatted_market_value', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id',
            'code',
            'name',
            'country_name',
            'country_code',
            'logo',
            'market_value',
            'market_value_formatted',
            'is_active',
        ]
        read_only_fields = ['id']


class TeamDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for team detail views
    
    Used for:
    - GET /api/v1/teams/{id}/ (retrieve single team)
    - Team profile pages
    - Detailed analytics
    
    Includes:
    - All team fields
    - Nested country details (full object)
    - Formatted market value
    - Timestamps
    """
    
    # Nested serializers for related objects
    country_details = serializers.SerializerMethodField()
    market_value_formatted = serializers.CharField(source='formatted_market_value', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id',
            'code',
            'name',
            'country',
            'country_details',
            'logo',
            'founded',
            'website',
            'market_value',
            'market_value_formatted',
            'external_id',
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


class TeamCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new teams
    
    Used for:
    - POST /api/v1/teams/ (create new team)
    
    Validation:
    - Ensures team name is unique
    - Ensures code is unique (if provided)
    - Validates country_id exists (if provided)
    - Validates external_id format
    - Validates website URL format (if provided)
    - Validates market_value range (if provided)
    """
    
    class Meta:
        model = Team
        fields = [
            'id',  # Can be provided or auto-generated
            'code',
            'name',
            'country',
            'logo',
            'founded',
            'website',
            'market_value',
            'external_id',
            'is_active',
        ]
    
    def validate_name(self, value):
        """
        Validate team name
        
        Rules:
        - Must not be empty
        - Must be at least 2 characters
        - Should be unique
        
        Args:
            value: Team name to validate
            
        Returns:
            str: Validated team name
            
        Raises:
            ValidationError: If validation fails
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Team name must be at least 2 characters long"
            )
        
        # Check for duplicate name
        if Team.objects.filter(name=value.strip()).exists():
            raise serializers.ValidationError(
                f"A team named '{value.strip()}' already exists"
            )
        
        return value.strip()
    
    def validate_code(self, value):
        """
        Validate team code
        
        Rules:
        - If provided, must be 2-10 characters
        - Should be uppercase letters/numbers only
        - Must be unique
        
        Args:
            value: Team code to validate
            
        Returns:
            str: Validated team code (uppercase)
            
        Raises:
            ValidationError: If validation fails
        """
        if not value:
            return value
        
        code = value.strip().upper()
        
        if len(code) < 2 or len(code) > 10:
            raise serializers.ValidationError(
                "Team code must be between 2-10 characters"
            )
        
        # Check for duplicate code
        if Team.objects.filter(code=code).exists():
            raise serializers.ValidationError(
                f"Team code '{code}' is already in use"
            )
        
        return code
    
    def validate_founded(self, value):
        """
        Validate foundation year
        
        Rules:
        - Must be between 1800 and current year + 1
        
        Args:
            value: Foundation year
            
        Returns:
            int: Validated year
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            return value
        
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 1800 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Foundation year must be between 1800 and {current_year + 1}"
            )
        
        return value
    
    def validate_market_value(self, value):
        """
        Validate market value
        
        Rules:
        - If provided, must be positive
        - Maximum value: 10 billion EUR
        
        Args:
            value: Market value in EUR
            
        Returns:
            int: Validated market value
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            return value
        
        if value < 0:
            raise serializers.ValidationError(
                "Market value cannot be negative"
            )
        
        if value > 10_000_000_000:  # 10 billion EUR
            raise serializers.ValidationError(
                "Market value cannot exceed €10 billion"
            )
        
        return value
    
    def validate_website(self, value):
        """
        Validate website URL
        
        Rules:
        - If provided, must be valid URL format
        - Must start with http:// or https://
        
        Args:
            value: Website URL
            
        Returns:
            str: Validated URL
            
        Raises:
            ValidationError: If validation fails
        """
        if not value:
            return value
        
        url = value.strip()
        
        if not (url.startswith('http://') or url.startswith('https://')):
            raise serializers.ValidationError(
                "Website URL must start with http:// or https://"
            )
        
        return url
    
    def validate(self, attrs):
        """
        Validate entire team object
        
        Rules:
        - Check for duplicate external_id if provided
        
        Args:
            attrs: Dictionary of all team attributes
            
        Returns:
            dict: Validated attributes
            
        Raises:
            ValidationError: If validation fails
        """
        external_id = attrs.get('external_id')
        
        # Check for duplicate external_id
        if external_id:
            if Team.objects.filter(external_id=external_id).exists():
                raise serializers.ValidationError({
                    'external_id': f"A team with external_id '{external_id}' already exists"
                })
        
        return attrs


class TeamUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing teams
    
    Used for:
    - PUT /api/v1/teams/{id}/ (full update)
    - PATCH /api/v1/teams/{id}/ (partial update)
    
    Allows updating:
    - code, name, logo, founded, website, market_value
    - country (can be changed)
    - external_id
    - is_active status
    
    Does NOT allow updating:
    - id (immutable)
    - created_at, updated_at (auto-managed)
    """
    
    class Meta:
        model = Team
        fields = [
            'code',
            'name',
            'country',
            'logo',
            'founded',
            'website',
            'market_value',
            'external_id',
            'is_active',
        ]
    
    def validate_name(self, value):
        """Validate team name on update"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Team name must be at least 2 characters long"
            )
        
        # Check for duplicate name (excluding current team)
        instance = self.instance
        if Team.objects.filter(name=value.strip()).exclude(id=instance.id).exists():
            raise serializers.ValidationError(
                f"A team named '{value.strip()}' already exists"
            )
        
        return value.strip()
    
    def validate_code(self, value):
        """Validate team code on update"""
        if not value:
            return value
        
        code = value.strip().upper()
        
        if len(code) < 2 or len(code) > 10:
            raise serializers.ValidationError(
                "Team code must be between 2-10 characters"
            )
        
        # Check for duplicate code (excluding current team)
        instance = self.instance
        if Team.objects.filter(code=code).exclude(id=instance.id).exists():
            raise serializers.ValidationError(
                f"Team code '{code}' is already in use"
            )
        
        return code
    
    def validate_founded(self, value):
        """Validate foundation year on update"""
        if value is None:
            return value
        
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 1800 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Foundation year must be between 1800 and {current_year + 1}"
            )
        
        return value
    
    def validate_market_value(self, value):
        """Validate market value on update"""
        if value is None:
            return value
        
        if value < 0:
            raise serializers.ValidationError(
                "Market value cannot be negative"
            )
        
        if value > 10_000_000_000:
            raise serializers.ValidationError(
                "Market value cannot exceed €10 billion"
            )
        
        return value
    
    def validate_website(self, value):
        """Validate website URL on update"""
        if not value:
            return value
        
        url = value.strip()
        
        if not (url.startswith('http://') or url.startswith('https://')):
            raise serializers.ValidationError(
                "Website URL must start with http:// or https://"
            )
        
        return url
    
    def validate(self, attrs):
        """
        Validate team update
        
        Rules:
        - Check for external_id conflicts (excluding current team)
        """
        external_id = attrs.get('external_id')
        instance = self.instance
        
        # Check for duplicate external_id (excluding self)
        if external_id:
            qs = Team.objects.filter(external_id=external_id).exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({
                    'external_id': f"A team with external_id '{external_id}' already exists"
                })
        
        return attrs
