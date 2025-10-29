"""
League ViewSet for Core App

This module contains Django REST Framework ViewSets for the League model.
Provides CRUD operations and filtering/searching capabilities.

Author: Oover Development Team
Date: October 2025
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.core.models import League
from apps.core.serializers import (
    LeagueListSerializer,
    LeagueDetailSerializer,
    LeagueCreateSerializer,
    LeagueUpdateSerializer,
)


class LeaguePagination(PageNumberPagination):
    """
    Custom pagination for league list views
    
    Settings:
    - page_size: 20 leagues per page (default)
    - page_size_query_param: 'page_size' (client can override)
    - max_page_size: 100 (maximum allowed)
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        summary="List all leagues",
        description="Get a paginated list of all leagues with optional filtering and search",
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search leagues by name',
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
                name='sport',
                description='Filter by sport ID',
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
                name='ordering',
                description='Order by field (name, created_at, -name for descending)',
                required=False,
                type=str
            ),
        ],
        tags=['Leagues']
    ),
    retrieve=extend_schema(
        summary="Get league details",
        description="Retrieve detailed information for a specific league",
        tags=['Leagues']
    ),
    create=extend_schema(
        summary="Create new league",
        description="Create a new league with validation",
        tags=['Leagues']
    ),
    update=extend_schema(
        summary="Update league",
        description="Full update of an existing league",
        tags=['Leagues']
    ),
    partial_update=extend_schema(
        summary="Partially update league",
        description="Partial update of an existing league (PATCH)",
        tags=['Leagues']
    ),
    destroy=extend_schema(
        summary="Delete league",
        description="Delete an existing league",
        tags=['Leagues']
    ),
)
class LeagueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for League CRUD operations
    
    Provides:
    - list: GET /api/v1/leagues/ (paginated, searchable, filterable)
    - retrieve: GET /api/v1/leagues/{id}/
    - create: POST /api/v1/leagues/
    - update: PUT /api/v1/leagues/{id}/
    - partial_update: PATCH /api/v1/leagues/{id}/
    - destroy: DELETE /api/v1/leagues/{id}/
    
    Custom Actions:
    - by_country: GET /api/v1/leagues/by_country/{country_id}/
    - active: GET /api/v1/leagues/active/
    
    Filtering:
    - ?search=premier (search by name)
    - ?country=<uuid> (filter by country)
    - ?sport=<id> (filter by sport)
    - ?is_active=true (filter by status)
    
    Ordering:
    - ?ordering=name (ascending by name)
    - ?ordering=-created_at (descending by creation date)
    """
    
    queryset = League.objects.select_related('country', 'sport').all()
    pagination_class = LeaguePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering fields
    filterset_fields = ['country', 'sport', 'is_active']
    
    # Search fields
    search_fields = ['name', 'external_id']
    
    # Ordering fields
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        
        - list → LeagueListSerializer (lightweight)
        - retrieve → LeagueDetailSerializer (comprehensive)
        - create → LeagueCreateSerializer (validation)
        - update/partial_update → LeagueUpdateSerializer (validation)
        
        Returns:
            Serializer class for current action
        """
        if self.action == 'list':
            return LeagueListSerializer
        elif self.action == 'retrieve':
            return LeagueDetailSerializer
        elif self.action == 'create':
            return LeagueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LeagueUpdateSerializer
        return LeagueDetailSerializer
    
    def get_queryset(self):
        """
        Get queryset with optimized database queries
        
        Always includes:
        - select_related('country', 'sport') for foreign key optimization
        
        Returns:
            Optimized queryset
        """
        queryset = super().get_queryset()
        
        # Additional filtering can be added here
        # For example, hide inactive leagues for non-admin users
        
        return queryset
    
    @extend_schema(
        summary="Get leagues by country",
        description="Retrieve all leagues for a specific country",
        parameters=[
            OpenApiParameter(
                name='country_id',
                location=OpenApiParameter.PATH,
                description='Country UUID',
                required=True,
                type=str
            ),
        ],
        tags=['Leagues']
    )
    @action(detail=False, methods=['get'], url_path='by-country/(?P<country_id>[^/.]+)')
    def by_country(self, request, country_id=None):
        """
        Get all leagues for a specific country
        
        URL: GET /api/v1/leagues/by-country/{country_id}/
        
        Args:
            country_id: Country UUID
            
        Returns:
            List of leagues for the specified country
        """
        leagues = self.queryset.filter(country_id=country_id, is_active=True)
        serializer = LeagueListSerializer(leagues, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get active leagues",
        description="Retrieve all active leagues (is_active=True)",
        tags=['Leagues']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active leagues
        
        URL: GET /api/v1/leagues/active/
        
        Returns:
            List of all active leagues
        """
        leagues = self.queryset.filter(is_active=True)
        serializer = LeagueListSerializer(leagues, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Search leagues",
        description="Advanced search with multiple criteria",
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query (searches name and external_id)',
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
        tags=['Leagues']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search endpoint
        
        URL: GET /api/v1/leagues/search/?q=premier&country=<uuid>
        
        Query Parameters:
        - q: Search query (required)
        - country: Country UUID (optional)
        
        Returns:
            List of matching leagues
        """
        query = request.query_params.get('q', '')
        country_id = request.query_params.get('country', None)
        
        if not query:
            return Response(
                {'error': 'Search query (q) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build search query
        leagues = self.queryset.filter(
            Q(name__icontains=query) | Q(external_id__icontains=query)
        )
        
        # Apply country filter if provided
        if country_id:
            leagues = leagues.filter(country_id=country_id)
        
        # Apply pagination
        page = self.paginate_queryset(leagues)
        if page is not None:
            serializer = LeagueListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LeagueListSerializer(leagues, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new league
        
        URL: POST /api/v1/leagues/
        
        Request Body:
            {
                "name": "Premier League",
                "sport": "<sport_id>",
                "country": "<country_uuid>",
                "logo": "https://...",
                "external_id": "api-football-39",
                "is_active": true
            }
        
        Returns:
            201 Created: Newly created league
            400 Bad Request: Validation errors
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detailed response
        headers = self.get_success_headers(serializer.data)
        league = League.objects.select_related('country', 'sport').get(id=serializer.data['id'])
        response_serializer = LeagueDetailSerializer(league)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def perform_create(self, serializer):
        """Save new league instance"""
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing league (full update)
        
        URL: PUT /api/v1/leagues/{id}/
        
        All fields required in request body.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return detailed response
        league = League.objects.select_related('country', 'sport').get(id=instance.id)
        response_serializer = LeagueDetailSerializer(league)
        return Response(response_serializer.data)
    
    def perform_update(self, serializer):
        """Save updated league instance"""
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a league
        
        URL: DELETE /api/v1/leagues/{id}/
        
        Returns:
            204 No Content: Successfully deleted
            404 Not Found: League doesn't exist
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        """Delete league instance"""
        instance.delete()
