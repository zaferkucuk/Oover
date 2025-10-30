"""
Core Serializers Package

This package contains all serializers for the core app models.
"""

from .country import (
    CountrySerializer,
    CountryCreateSerializer,
    CountryUpdateSerializer,
    CountryWithRelationsSerializer,
    CountryFilterSerializer,
    CountryListResponseSerializer,
    CountryResponseSerializer,
    CountryOperationResultSerializer,
)

from .league import (
    LeagueListSerializer,
    LeagueDetailSerializer,
    LeagueCreateSerializer,
    LeagueUpdateSerializer,
)

from .team import (
    TeamListSerializer,
    TeamDetailSerializer,
    TeamCreateSerializer,
    TeamUpdateSerializer,
)

from .api_sync import (
    APISyncListSerializer,
    APISyncDetailSerializer,
)

__all__ = [
    # Country Serializers
    'CountrySerializer',
    'CountryCreateSerializer',
    'CountryUpdateSerializer',
    'CountryWithRelationsSerializer',
    'CountryFilterSerializer',
    'CountryListResponseSerializer',
    'CountryResponseSerializer',
    'CountryOperationResultSerializer',
    
    # League Serializers
    'LeagueListSerializer',
    'LeagueDetailSerializer',
    'LeagueCreateSerializer',
    'LeagueUpdateSerializer',
    
    # Team Serializers
    'TeamListSerializer',
    'TeamDetailSerializer',
    'TeamCreateSerializer',
    'TeamUpdateSerializer',
    
    # API Sync Serializers
    'APISyncListSerializer',
    'APISyncDetailSerializer',
]
