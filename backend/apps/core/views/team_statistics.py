"""
Team Statistics Views for Django REST Framework

This module provides ViewSets for TeamStatistics model, enabling
full CRUD operations and analytics via REST API endpoints.

Author: Oover Development Team
Date: November 2025
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.core.models import TeamStatistics
from apps.core.serializers.team_statistics import (
    TeamStatisticsListSerializer,
    TeamStatisticsDetailSerializer,
    TeamStatisticsCreateSerializer,
    TeamStatisticsUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all team statistics",
        description="Retrieve a paginated list of team statistics with optional filtering",
        parameters=[
            OpenApiParameter(
                name='team',
                type=str,
                description='Filter by team UUID'
            ),
            OpenApiParameter(
                name='league',
                type=str,
                description='Filter by league UUID'
            ),
            OpenApiParameter(
                name='season',
                type=str,
                description='Filter by season (e.g., 2024-2025)'
            ),
            OpenApiParameter(
                name='search',
                type=str,
                description='Search in team name or league name'
            ),
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by: season, matches_played, created_at, updated_at (prefix with - for descending)'
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Get team statistics details",
        description="Retrieve detailed team statistics with full JSONB data"
    ),
    create=extend_schema(
        summary="Create team statistics",
        description="Create a new team statistics record"
    ),
    update=extend_schema(
        summary="Update team statistics",
        description="Update all fields of team statistics"
    ),
    partial_update=extend_schema(
        summary="Partially update team statistics",
        description="Update specific fields of team statistics"
    ),
    destroy=extend_schema(
        summary="Delete team statistics",
        description="Delete team statistics record"
    ),
)
class TeamStatisticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TeamStatistics model providing full CRUD operations.
    
    Endpoints:
    - GET    /api/team-statistics/              - List all team statistics (paginated)
    - POST   /api/team-statistics/              - Create new team statistics
    - GET    /api/team-statistics/{id}/         - Get team statistics details
    - PUT    /api/team-statistics/{id}/         - Update team statistics (all fields)
    - PATCH  /api/team-statistics/{id}/         - Partial update team statistics
    - DELETE /api/team-statistics/{id}/         - Delete team statistics
    - GET    /api/team-statistics/by_team/      - Get statistics by team
    - GET    /api/team-statistics/by_league/    - Get statistics by league
    - GET    /api/team-statistics/by_season/    - Get statistics by season
    - GET    /api/team-statistics/stats/        - Get aggregate statistics
    """
    
    queryset = TeamStatistics.objects.select_related('team', 'league').all()
    serializer_class = TeamStatisticsListSerializer
    lookup_field = 'id'
    
    # Filtering and search
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    # DjangoFilterBackend settings
    filterset_fields = {
        'team': ['exact'],
        'league': ['exact'],
        'season': ['exact', 'icontains'],
        'matches_played': ['exact', 'gte', 'lte'],
    }
    
    # SearchFilter settings - search in team name and league name
    search_fields = ['team__name', 'league__name', 'season']
    
    # OrderingFilter settings
    ordering_fields = ['season', 'matches_played', 'created_at', 'updated_at']
    ordering = ['-season', '-updated_at']  # Default ordering: newest season first
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        - list: TeamStatisticsListSerializer (lightweight list view)
        - retrieve: TeamStatisticsDetailSerializer (full details with JSONB)
        - create: TeamStatisticsCreateSerializer (validation for new records)
        - update/partial_update: TeamStatisticsUpdateSerializer (validation for updates)
        """
        if self.action == 'create':
            return TeamStatisticsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeamStatisticsUpdateSerializer
        elif self.action == 'retrieve':
            return TeamStatisticsDetailSerializer
        return TeamStatisticsListSerializer
    
    def get_queryset(self):
        """
        Optionally restricts the returned statistics based on query parameters.
        
        Query parameters:
        - team: UUID (filter by specific team)
        - league: UUID (filter by specific league)
        - season: string (filter by season)
        """
        queryset = TeamStatistics.objects.select_related('team', 'league').all()
        
        # Additional filtering via query params
        team_id = self.request.query_params.get('team', None)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        
        league_id = self.request.query_params.get('league', None)
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        season = self.request.query_params.get('season', None)
        if season:
            queryset = queryset.filter(season=season)
        
        return queryset
    
    @extend_schema(
        summary="Get statistics by team",
        description="Retrieve all statistics for a specific team across seasons",
        parameters=[
            OpenApiParameter(
                name='team_id',
                type=str,
                required=True,
                description='Team UUID'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def by_team(self, request):
        """
        Get all statistics for a specific team.
        
        GET /api/team-statistics/by_team/?team_id={uuid}
        """
        team_id = request.query_params.get('team_id')
        if not team_id:
            return Response(
                {'error': 'team_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        statistics = self.get_queryset().filter(team_id=team_id).order_by('-season')
        
        # Apply pagination
        page = self.paginate_queryset(statistics)
        if page is not None:
            serializer = TeamStatisticsDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeamStatisticsDetailSerializer(statistics, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': statistics.count()
        })
    
    @extend_schema(
        summary="Get statistics by league",
        description="Retrieve all team statistics for a specific league and season",
        parameters=[
            OpenApiParameter(
                name='league_id',
                type=str,
                required=True,
                description='League UUID'
            ),
            OpenApiParameter(
                name='season',
                type=str,
                required=False,
                description='Season filter (optional)'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def by_league(self, request):
        """
        Get all team statistics for a specific league.
        
        GET /api/team-statistics/by_league/?league_id={uuid}&season=2024-2025
        """
        league_id = request.query_params.get('league_id')
        if not league_id:
            return Response(
                {'error': 'league_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        statistics = self.get_queryset().filter(league_id=league_id)
        
        # Optional season filter
        season = request.query_params.get('season')
        if season:
            statistics = statistics.filter(season=season)
        
        statistics = statistics.order_by('-season', 'team__name')
        
        # Apply pagination
        page = self.paginate_queryset(statistics)
        if page is not None:
            serializer = TeamStatisticsListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeamStatisticsListSerializer(statistics, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': statistics.count()
        })
    
    @extend_schema(
        summary="Get statistics by season",
        description="Retrieve all team statistics for a specific season across leagues",
        parameters=[
            OpenApiParameter(
                name='season',
                type=str,
                required=True,
                description='Season (e.g., 2024-2025)'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def by_season(self, request):
        """
        Get all team statistics for a specific season.
        
        GET /api/team-statistics/by_season/?season=2024-2025
        """
        season = request.query_params.get('season')
        if not season:
            return Response(
                {'error': 'season parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        statistics = self.get_queryset().filter(season=season).order_by(
            'league__name', 'team__name'
        )
        
        # Apply pagination
        page = self.paginate_queryset(statistics)
        if page is not None:
            serializer = TeamStatisticsListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeamStatisticsListSerializer(statistics, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': statistics.count()
        })
    
    @extend_schema(
        summary="Get aggregate statistics",
        description="Get summary statistics about team statistics records"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get aggregate statistics.
        
        GET /api/team-statistics/stats/
        
        Returns:
        - total_records: Total number of team statistics records
        - unique_teams: Number of unique teams with statistics
        - unique_leagues: Number of unique leagues
        - unique_seasons: Number of unique seasons
        - latest_season: Most recent season with data
        """
        queryset = self.get_queryset()
        
        # Get unique values
        unique_teams = queryset.values('team').distinct().count()
        unique_leagues = queryset.values('league').distinct().count()
        seasons = queryset.values_list('season', flat=True).distinct().order_by('-season')
        
        stats = {
            'total_records': queryset.count(),
            'unique_teams': unique_teams,
            'unique_leagues': unique_leagues,
            'unique_seasons': len(seasons),
            'latest_season': seasons[0] if seasons else None,
            'seasons': list(seasons)
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        """
        List team statistics with pagination and filtering.
        
        Override to add custom response structure.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': queryset.count()
        })
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve single team statistics record.
        
        Override to add custom response structure.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """
        Create new team statistics record.
        
        Override to add custom response structure.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'success': True,
            'message': 'Team statistics created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update team statistics record.
        
        Override to add custom response structure.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Team statistics updated successfully',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete team statistics record.
        
        Override to add custom response structure.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response({
            'success': True,
            'message': 'Team statistics deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
