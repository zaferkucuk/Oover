"""
Country ViewSet for Django REST Framework

This module provides API endpoints for country data management
in the Oover sport prediction application.

Endpoints:
    - GET    /api/countries/          - List all countries
    - GET    /api/countries/{id}/     - Get single country
    - POST   /api/countries/          - Create new country
    - PUT    /api/countries/{id}/     - Update country
    - DELETE /api/countries/{id}/     - Delete country
    - POST   /api/countries/search/   - Search countries
    - GET    /api/countries/statistics/ - Get statistics
    - GET    /api/countries/export/   - Export countries

Author: Oover Development Team
Date: October 2025
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from typing import Dict, Any, List, Optional
import logging
from supabase import create_client, Client
import os
from datetime import datetime

from ..serializers.country import (
    CountrySerializer,
    CountryCreateSerializer,
    CountryUpdateSerializer,
    CountryWithRelationsSerializer,
    CountryFilterSerializer,
    CountryListResponseSerializer,
    CountryResponseSerializer,
    CountryOperationResultSerializer
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials not found in environment variables")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class CountryPagination(PageNumberPagination):
    """
    Custom pagination class for country list endpoints
    
    Attributes:
        page_size: Default number of items per page
        page_size_query_param: Query parameter for custom page size
        max_page_size: Maximum allowed page size
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class CountryViewSet(viewsets.ViewSet):
    """
    ViewSet for Country CRUD operations
    
    This ViewSet provides comprehensive country data management:
    - CRUD operations for countries
    - Advanced filtering and search
    - Statistics and analytics
    - Data export functionality
    - Bulk operations support
    
    Authentication:
        - List/Retrieve: Public access (AllowAny)
        - Create/Update/Delete: Authenticated users only
        
    Example Usage:
        # List countries
        GET /api/countries/?is_active=true&page=1&page_size=20
        
        # Get single country
        GET /api/countries/tr/
        
        # Create country
        POST /api/countries/
        {
            "id": "nl",
            "name": "Netherlands",
            "code": "NLD",
            "flag": "🇳🇱",
            "is_international": false,
            "is_active": true
        }
        
        # Update country
        PUT /api/countries/nl/
        {
            "name": "The Netherlands",
            "is_active": true
        }
        
        # Search countries
        POST /api/countries/search/
        {
            "query": "united",
            "filters": {
                "is_active": true
            }
        }
    """
    
    pagination_class = CountryPagination
    
    def get_permissions(self):
        """
        Define permissions based on action
        
        Returns:
            List of permission classes
        """
        if self.action in ['list', 'retrieve', 'search', 'statistics']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def _get_supabase_client(self) -> Optional[Client]:
        """
        Get Supabase client instance
        
        Returns:
            Supabase client or None if not configured
        """
        if supabase is None:
            logger.error("Supabase client not initialized")
        return supabase
    
    def _build_query_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Supabase query filters from request parameters
        
        Args:
            filters: Dictionary of filter parameters
            
        Returns:
            Processed filters for Supabase query
        """
        query_filters = {}
        
        if 'is_active' in filters:
            query_filters['is_active'] = filters['is_active']
            
        if 'is_international' in filters:
            query_filters['is_international'] = filters['is_international']
            
        return query_filters
    
    def _paginate_queryset(self, queryset: List[Dict], page: int, page_size: int) -> Dict[str, Any]:
        """
        Paginate queryset manually
        
        Args:
            queryset: List of items to paginate
            page: Page number (1-indexed)
            page_size: Items per page
            
        Returns:
            Paginated response data
        """
        total = len(queryset)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            'data': queryset[start:end],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }
    
    def list(self, request):
        """
        List all countries with optional filtering and pagination
        
        Query Parameters:
            - is_active (bool): Filter by active status
            - is_international (bool): Filter by international status
            - name_contains (str): Filter by name substring
            - page (int): Page number (default: 1)
            - page_size (int): Items per page (default: 50, max: 100)
            - sort_by (str): Sort field (name|code|created_at|updated_at)
            - sort_order (str): Sort order (asc|desc)
            - include_counts (bool): Include leagues/teams counts
            
        Returns:
            200: Paginated list of countries
            500: Server error
            
        Example:
            GET /api/countries/?is_active=true&page=1&page_size=20&sort_by=name
        """
        try:
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available',
                        'error': 'Supabase client not initialized'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Parse query parameters
            filter_serializer = CountryFilterSerializer(data=request.query_params)
            if not filter_serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid query parameters',
                        'errors': filter_serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            filters = filter_serializer.validated_data
            
            # Build Supabase query
            query = client.table('countries').select('*')
            
            # Apply filters
            if 'is_active' in filters:
                query = query.eq('is_active', filters['is_active'])
            
            if 'is_international' in filters:
                query = query.eq('is_international', filters['is_international'])
            
            if 'name_contains' in filters:
                query = query.ilike('name', f"%{filters['name_contains']}%")
            
            if 'ids' in filters:
                query = query.in_('id', filters['ids'])
            
            if 'codes' in filters:
                query = query.in_('code', filters['codes'])
            
            # Apply sorting
            sort_by = filters.get('sort_by', 'name')
            sort_order = filters.get('sort_order', 'asc')
            ascending = sort_order == 'asc'
            query = query.order(sort_by, desc=not ascending)
            
            # Execute query
            response = query.execute()
            
            if not response.data:
                return Response(
                    self._paginate_queryset([], filters.get('page', 1), filters.get('page_size', 50)),
                    status=status.HTTP_200_OK
                )
            
            # Add counts if requested
            if filters.get('include_counts', False):
                for country in response.data:
                    # Get leagues count
                    leagues_response = client.table('leagues')\
                        .select('id', count='exact')\
                        .eq('country_id', country['id'])\
                        .execute()
                    country['leagues_count'] = len(leagues_response.data) if leagues_response.data else 0
                    
                    # Get teams count
                    teams_response = client.table('teams')\
                        .select('id', count='exact')\
                        .eq('country_id', country['id'])\
                        .execute()
                    country['teams_count'] = len(teams_response.data) if teams_response.data else 0
            
            # Paginate results
            paginated_data = self._paginate_queryset(
                response.data,
                filters.get('page', 1),
                filters.get('page_size', 50)
            )
            
            # Serialize response
            serializer = CountryListResponseSerializer(data=paginated_data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Return raw data if serialization fails
                return Response(paginated_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error listing countries: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to list countries',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a single country by ID
        
        Args:
            pk: Country ID
            
        Query Parameters:
            - include_relations (bool): Include leagues and teams
            - include_counts (bool): Include leagues/teams counts
            
        Returns:
            200: Country data
            404: Country not found
            500: Server error
            
        Example:
            GET /api/countries/tr/?include_relations=true
        """
        try:
            if not pk:
                return Response(
                    {
                        'success': False,
                        'message': 'Country ID is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Fetch country
            response = client.table('countries')\
                .select('*')\
                .eq('id', pk.lower())\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return Response(
                    {
                        'success': False,
                        'message': f'Country with ID "{pk}" not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            country = response.data[0]
            
            # Add relations if requested
            include_relations = request.query_params.get('include_relations', '').lower() == 'true'
            include_counts = request.query_params.get('include_counts', '').lower() == 'true'
            
            if include_relations or include_counts:
                # Get leagues
                leagues_response = client.table('leagues')\
                    .select('id, name, logo, is_active')\
                    .eq('country_id', pk.lower())\
                    .execute()
                
                if include_relations:
                    country['leagues'] = leagues_response.data if leagues_response.data else []
                
                if include_counts:
                    country['leagues_count'] = len(leagues_response.data) if leagues_response.data else 0
                
                # Get teams
                teams_response = client.table('teams')\
                    .select('id, name, logo, is_active')\
                    .eq('country_id', pk.lower())\
                    .execute()
                
                if include_relations:
                    country['teams'] = teams_response.data if teams_response.data else []
                
                if include_counts:
                    country['teams_count'] = len(teams_response.data) if teams_response.data else 0
            
            # Serialize response
            serializer_class = CountryWithRelationsSerializer if (include_relations or include_counts) else CountrySerializer
            serializer = serializer_class(data=country)
            
            if serializer.is_valid():
                return Response(
                    {
                        'success': True,
                        'data': serializer.data,
                        'message': 'Country retrieved successfully'
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Return raw data if serialization fails
                return Response(
                    {
                        'success': True,
                        'data': country
                    },
                    status=status.HTTP_200_OK
                )
                
        except Exception as e:
            logger.error(f"Error retrieving country {pk}: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to retrieve country',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """
        Create a new country
        
        Request Body:
            {
                "id": "nl",               # Required, 2-10 chars, alphanumeric
                "name": "Netherlands",     # Required, max 100 chars
                "code": "NLD",            # Required, 2-10 chars, alphanumeric
                "flag": "🇳🇱",             # Required, max 50 chars
                "is_international": false, # Optional, default: false
                "is_active": true         # Optional, default: true
            }
            
        Returns:
            201: Country created successfully
            400: Invalid request data
            409: Country already exists
            500: Server error
            
        Example:
            POST /api/countries/
            {
                "id": "nl",
                "name": "Netherlands",
                "code": "NLD",
                "flag": "🇳🇱"
            }
        """
        try:
            # Validate request data
            serializer = CountryCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid request data',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Check if country already exists
            existing = client.table('countries')\
                .select('id')\
                .eq('id', serializer.validated_data['id'])\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                return Response(
                    {
                        'success': False,
                        'message': f'Country with ID "{serializer.validated_data["id"]}" already exists'
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Create country
            country_data = serializer.validated_data
            country_data['created_at'] = datetime.utcnow().isoformat()
            country_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = client.table('countries').insert(country_data).execute()
            
            if not response.data:
                return Response(
                    {
                        'success': False,
                        'message': 'Failed to create country'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return created country
            result_serializer = CountryOperationResultSerializer(data={
                'success': True,
                'data': response.data[0],
                'message': 'Country created successfully'
            })
            
            if result_serializer.is_valid():
                return Response(
                    result_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'success': True,
                        'data': response.data[0],
                        'message': 'Country created successfully'
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"Error creating country: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to create country',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """
        Update an existing country
        
        Args:
            pk: Country ID
            
        Request Body:
            {
                "name": "The Netherlands",    # Optional
                "code": "NLD",               # Optional
                "flag": "🇳🇱",                # Optional
                "is_international": false,   # Optional
                "is_active": true            # Optional
            }
            
        Returns:
            200: Country updated successfully
            400: Invalid request data
            404: Country not found
            500: Server error
            
        Example:
            PUT /api/countries/nl/
            {
                "name": "The Netherlands",
                "is_active": true
            }
        """
        try:
            if not pk:
                return Response(
                    {
                        'success': False,
                        'message': 'Country ID is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate request data
            update_data = {**request.data, 'id': pk.lower()}
            serializer = CountryUpdateSerializer(data=update_data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid request data',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Check if country exists
            existing = client.table('countries')\
                .select('*')\
                .eq('id', pk.lower())\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                return Response(
                    {
                        'success': False,
                        'message': f'Country with ID "{pk}" not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Prepare update data (exclude id field)
            validated_data = serializer.validated_data
            update_fields = {k: v for k, v in validated_data.items() if k != 'id'}
            update_fields['updated_at'] = datetime.utcnow().isoformat()
            
            # Update country
            response = client.table('countries')\
                .update(update_fields)\
                .eq('id', pk.lower())\
                .execute()
            
            if not response.data:
                return Response(
                    {
                        'success': False,
                        'message': 'Failed to update country'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return updated country
            result_serializer = CountryOperationResultSerializer(data={
                'success': True,
                'data': response.data[0],
                'message': 'Country updated successfully'
            })
            
            if result_serializer.is_valid():
                return Response(result_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'success': True,
                        'data': response.data[0],
                        'message': 'Country updated successfully'
                    },
                    status=status.HTTP_200_OK
                )
                
        except Exception as e:
            logger.error(f"Error updating country {pk}: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to update country',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, pk=None):
        """
        Delete a country
        
        Args:
            pk: Country ID
            
        Returns:
            200: Country deleted successfully
            404: Country not found
            409: Cannot delete (has related data)
            500: Server error
            
        Example:
            DELETE /api/countries/nl/
        """
        try:
            if not pk:
                return Response(
                    {
                        'success': False,
                        'message': 'Country ID is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Check if country exists
            existing = client.table('countries')\
                .select('*')\
                .eq('id', pk.lower())\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                return Response(
                    {
                        'success': False,
                        'message': f'Country with ID "{pk}" not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check for related data
            leagues = client.table('leagues')\
                .select('id', count='exact')\
                .eq('country_id', pk.lower())\
                .execute()
            
            teams = client.table('teams')\
                .select('id', count='exact')\
                .eq('country_id', pk.lower())\
                .execute()
            
            if (leagues.data and len(leagues.data) > 0) or (teams.data and len(teams.data) > 0):
                return Response(
                    {
                        'success': False,
                        'message': 'Cannot delete country with related leagues or teams',
                        'details': {
                            'leagues_count': len(leagues.data) if leagues.data else 0,
                            'teams_count': len(teams.data) if teams.data else 0
                        }
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Delete country
            response = client.table('countries')\
                .delete()\
                .eq('id', pk.lower())\
                .execute()
            
            return Response(
                {
                    'success': True,
                    'message': f'Country "{pk}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
                
        except Exception as e:
            logger.error(f"Error deleting country {pk}: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to delete country',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def search(self, request):
        """
        Advanced country search with multiple criteria
        
        Request Body:
            {
                "query": "united",         # Search term (searches name, code)
                "filters": {
                    "is_active": true,
                    "is_international": false
                },
                "page": 1,
                "page_size": 20
            }
            
        Returns:
            200: Search results
            400: Invalid request
            500: Server error
            
        Example:
            POST /api/countries/search/
            {
                "query": "united",
                "filters": {"is_active": true}
            }
        """
        try:
            query_text = request.data.get('query', '').strip()
            filters = request.data.get('filters', {})
            page = request.data.get('page', 1)
            page_size = request.data.get('page_size', 20)
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Build query
            query = client.table('countries').select('*')
            
            # Apply text search
            if query_text:
                # Search in name and code
                query = query.or_(f'name.ilike.%{query_text}%,code.ilike.%{query_text}%')
            
            # Apply filters
            if filters.get('is_active') is not None:
                query = query.eq('is_active', filters['is_active'])
            
            if filters.get('is_international') is not None:
                query = query.eq('is_international', filters['is_international'])
            
            # Execute query
            response = query.execute()
            
            if not response.data:
                return Response(
                    self._paginate_queryset([], page, page_size),
                    status=status.HTTP_200_OK
                )
            
            # Paginate results
            paginated_data = self._paginate_queryset(response.data, page, page_size)
            
            return Response(
                {
                    'success': True,
                    **paginated_data
                },
                status=status.HTTP_200_OK
            )
                
        except Exception as e:
            logger.error(f"Error searching countries: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to search countries',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def statistics(self, request):
        """
        Get country statistics and analytics
        
        Returns:
            200: Statistics data
            500: Server error
            
        Response:
            {
                "total_countries": 10,
                "active_countries": 8,
                "international_countries": 1,
                "by_status": {
                    "active": 8,
                    "inactive": 2
                },
                "by_type": {
                    "international": 1,
                    "national": 9
                },
                "with_leagues": 7,
                "with_teams": 8
            }
            
        Example:
            GET /api/countries/statistics/
        """
        try:
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Get all countries
            countries_response = client.table('countries').select('*').execute()
            countries = countries_response.data if countries_response.data else []
            
            # Calculate statistics
            total = len(countries)
            active = sum(1 for c in countries if c.get('is_active', False))
            international = sum(1 for c in countries if c.get('is_international', False))
            
            # Count countries with leagues
            with_leagues = 0
            with_teams = 0
            
            for country in countries:
                # Check leagues
                leagues = client.table('leagues')\
                    .select('id')\
                    .eq('country_id', country['id'])\
                    .limit(1)\
                    .execute()
                if leagues.data and len(leagues.data) > 0:
                    with_leagues += 1
                
                # Check teams
                teams = client.table('teams')\
                    .select('id')\
                    .eq('country_id', country['id'])\
                    .limit(1)\
                    .execute()
                if teams.data and len(teams.data) > 0:
                    with_teams += 1
            
            stats = {
                'total_countries': total,
                'active_countries': active,
                'inactive_countries': total - active,
                'international_countries': international,
                'national_countries': total - international,
                'by_status': {
                    'active': active,
                    'inactive': total - active
                },
                'by_type': {
                    'international': international,
                    'national': total - international
                },
                'with_leagues': with_leagues,
                'with_teams': with_teams,
                'without_data': total - max(with_leagues, with_teams)
            }
            
            return Response(
                {
                    'success': True,
                    'data': stats,
                    'message': 'Statistics retrieved successfully'
                },
                status=status.HTTP_200_OK
            )
                
        except Exception as e:
            logger.error(f"Error getting country statistics: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to retrieve statistics',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def export(self, request):
        """
        Export countries data in various formats
        
        Query Parameters:
            - format (str): Export format (json|csv) - default: json
            - is_active (bool): Filter by active status
            - is_international (bool): Filter by international status
            
        Returns:
            200: Exported data
            400: Invalid format
            500: Server error
            
        Example:
            GET /api/countries/export/?format=json&is_active=true
        """
        try:
            export_format = request.query_params.get('format', 'json').lower()
            
            if export_format not in ['json', 'csv']:
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid export format. Supported: json, csv'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Build query
            query = client.table('countries').select('*')
            
            # Apply filters
            if request.query_params.get('is_active'):
                is_active = request.query_params.get('is_active').lower() == 'true'
                query = query.eq('is_active', is_active)
            
            if request.query_params.get('is_international'):
                is_international = request.query_params.get('is_international').lower() == 'true'
                query = query.eq('is_international', is_international)
            
            # Execute query
            response = query.execute()
            
            if not response.data:
                return Response(
                    {
                        'success': False,
                        'message': 'No data to export'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Return data in requested format
            if export_format == 'json':
                return Response(
                    {
                        'success': True,
                        'data': response.data,
                        'count': len(response.data),
                        'exported_at': datetime.utcnow().isoformat()
                    },
                    status=status.HTTP_200_OK
                )
            
            elif export_format == 'csv':
                # Convert to CSV format
                import csv
                from io import StringIO
                
                output = StringIO()
                if response.data:
                    fieldnames = response.data[0].keys()
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(response.data)
                
                csv_content = output.getvalue()
                
                from django.http import HttpResponse
                response = HttpResponse(csv_content, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="countries_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv"'
                return response
                
        except Exception as e:
            logger.error(f"Error exporting countries: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to export countries',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_create(self, request):
        """
        Create multiple countries at once
        
        Request Body:
            {
                "countries": [
                    {
                        "id": "nl",
                        "name": "Netherlands",
                        "code": "NLD",
                        "flag": "🇳🇱"
                    },
                    {
                        "id": "be",
                        "name": "Belgium",
                        "code": "BEL",
                        "flag": "🇧🇪"
                    }
                ]
            }
            
        Returns:
            201: Bulk create successful
            400: Invalid request data
            500: Server error
            
        Response:
            {
                "success": true,
                "created": 2,
                "failed": 0,
                "results": [...]
            }
            
        Example:
            POST /api/countries/bulk_create/
        """
        try:
            countries_data = request.data.get('countries', [])
            
            if not countries_data or not isinstance(countries_data, list):
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid request: "countries" array is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get Supabase client
            client = self._get_supabase_client()
            if not client:
                return Response(
                    {
                        'success': False,
                        'message': 'Database connection not available'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Validate and prepare countries
            validated_countries = []
            errors = []
            
            for idx, country_data in enumerate(countries_data):
                serializer = CountryCreateSerializer(data=country_data)
                if serializer.is_valid():
                    country = serializer.validated_data
                    country['created_at'] = datetime.utcnow().isoformat()
                    country['updated_at'] = datetime.utcnow().isoformat()
                    validated_countries.append(country)
                else:
                    errors.append({
                        'index': idx,
                        'data': country_data,
                        'errors': serializer.errors
                    })
            
            if errors:
                return Response(
                    {
                        'success': False,
                        'message': 'Validation errors in request data',
                        'errors': errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Bulk insert
            response = client.table('countries').insert(validated_countries).execute()
            
            created_count = len(response.data) if response.data else 0
            
            return Response(
                {
                    'success': True,
                    'created': created_count,
                    'failed': len(countries_data) - created_count,
                    'results': response.data,
                    'message': f'Successfully created {created_count} countries'
                },
                status=status.HTTP_201_CREATED
            )
                
        except Exception as e:
            logger.error(f"Error bulk creating countries: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'message': 'Failed to bulk create countries',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
