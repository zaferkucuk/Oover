"""
Team Statistics Serializers for Core App

This module contains Django REST Framework serializers for the TeamStatistics model.
Provides serialization/deserialization for API endpoints with JSONB field handling.

Author: Oover Development Team
Date: November 2025
"""

from rest_framework import serializers
from apps.core.models import TeamStatistics, Team, League
import re


class TeamStatisticsListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for team statistics list views
    
    Used for:
    - GET /api/v1/team-statistics/ (list all statistics)
    - Quick reference data
    - Team performance overview
    
    Includes:
    - Basic info (id, season)
    - Nested team and league names
    - Computed properties (goals_for, goals_against, goal_difference)
    - Timestamps
    """
    
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_code = serializers.CharField(source='team.code', read_only=True, allow_null=True)
    league_name = serializers.CharField(source='league.name', read_only=True)
    
    # Computed properties from JSONB statistics field
    goals_for_total = serializers.IntegerField(source='goals_for', read_only=True)
    goals_against_total = serializers.IntegerField(source='goals_against', read_only=True)
    goal_diff = serializers.IntegerField(source='goal_difference', read_only=True)
    clean_sheets_count = serializers.IntegerField(source='clean_sheets', read_only=True)
    
    class Meta:
        model = TeamStatistics
        fields = [
            'id',
            'team',
            'team_name',
            'team_code',
            'league',
            'league_name',
            'season',
            'goals_for_total',
            'goals_against_total',
            'goal_diff',
            'clean_sheets_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeamStatisticsDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for team statistics detail views
    
    Used for:
    - GET /api/v1/team-statistics/{id}/ (retrieve single record)
    - Team performance analysis pages
    - Detailed statistics display
    
    Includes:
    - All fields including full JSONB statistics
    - Nested team and league details
    - Computed properties
    - Full timestamps
    """
    
    # Nested serializers for related objects
    team_details = serializers.SerializerMethodField()
    league_details = serializers.SerializerMethodField()
    
    # Computed properties from JSONB statistics field
    goals_for_total = serializers.IntegerField(source='goals_for', read_only=True)
    goals_against_total = serializers.IntegerField(source='goals_against', read_only=True)
    goal_diff = serializers.IntegerField(source='goal_difference', read_only=True)
    clean_sheets_count = serializers.IntegerField(source='clean_sheets', read_only=True)
    avg_possession = serializers.FloatField(source='average_possession', read_only=True)
    pass_acc = serializers.FloatField(source='pass_accuracy', read_only=True)
    
    class Meta:
        model = TeamStatistics
        fields = [
            'id',
            'team',
            'team_details',
            'league',
            'league_details',
            'season',
            'statistics',
            'goals_for_total',
            'goals_against_total',
            'goal_diff',
            'clean_sheets_count',
            'avg_possession',
            'pass_acc',
            'external_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_team_details(self, obj):
        """
        Get nested team information
        
        Returns:
            dict: Team details or None
        """
        if obj.team:
            return {
                'id': str(obj.team.id),
                'name': obj.team.name,
                'code': obj.team.code,
                'logo': obj.team.logo,
            }
        return None
    
    def get_league_details(self, obj):
        """
        Get nested league information
        
        Returns:
            dict: League details or None
        """
        if obj.league:
            return {
                'id': str(obj.league.id),
                'name': obj.league.name,
                'logo': obj.league.logo,
                'tier': obj.league.tier,
            }
        return None


class TeamStatisticsCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new team statistics records
    
    Used for:
    - POST /api/v1/team-statistics/ (create new statistics)
    
    Validation:
    - Ensures team exists
    - Ensures league exists
    - Validates season format (YYYY or YYYY-YYYY)
    - Validates statistics JSONB structure
    - Ensures no duplicate (team, league, season) combination
    - Validates external_id format (if provided)
    """
    
    class Meta:
        model = TeamStatistics
        fields = [
            'id',  # Can be provided or auto-generated
            'team',
            'league',
            'season',
            'statistics',
            'external_id',
        ]
    
    def validate_season(self, value):
        """
        Validate season format
        
        Rules:
        - Must be in format: YYYY or YYYY-YYYY
        - Years must be valid (1900-2100)
        - For YYYY-YYYY format, second year must be first year + 1
        
        Args:
            value: Season string to validate
            
        Returns:
            str: Validated season string
            
        Raises:
            ValidationError: If validation fails
        """
        if not value:
            raise serializers.ValidationError("Season is required")
        
        # Check single year format (e.g., "2025")
        if re.match(r'^\d{4}$', value):
            year = int(value)
            if year < 1900 or year > 2100:
                raise serializers.ValidationError(
                    "Season year must be between 1900 and 2100"
                )
            return value
        
        # Check year range format (e.g., "2024-2025")
        match = re.match(r'^(\d{4})-(\d{4})$', value)
        if match:
            year1 = int(match.group(1))
            year2 = int(match.group(2))
            
            if year1 < 1900 or year1 > 2100:
                raise serializers.ValidationError(
                    "First season year must be between 1900 and 2100"
                )
            
            if year2 < 1900 or year2 > 2100:
                raise serializers.ValidationError(
                    "Second season year must be between 1900 and 2100"
                )
            
            if year2 != year1 + 1:
                raise serializers.ValidationError(
                    "For YYYY-YYYY format, second year must be first year + 1"
                )
            
            return value
        
        raise serializers.ValidationError(
            "Season must be in format YYYY or YYYY-YYYY (e.g., '2025' or '2024-2025')"
        )
    
    def validate_statistics(self, value):
        """
        Validate statistics JSONB structure
        
        Rules:
        - Can be None/empty
        - If provided, must be a valid dict
        - If provided, should have expected structure (goals, shots, etc.)
        - Numeric values should be non-negative
        
        Args:
            value: Statistics dict to validate
            
        Returns:
            dict: Validated statistics dict
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            return value
        
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Statistics must be a JSON object"
            )
        
        # Optional: Validate structure if provided
        # This is a basic validation - you can make it more strict if needed
        valid_keys = {
            'goals', 'shots', 'possession', 'passes', 'corners',
            'fouls', 'cards', 'clean_sheets', 'failed_to_score', 'discipline'
        }
        
        for key in value.keys():
            if key not in valid_keys:
                # Warning: Unknown key, but not blocking
                pass
        
        # Validate numeric fields are non-negative
        if 'clean_sheets' in value:
            if not isinstance(value['clean_sheets'], int) or value['clean_sheets'] < 0:
                raise serializers.ValidationError(
                    "clean_sheets must be a non-negative integer"
                )
        
        if 'failed_to_score' in value:
            if not isinstance(value['failed_to_score'], int) or value['failed_to_score'] < 0:
                raise serializers.ValidationError(
                    "failed_to_score must be a non-negative integer"
                )
        
        return value
    
    def validate(self, attrs):
        """
        Validate entire team statistics object
        
        Rules:
        - Check for duplicate (team, league, season) combination
        - Check for duplicate external_id if provided
        - Ensure team and league exist
        
        Args:
            attrs: Dictionary of all attributes
            
        Returns:
            dict: Validated attributes
            
        Raises:
            ValidationError: If validation fails
        """
        team = attrs.get('team')
        league = attrs.get('league')
        season = attrs.get('season')
        external_id = attrs.get('external_id')
        
        # Check for duplicate (team, league, season)
        qs = TeamStatistics.objects.filter(
            team=team,
            league=league,
            season=season
        )
        
        if qs.exists():
            raise serializers.ValidationError({
                'non_field_errors': [
                    f"Statistics for {team.name} in {league.name} for season {season} already exist"
                ]
            })
        
        # Check for duplicate external_id
        if external_id:
            if TeamStatistics.objects.filter(external_id=external_id).exists():
                raise serializers.ValidationError({
                    'external_id': f"Statistics with external_id '{external_id}' already exist"
                })
        
        return attrs


class TeamStatisticsUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing team statistics
    
    Used for:
    - PUT /api/v1/team-statistics/{id}/ (full update)
    - PATCH /api/v1/team-statistics/{id}/ (partial update)
    
    Allows updating:
    - statistics (JSONB field)
    - external_id
    - Season can be changed (with validation)
    
    Does NOT allow updating:
    - id (immutable)
    - team, league (should not change - create new record instead)
    - created_at, updated_at (auto-managed)
    """
    
    class Meta:
        model = TeamStatistics
        fields = [
            'season',
            'statistics',
            'external_id',
        ]
    
    def validate_season(self, value):
        """Validate season format on update"""
        if not value:
            raise serializers.ValidationError("Season is required")
        
        # Check single year format (e.g., "2025")
        if re.match(r'^\d{4}$', value):
            year = int(value)
            if year < 1900 or year > 2100:
                raise serializers.ValidationError(
                    "Season year must be between 1900 and 2100"
                )
            return value
        
        # Check year range format (e.g., "2024-2025")
        match = re.match(r'^(\d{4})-(\d{4})$', value)
        if match:
            year1 = int(match.group(1))
            year2 = int(match.group(2))
            
            if year1 < 1900 or year1 > 2100:
                raise serializers.ValidationError(
                    "First season year must be between 1900 and 2100"
                )
            
            if year2 < 1900 or year2 > 2100:
                raise serializers.ValidationError(
                    "Second season year must be between 1900 and 2100"
                )
            
            if year2 != year1 + 1:
                raise serializers.ValidationError(
                    "For YYYY-YYYY format, second year must be first year + 1"
                )
            
            return value
        
        raise serializers.ValidationError(
            "Season must be in format YYYY or YYYY-YYYY (e.g., '2025' or '2024-2025')"
        )
    
    def validate_statistics(self, value):
        """Validate statistics JSONB structure on update"""
        if value is None:
            return value
        
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Statistics must be a JSON object"
            )
        
        # Validate numeric fields are non-negative
        if 'clean_sheets' in value:
            if not isinstance(value['clean_sheets'], int) or value['clean_sheets'] < 0:
                raise serializers.ValidationError(
                    "clean_sheets must be a non-negative integer"
                )
        
        if 'failed_to_score' in value:
            if not isinstance(value['failed_to_score'], int) or value['failed_to_score'] < 0:
                raise serializers.ValidationError(
                    "failed_to_score must be a non-negative integer"
                )
        
        return value
    
    def validate(self, attrs):
        """
        Validate team statistics update
        
        Rules:
        - If season is changed, check for conflicts
        - Check for external_id conflicts (excluding current record)
        """
        instance = self.instance
        season = attrs.get('season', instance.season)
        external_id = attrs.get('external_id')
        
        # Check for duplicate (team, league, season) if season changed
        if season != instance.season:
            qs = TeamStatistics.objects.filter(
                team=instance.team,
                league=instance.league,
                season=season
            ).exclude(id=instance.id)
            
            if qs.exists():
                raise serializers.ValidationError({
                    'season': f"Statistics for this team in this league for season {season} already exist"
                })
        
        # Check for duplicate external_id (excluding self)
        if external_id:
            qs = TeamStatistics.objects.filter(external_id=external_id).exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({
                    'external_id': f"Statistics with external_id '{external_id}' already exist"
                })
        
        return attrs
