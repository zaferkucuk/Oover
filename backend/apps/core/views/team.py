"""
Team ViewSet for Core App

This module contains Django REST Framework ViewSets for the Team model.
Provides CRUD operations and filtering/searching capabilities.
Also includes API endpoints for external data operations (fetch, sync).

Author: Oover Development Team
Date: October 2025
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging

from apps.core.models import Team
from apps.core.serializers import (
    TeamListSerializer,
    TeamDetailSerializer,
    TeamCreateSerializer,
    TeamUpdateSerializer,
)
from api_integrations.services.teams_service import TeamsService

logger = logging.getLogger(__name__)


class TeamPagination(PageNumberPagination):
    """
    Custom pagination for team list views
    
    Settings:
    - page_size: 30 teams per page (default)
    - page_size_query_param: 'page_size' (client can override)
    - max_page_size: 100 (maximum allowed)
    """
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        summary="List all teams",
        description="Get a paginated list of all teams with optional filtering and search",
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search teams by name or code',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='country',
                description='Filter by country ID (UUID)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='is_active',
                description='Filter by active status (true/false)',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='market_value_min',
                description='Filter by minimum market value (EUR)',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='market_value_max',
                description='Filter by maximum market value (EUR)',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='ordering',
                description='Order by field (name, market_value, founded, -name for descending)',
                required=False,
                type=str
            ),
        ],
        tags=['Teams']
    ),
    retrieve=extend_schema(
        summary="Get team details",
        description="Retrieve detailed information for a specific team",
        tags=['Teams']
    ),
    create=extend_schema(
        summary="Create new team",
        description="Create a new team with validation",
        tags=['Teams']
    ),
    update=extend_schema(
        summary="Update team",
        description="Full update of an existing team",
        tags=['Teams']
    ),
    partial_update=extend_schema(
        summary="Partially update team",
        description="Partial update of an existing team (PATCH)",
        tags=['Teams']
    ),
    destroy=extend_schema(
        summary="Delete team",
        description="Delete an existing team",
        tags=['Teams']
    ),
)
class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Team CRUD operations
    
    Provides:
    - list: GET /api/v1/teams/ (paginated, searchable, filterable)
    - retrieve: GET /api/v1/teams/{id}/
    - create: POST /api/v1/teams/
    - update: PUT /api/v1/teams/{id}/
    - partial_update: PATCH /api/v1/teams/{id}/
    - destroy: DELETE /api/v1/teams/{id}/
    
    Custom Actions:
    - by_country: GET /api/v1/teams/by-country/{country_id}/
    - active: GET /api/v1/teams/active/
    - top_by_market_value: GET /api/v1/teams/top-by-market-value/?limit=10
    - fetch: POST /api/v1/teams/fetch/ (fetch teams from external API)
    
    Filtering:
    - ?search=manchester (search by name or code)
    - ?country=<uuid> (filter by country)
    - ?is_active=true (filter by status)
    - ?market_value_min=1000000 (minimum market value)
    - ?market_value_max=1000000000 (maximum market value)
    
    Ordering:
    - ?ordering=name (ascending by name)
    - ?ordering=-market_value (descending by market value)
    - ?ordering=-founded (descending by foundation year)
    """
    
    queryset = Team.objects.select_related('country').all()
    pagination_class = TeamPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering fields
    filterset_fields = ['country', 'is_active']
    
    # Search fields
    search_fields = ['name', 'code', 'external_id']
    
    # Ordering fields
    ordering_fields = ['name', 'code', 'market_value', 'founded', 'created_at', 'updated_at']
    ordering = ['name']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        
        - list → TeamListSerializer (lightweight)
        - retrieve → TeamDetailSerializer (comprehensive)
        - create → TeamCreateSerializer (validation)
        - update/partial_update → TeamUpdateSerializer (validation)
        
        Returns:
            Serializer class for current action
        """
        if self.action == 'list':
            return TeamListSerializer
        elif self.action == 'retrieve':
            return TeamDetailSerializer
        elif self.action == 'create':
            return TeamCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeamUpdateSerializer
        return TeamDetailSerializer
    
    def get_queryset(self):
        """
        Get queryset with optimized database queries and custom filters
        
        Always includes:
        - select_related('country') for foreign key optimization
        
        Custom filters:
        - market_value_min: Filter teams with market value >= value
        - market_value_max: Filter teams with market value <= value
        
        Returns:
            Optimized and filtered queryset
        """
        queryset = super().get_queryset()
        
        # Market value range filtering
        market_value_min = self.request.query_params.get('market_value_min', None)
        market_value_max = self.request.query_params.get('market_value_max', None)
        
        if market_value_min:
            try:
                min_value = int(market_value_min)
                queryset = queryset.filter(market_value__gte=min_value)
            except ValueError:
                pass  # Invalid value, ignore filter
        
        if market_value_max:
            try:
                max_value = int(market_value_max)
                queryset = queryset.filter(market_value__lte=max_value)
            except ValueError:
                pass  # Invalid value, ignore filter
        
        return queryset
    
    @extend_schema(
        summary="Get teams by country",
        description="Retrieve all teams for a specific country",
        parameters=[
            OpenApiParameter(
                name='country_id',
                location=OpenApiParameter.PATH,
                description='Country UUID',
                required=True,
                type=str
            ),
        ],
        tags=['Teams']
    )
    @action(detail=False, methods=['get'], url_path='by-country/(?P<country_id>[^/.]+)')
    def by_country(self, request, country_id=None):
        """
        Get all teams for a specific country
        
        URL: GET /api/v1/teams/by-country/{country_id}/
        
        Args:
            country_id: Country UUID
            
        Returns:
            List of teams for the specified country
        """
        teams = self.queryset.filter(country_id=country_id, is_active=True)
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get active teams",
        description="Retrieve all active teams (is_active=True)",
        tags=['Teams']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active teams
        
        URL: GET /api/v1/teams/active/
        
        Returns:
            List of all active teams
        """
        teams = self.queryset.filter(is_active=True)
        
        # Apply pagination
        page = self.paginate_queryset(teams)
        if page is not None:
            serializer = TeamListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get top teams by market value",
        description="Retrieve top teams ordered by market value (highest first)",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Number of teams to return (default: 10, max: 50)',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='country',
                description='Filter by country ID (UUID)',
                required=False,
                type=str
            ),
        ],
        tags=['Teams']
    )
    @action(detail=False, methods=['get'], url_path='top-by-market-value')
    def top_by_market_value(self, request):
        """
        Get top teams by market value
        
        URL: GET /api/v1/teams/top-by-market-value/?limit=10&country=<uuid>
        
        Query Parameters:
        - limit: Number of teams to return (default: 10, max: 50)
        - country: Country UUID (optional filter)
        
        Returns:
            List of top teams ordered by market value
        """
        limit = request.query_params.get('limit', '10')
        country_id = request.query_params.get('country', None)
        
        try:
            limit = min(int(limit), 50)  # Maximum 50 teams
        except ValueError:
            limit = 10
        
        # Build query
        teams = self.queryset.filter(is_active=True, market_value__isnull=False)
        
        # Apply country filter if provided
        if country_id:
            teams = teams.filter(country_id=country_id)
        
        # Order by market value (descending) and limit
        teams = teams.order_by('-market_value')[:limit]
        
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Search teams",
        description="Advanced search with multiple criteria",
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query (searches name, code, and external_id)',
                required=True,
                type=str
            ),
            OpenApiParameter(
                name='country',
                description='Filter by country ID',
                required=False,
                type=str
            ),
        ],
        tags=['Teams']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search endpoint
        
        URL: GET /api/v1/teams/search/?q=united&country=<uuid>
        
        Query Parameters:
        - q: Search query (required)
        - country: Country UUID (optional)
        
        Returns:
            List of matching teams
        """
        query = request.query_params.get('q', '')
        country_id = request.query_params.get('country', None)
        
        if not query:
            return Response(
                {'error': 'Search query (q) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build search query
        teams = self.queryset.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) | 
            Q(external_id__icontains=query)
        )
        
        # Apply country filter if provided
        if country_id:
            teams = teams.filter(country_id=country_id)
        
        # Apply pagination
        page = self.paginate_queryset(teams)
        if page is not None:
            serializer = TeamListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Fetch teams from external API",
        description="""
        Fetch teams from external APIs (Football-Data.org or API-Football).
        
        This endpoint performs a one-time fetch operation to retrieve teams from external sources.
        Use this for initial data population or when you need to fetch teams for new leagues.
        
        **Providers:**
        - `football-data`: Football-Data.org API (10 requests/minute)
        - `api-football`: API-Football (100 requests/day)
        
        **Filter Options (mutually exclusive):**
        - `leagues`: Array of league codes (e.g., ["PL", "SA"])
        - `country`: Country code (e.g., "GB")
        - `all_european`: Fetch top 5 European leagues (PL, PD, SA, BL1, FL1)
        
        If no filter is provided, defaults to `all_european=true`.
        
        **Rate Limiting:**
        - Football-Data.org: 10 requests per minute
        - API-Football: 100 requests per day
        
        **Note:** This is a long-running operation. The response will include statistics
        about the fetch operation, but the actual data fetching happens asynchronously.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'provider': {
                        'type': 'string',
                        'enum': ['football-data', 'api-football'],
                        'description': 'API provider to use',
                        'default': 'football-data'
                    },
                    'leagues': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'League codes to fetch (mutually exclusive with country and all_european)',
                        'example': ['PL', 'SA']
                    },
                    'country': {
                        'type': 'string',
                        'description': 'Country code to fetch teams for (mutually exclusive with leagues and all_european)',
                        'example': 'GB'
                    },
                    'all_european': {
                        'type': 'boolean',
                        'description': 'Fetch top 5 European leagues (mutually exclusive with leagues and country)',
                        'default': True
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Limit number of teams for testing (optional)',
                        'example': 10
                    }
                }
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'stats': {
                        'type': 'object',
                        'properties': {
                            'fetched': {'type': 'integer'},
                            'created': {'type': 'integer'},
                            'updated': {'type': 'integer'},
                            'failed': {'type': 'integer'}
                        }
                    },
                    'provider': {'type': 'string'},
                    'filters': {'type': 'object'}
                },
                'example': {
                    'success': True,
                    'message': 'Successfully fetched teams from football-data',
                    'stats': {
                        'fetched': 100,
                        'created': 95,
                        'updated': 5,
                        'failed': 0
                    },
                    'provider': 'football-data',
                    'filters': {'leagues': ['PL', 'PD', 'SA', 'BL1', 'FL1']}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'}
                },
                'example': {
                    'success': False,
                    'error': 'Only one of leagues, country, or all_european can be specified'
                }
            },
            500: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'}
                },
                'example': {
                    'success': False,
                    'error': 'Fetch operation failed: Connection timeout'
                }
            }
        },
        tags=['Teams - External API']
    )
    @action(detail=False, methods=['post'])
    def fetch(self, request):
        """
        Fetch teams from external APIs
        
        URL: POST /api/v1/teams/fetch/
        
        Request Body:
            {
                "provider": "football-data",  // or "api-football"
                "leagues": ["PL", "SA"],      // Optional, mutually exclusive with country/all_european
                "country": "GB",              // Optional, mutually exclusive with leagues/all_european
                "all_european": true,         // Optional, mutually exclusive with leagues/country
                "limit": 10                   // Optional, for testing
            }
        
        Returns:
            200 OK: Operation statistics
            400 Bad Request: Invalid parameters
            500 Internal Server Error: Fetch operation failed
        """
        try:
            # Extract and validate parameters
            provider = request.data.get('provider', 'football-data')
            leagues = request.data.get('leagues')
            country = request.data.get('country')
            all_european = request.data.get('all_european', False)
            limit = request.data.get('limit')
            
            # Validate provider
            if provider not in ['football-data', 'api-football']:
                return Response(
                    {
                        'success': False,
                        'error': 'Invalid provider. Must be "football-data" or "api-football"'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate mutually exclusive filters
            filter_count = sum([
                bool(leagues),
                bool(country),
                bool(all_european)
            ])
            
            if filter_count > 1:
                return Response(
                    {
                        'success': False,
                        'error': 'Only one of leagues, country, or all_european can be specified'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Build filters dictionary
            filters = {}
            
            if all_european:
                filters['leagues'] = ['PL', 'PD', 'SA', 'BL1', 'FL1']
            elif leagues:
                filters['leagues'] = leagues
            elif country:
                filters['country'] = country
            else:
                # Default to all European leagues
                filters['leagues'] = ['PL', 'PD', 'SA', 'BL1', 'FL1']
            
            if limit:
                filters['limit'] = int(limit)
            
            # Initialize teams service
            teams_service = TeamsService(provider=provider)
            
            # Execute fetch operation
            logger.info(f"Starting fetch_teams operation via API - Provider: {provider}, Filters: {filters}")
            stats = teams_service.fetch_teams(filters=filters)
            
            # Return success response
            return Response(
                {
                    'success': True,
                    'message': f'Successfully fetched teams from {provider}',
                    'stats': stats,
                    'provider': provider,
                    'filters': filters
                },
                status=status.HTTP_200_OK
            )
            
        except ValueError as e:
            logger.error(f"Validation error in fetch_teams API: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in fetch_teams API: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'error': f'Fetch operation failed: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new team
        
        URL: POST /api/v1/teams/
        
        Request Body:
            {
                "id": "unique-text-id",  // Optional, auto-generated if not provided
                "code": "MUN",
                "name": "Manchester United",
                "country": "<country_uuid>",
                "logo": "https://...",
                "founded": 1878,
                "website": "https://www.manutd.com",
                "market_value": 1000000000,
                "external_id": "api-football-33",
                "is_active": true
            }
        
        Returns:
            201 Created: Newly created team
            400 Bad Request: Validation errors
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detailed response
        headers = self.get_success_headers(serializer.data)
        team = Team.objects.select_related('country').get(id=serializer.data['id'])
        response_serializer = TeamDetailSerializer(team)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def perform_create(self, serializer):
        """Save new team instance"""
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing team (full update)
        
        URL: PUT /api/v1/teams/{id}/
        
        All fields required in request body.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return detailed response
        team = Team.objects.select_related('country').get(id=instance.id)
        response_serializer = TeamDetailSerializer(team)
        return Response(response_serializer.data)
    
    def perform_update(self, serializer):
        """Save updated team instance"""
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a team
        
        URL: DELETE /api/v1/teams/{id}/
        
        Returns:
            204 No Content: Successfully deleted
            404 Not Found: Team doesn't exist
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        """Delete team instance"""
        instance.delete()
