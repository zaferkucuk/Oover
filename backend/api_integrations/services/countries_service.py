"""
Countries Service

Business logic for managing country data from external APIs and database operations.

This service provides comprehensive country management including:
- CRUD operations on Country model
- Fetching countries from API-Football
- Data transformation and validation
- Bulk operations with transaction support
- One-time population and periodic sync

Countries are relatively static data that rarely change. This service is designed
for one-time initial population followed by infrequent syncs (recommended: yearly).

Dependencies:
- providers.api_football.client: APIFootballClient
- transformers.country_transformer: CountryTransformer
- apps.core.models: Country

Author: Oover Development Team
Date: November 2025
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from django.db import transaction
from django.db.models import QuerySet, Q
from django.core.exceptions import ValidationError
from django.conf import settings

from apps.core.models import Country
from api_integrations.providers.api_football.client import APIFootballClient
from api_integrations.transformers.country_transformer import CountryTransformer

logger = logging.getLogger(__name__)


class CountriesService:
    """
    Service for managing country data from external APIs and database operations.
    
    This service provides three layers of functionality:
    
    1. Base CRUD Operations:
       - get_by_id, list, count, exists
       - create, update, delete
       - bulk_create, bulk_upsert
       - get_or_create, update_or_create
    
    2. Country-Specific Operations:
       - get_by_code, get_by_external_id
       - search_countries, get_by_name
       - get_countries_with_leagues (future)
    
    3. API Integration:
       - fetch_countries_from_api
       - Transform + Validate + Save pipeline
       - Duplicate detection via external_id
       - Error handling and statistics
    
    Usage Notes:
        - Countries are static data (rarely change)
        - Initial population: fetch all ~200 countries once
        - Periodic sync: yearly refresh recommended
        - Cache results for 1 year after fetching
    
    Example Usage:
        >>> from api_integrations.services.countries_service import CountriesService
        >>> 
        >>> service = CountriesService()
        >>> 
        >>> # Initial population: fetch all countries
        >>> result = service.fetch_countries_from_api()
        >>> print(f"Saved {result['saved']} countries")
        >>> # Output: Saved 200 countries
        >>> 
        >>> # Get country by code
        >>> country = service.get_by_code('GB')
        >>> print(country.name)  # England
        >>> 
        >>> # Search countries
        >>> countries = service.search_countries('united')
        >>> # Returns: United States, United Kingdom, UAE, etc.
        >>> 
        >>> # Get country by external ID
        >>> country = service.get_by_external_id('api-football-ES')
        >>> print(country.name)  # Spain
        >>> 
        >>> # Check if country exists
        >>> exists = service.exists({'code': 'TR'})
        >>> print(exists)  # True if Turkey exists
    """
    
    def __init__(self):
        """
        Initialize countries service with API provider and transformer.
        
        Retrieves API-Football API key from Django settings and initializes:
        - API-Football client (primary and only provider for countries)
        - Country data transformer for API-Football format
        
        Raises:
            ValueError: If API_FOOTBALL_KEY is not configured in settings
        """
        # Get API key from Django settings
        api_key = settings.API_FOOTBALL_CONFIG.get('API_KEY')
        if not api_key:
            error_msg = (
                "API_FOOTBALL_KEY not configured. "
                "Please set API_FOOTBALL_KEY in your .env file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize API-Football client
        self.client = APIFootballClient(api_key=api_key)
        
        # Initialize transformer
        self.transformer = CountryTransformer()
        
        logger.info("Initialized CountriesService with API-Football provider")
    
    # ==================== Basic CRUD Operations ====================
    
    def get_by_id(self, country_id: str) -> Optional[Country]:
        """
        Get country by primary key ID.
        
        Args:
            country_id: Country UUID string
            
        Returns:
            Country object or None if not found
        """
        try:
            return Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            logger.warning(f"Country not found: {country_id}")
            return None
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QuerySet:
        """
        List countries with optional filtering, ordering, and pagination.
        
        Args:
            filters: Dictionary of field filters (e.g., {'code': 'GB'})
            order_by: List of fields to order by (e.g., ['name', '-created_at'])
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            QuerySet of Country objects
        """
        queryset = Country.objects.all()
        
        if filters:
            queryset = queryset.filter(**filters)
        
        if order_by:
            queryset = queryset.order_by(*order_by)
        
        if offset:
            queryset = queryset[offset:]
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count countries matching filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching countries
        """
        queryset = Country.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if any country matches filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            True if at least one country matches, False otherwise
        """
        return Country.objects.filter(**filters).exists()
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> Country:
        """
        Create a new country.
        
        Args:
            data: Country data dictionary
            
        Returns:
            Created Country object
            
        Raises:
            ValidationError: If data is invalid
        """
        # Basic validation
        required_fields = ['name', 'code']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        country = Country.objects.create(**data)
        logger.info(f"Created country: {country.name} ({country.code}) - ID: {country.id}")
        return country
    
    @transaction.atomic
    def update(self, country_id: str, data: Dict[str, Any]) -> Optional[Country]:
        """
        Update existing country.
        
        Args:
            country_id: Country UUID string
            data: Updated country data
            
        Returns:
            Updated Country object or None if not found
        """
        country = self.get_by_id(country_id)
        if not country:
            return None
        
        for field, value in data.items():
            setattr(country, field, value)
        
        country.save()
        logger.info(f"Updated country: {country.name} ({country.code}) - ID: {country.id}")
        return country
    
    @transaction.atomic
    def delete(self, country_id: str) -> bool:
        """
        Delete a country by ID.
        
        Args:
            country_id: Country UUID string
            
        Returns:
            True if deleted, False if not found
        """
        country = self.get_by_id(country_id)
        if not country:
            return False
        
        country_name = country.name
        country_code = country.code
        country.delete()
        logger.info(f"Deleted country: {country_name} ({country_code}) - ID: {country_id}")
        return True
    
    @transaction.atomic
    def bulk_create(
        self,
        countries_data: List[Dict[str, Any]]
    ) -> Tuple[List[Country], List[str]]:
        """
        Bulk create countries.
        
        Args:
            countries_data: List of country data dictionaries
            
        Returns:
            Tuple of (created_countries, error_messages)
        """
        created_countries = []
        errors = []
        
        for idx, data in enumerate(countries_data):
            try:
                country = self.create(data)
                created_countries.append(country)
            except Exception as e:
                error_msg = (
                    f"Country #{idx + 1} ({data.get('name', 'Unknown')}): {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk create: {len(created_countries)} created, {len(errors)} failed"
        )
        return created_countries, errors
    
    @transaction.atomic
    def bulk_upsert_countries(
        self,
        countries_data: List[Dict[str, Any]],
        match_field: str = 'external_id'
    ) -> Tuple[List[Country], List[Country], List[str]]:
        """
        Bulk create or update countries based on match_field.
        
        Args:
            countries_data: List of country data dictionaries
            match_field: Field to use for matching (default: 'external_id')
            
        Returns:
            Tuple of (created_countries, updated_countries, error_messages)
        """
        created_countries = []
        updated_countries = []
        errors = []
        
        for idx, data in enumerate(countries_data):
            try:
                match_value = data.get(match_field)
                if not match_value:
                    raise ValueError(f"Missing {match_field} field")
                
                # Check if country exists
                existing_country = Country.objects.filter(
                    **{match_field: match_value}
                ).first()
                
                if existing_country:
                    # Update existing country
                    for field, value in data.items():
                        setattr(existing_country, field, value)
                    existing_country.save()
                    updated_countries.append(existing_country)
                    logger.debug(
                        f"Updated country: {existing_country.name} ({existing_country.code})"
                    )
                else:
                    # Create new country
                    country = self.create(data)
                    created_countries.append(country)
                    logger.debug(f"Created country: {country.name} ({country.code})")
                    
            except Exception as e:
                error_msg = (
                    f"Country #{idx + 1} ({data.get('name', 'Unknown')}): {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk upsert: {len(created_countries)} created, "
            f"{len(updated_countries)} updated, {len(errors)} failed"
        )
        return created_countries, updated_countries, errors
    
    def get_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[Country, bool]:
        """
        Get existing country or create new one.
        
        Args:
            defaults: Default values for creation
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (Country, created_boolean)
        """
        return Country.objects.get_or_create(defaults=defaults, **kwargs)
    
    @transaction.atomic
    def update_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[Country, bool]:
        """
        Update existing country or create new one.
        
        Args:
            defaults: Values to update/create with
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (Country, created_boolean)
        """
        return Country.objects.update_or_create(defaults=defaults, **kwargs)
    
    # ==================== Country-Specific Operations ====================
    
    def get_by_code(self, code: str) -> Optional[Country]:
        """
        Get country by ISO 3166-1 alpha-2 code.
        
        Args:
            code: 2-letter country code (e.g., 'GB', 'ES', 'TR')
            
        Returns:
            Country object or None if not found
        """
        try:
            return Country.objects.get(code=code.upper())
        except Country.DoesNotExist:
            logger.debug(f"Country not found by code: {code}")
            return None
    
    def get_by_external_id(self, external_id: str) -> Optional[Country]:
        """
        Get country by external API identifier.
        
        Args:
            external_id: External ID (e.g., 'api-football-GB')
            
        Returns:
            Country object or None if not found
        """
        try:
            return Country.objects.get(external_id=external_id)
        except Country.DoesNotExist:
            logger.debug(f"Country not found by external_id: {external_id}")
            return None
    
    def get_by_name(self, name: str, exact: bool = True) -> Optional[Country]:
        """
        Get country by name.
        
        Args:
            name: Country name
            exact: If True, exact match; if False, case-insensitive match
            
        Returns:
            Country object or None if not found
        """
        try:
            if exact:
                return Country.objects.get(name=name)
            else:
                return Country.objects.get(name__iexact=name)
        except Country.DoesNotExist:
            logger.debug(f"Country not found by name: {name}")
            return None
    
    def search_countries(self, query: str) -> QuerySet:
        """
        Search countries by name or code.
        
        Args:
            query: Search term
            
        Returns:
            QuerySet of matching Country objects
        """
        filters = Q(name__icontains=query) | Q(code__icontains=query)
        return Country.objects.filter(filters)
    
    # ==================== API Integration ====================
    
    @transaction.atomic
    def fetch_countries_from_api(
        self,
        name_filter: Optional[str] = None,
        code_filter: Optional[str] = None,
        search_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch countries from API-Football and save to database.
        
        This is the main method for populating/syncing country data.
        Typically called once for initial population, then yearly for sync.
        
        Workflow:
        1. Fetch countries from API-Football
        2. Transform to internal format
        3. Validate data
        4. Upsert to database (create new, update existing)
        
        Args:
            name_filter: Optional country name filter
            code_filter: Optional country code filter
            search_filter: Optional search term
            
        Returns:
            Dictionary with operation statistics:
            {
                'fetched': 200,
                'transformed': 200,
                'saved': 200,
                'created': 150,
                'updated': 50,
                'failed': 0,
                'errors': []
            }
        """
        logger.info(
            f"fetch_countries_from_api called: "
            f"name={name_filter}, code={code_filter}, search={search_filter}"
        )
        
        stats = {
            'fetched': 0,
            'transformed': 0,
            'saved': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Fetch countries from API-Football
            logger.info("Fetching countries from API-Football...")
            api_countries = self.client.get_countries(
                name=name_filter,
                code=code_filter,
                search=search_filter
            )
            
            stats['fetched'] = len(api_countries)
            logger.info(f"Fetched {stats['fetched']} countries from API-Football")
            
            if not api_countries:
                logger.warning("No countries returned from API")
                return stats
            
            # Transform countries data
            transformed_countries = []
            for api_country in api_countries:
                try:
                    transformed = self.transformer.transform(
                        api_country,
                        provider='api-football'
                    )
                    if transformed:
                        transformed_countries.append(transformed)
                        stats['transformed'] += 1
                    else:
                        error_msg = (
                            f"Transform returned None for "
                            f"{api_country.get('name', 'Unknown')}"
                        )
                        stats['errors'].append(error_msg)
                        logger.warning(error_msg)
                except Exception as e:
                    error_msg = (
                        f"Transform error for {api_country.get('name', 'Unknown')}: "
                        f"{str(e)}"
                    )
                    stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Transformed {stats['transformed']} countries")
            
            # Check transformer errors
            if self.transformer.has_errors():
                transformer_errors = self.transformer.get_errors()
                stats['errors'].extend(transformer_errors)
                logger.warning(
                    f"Transformer collected {len(transformer_errors)} errors"
                )
            
            # Save countries to database (upsert)
            created, updated, save_errors = self.bulk_upsert_countries(
                transformed_countries,
                match_field='external_id'
            )
            
            stats['created'] = len(created)
            stats['updated'] = len(updated)
            stats['saved'] = stats['created'] + stats['updated']
            stats['failed'] = len(save_errors)
            stats['errors'].extend(save_errors)
            
            logger.info(
                f"Fetch complete: {stats['fetched']} fetched, "
                f"{stats['saved']} saved ({stats['created']} new, "
                f"{stats['updated']} updated), {stats['failed']} failed"
            )
            
            if stats['errors']:
                logger.warning(
                    f"Encountered {len(stats['errors'])} errors during fetch"
                )
            
            return stats
            
        except Exception as e:
            error_msg = f"Fatal error in fetch_countries_from_api: {str(e)}"
            logger.exception(error_msg)
            stats['errors'].append(error_msg)
            raise
