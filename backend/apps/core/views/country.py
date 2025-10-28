"""
Country Views for Django REST Framework

This module provides ViewSets for Country model, enabling
full CRUD operations via REST API endpoints.

Author: Oover Development Team
Date: October 2025
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.core.models import Country
from apps.core.serializers.country import (
    CountrySerializer,
    CountryCreateSerializer,
    CountryUpdateSerializer,
    CountryWithRelationsSerializer,
    CountryFilterSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all countries",
        description="Retrieve a paginated list of all countries with optional filtering",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=bool,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='is_international',
                type=bool,
                description='Filter by international status'
            ),
            OpenApiParameter(
                name='search',
                type=str,
                description='Search in country name or code'
            ),
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by: name, code, created_at, updated_at (prefix with - for descending)'
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Get country details",
        description="Retrieve detailed information about a specific country"
    ),
    create=extend_schema(
        summary="Create new country",
        description="Create a new country record"
    ),
    update=extend_schema(
        summary="Update country",
        description="Update all fields of a country"
    ),
    partial_update=extend_schema(
        summary="Partially update country",
        description="Update specific fields of a country"
    ),
    destroy=extend_schema(
        summary="Delete country",
        description="Delete a country record"
    ),
)
class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Country model providing full CRUD operations.
    
    Endpoints:
    - GET    /api/countries/          - List all countries (paginated)
    - POST   /api/countries/          - Create new country
    - GET    /api/countries/{id}/     - Get country details
    - PUT    /api/countries/{id}/     - Update country (all fields)
    - PATCH  /api/countries/{id}/     - Partial update country
    - DELETE /api/countries/{id}/     - Delete country
    - GET    /api/countries/active/   - List only active countries
    - GET    /api/countries/stats/    - Get country statistics
    """
    
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'id'
    
    # Filtering and search
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    # DjangoFilterBackend settings
    filterset_fields = {
        'is_active': ['exact'],
        'is_international': ['exact'],
        'code': ['exact', 'icontains'],
    }
    
    # SearchFilter settings - search in name and code
    search_fields = ['name', 'code']
    
    # OrderingFilter settings
    ordering_fields = ['name', 'code', 'created_at', 'updated_at']
    ordering = ['name']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        - list/retrieve: CountrySerializer (basic info)
        - create: CountryCreateSerializer (validation for new records)
        - update/partial_update: CountryUpdateSerializer (validation for updates)
        """
        if self.action == 'create':
            return CountryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CountryUpdateSerializer
        elif self.action in ['retrieve', 'with_relations']:
            return CountryWithRelationsSerializer
        return CountrySerializer
    
    def get_queryset(self):
        """
        Optionally restricts the returned countries based on query parameters.
        
        Query parameters:
        - is_active: boolean (true/false)
        - is_international: boolean (true/false)
        - include_relations: boolean (true/false) - prefetch leagues and teams
        """
        queryset = Country.objects.all()
        
        # Prefetch related data if requested
        include_relations = self.request.query_params.get('include_relations', 'false')
        if include_relations.lower() == 'true':
            queryset = queryset.prefetch_related('leagues', 'teams')
        
        return queryset
    
    @extend_schema(
        summary="List active countries",
        description="Retrieve only active countries (is_active=True)"
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Custom endpoint to get only active countries.
        
        GET /api/countries/active/
        """
        active_countries = self.get_queryset().filter(is_active=True)
        
        # Apply pagination
        page = self.paginate_queryset(active_countries)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(active_countries, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get country statistics",
        description="Get aggregate statistics about countries"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get country statistics.
        
        GET /api/countries/stats/
        
        Returns:
        - total_countries: Total number of countries
        - active_countries: Number of active countries
        - international_entities: Number of international entities
        - countries_with_leagues: Number of countries that have leagues
        - countries_with_teams: Number of countries that have teams
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_countries': queryset.count(),
            'active_countries': queryset.filter(is_active=True).count(),
            'international_entities': queryset.filter(is_international=True).count(),
            'national_countries': queryset.filter(is_international=False).count(),
            'countries_with_leagues': queryset.filter(leagues__isnull=False).distinct().count(),
            'countries_with_teams': queryset.filter(teams__isnull=False).distinct().count(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Get country with relations",
        description="Get country details including leagues and teams"
    )
    @action(detail=True, methods=['get'])
    def with_relations(self, request, id=None):
        """
        Get country with all related leagues and teams.
        
        GET /api/countries/{id}/with_relations/
        """
        country = self.get_object()
        
        # Use serializer with relations
        serializer = CountryWithRelationsSerializer(country)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        """
        List countries with pagination and filtering.
        
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
        Retrieve a single country.
        
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
        Create a new country.
        
        Override to add custom response structure.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'success': True,
            'message': 'Country created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update a country.
        
        Override to add custom response structure.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Country updated successfully',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a country.
        
        Override to add custom response structure.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response({
            'success': True,
            'message': 'Country deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
