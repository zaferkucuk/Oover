"""
Leagues Service

Business logic for managing league data from external APIs and database operations.

This service provides comprehensive league management including:
- CRUD operations on League model
- Fetching leagues from API-Football
- Data transformation and validation
- Bulk operations with transaction support
- Seasonal updates and league discovery

Leagues data is semi-static (stable within a season but changes between seasons).
This service is designed for:
- Initial population: fetch all ~800 leagues once
- Seasonal updates: refresh at season boundaries (typically summer)
- Discovery: find new leagues as they become available

Dependencies:
- providers.api_football.client: APIFootballClient
- transformers.league_transformer: LeagueTransformer
- apps.core.models: League, Country

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

from apps.core.models import League, Country
from api_integrations.providers.api_football.client import APIFootballClient
from api_integrations.transformers.league_transformer import LeagueTransformer

logger = logging.getLogger(__name__)


class LeaguesService:
    """
    Service for managing league data from external APIs and database operations.
    
    This service provides three layers of functionality:
    
    1. Base CRUD Operations:
       - get_by_id, list, count, exists
       - create, update, delete
       - bulk_create, bulk_upsert
       - get_or_create, update_or_create
    
    2. League-Specific Operations:
       - get_by_external_id, get_by_name
       - get_by_country, get_by_tier
       - get_by_confederation, get_current_leagues
       - search_leagues
    
    3. API Integration:
       - fetch_leagues_from_api
       - Transform + Validate + Save pipeline
       - Duplicate detection via external_id
       - Error handling and statistics
    
    Usage Notes:
        - Leagues are semi-static (stable within season)
        - Initial population: fetch all ~800 leagues once
        - Seasonal sync: refresh at season boundaries (summer)
        - Cache results for 6 months after fetching
        - Focus on top-tier leagues for daily operations
    
    Example Usage:
        >>> from api_integrations.services.leagues_service import LeaguesService
        >>> 
        >>> service = LeaguesService()
        >>> 
        >>> # Initial population: fetch all leagues
        >>> result = service.fetch_leagues_from_api()
        >>> print(f"Saved {result['saved']} leagues")
        >>> # Output: Saved 800 leagues
        >>> 
        >>> # Fetch leagues for specific country
        >>> spain = Country.objects.get(code='ES')
        >>> result = service.fetch_leagues_from_api(country_id=spain.id)
        >>> print(f"Saved {result['saved']} Spanish leagues")
        >>> # Output: Saved 8 Spanish leagues
        >>> 
        >>> # Get current season leagues only
        >>> result = service.fetch_leagues_from_api(current_only=True)
        >>> print(f"Saved {result['saved']} active leagues")
        >>> 
        >>> # Get league by external ID
        >>> league = service.get_by_external_id('api-football-140')
        >>> print(league.name)  # La Liga
        >>> 
        >>> # Get leagues by country
        >>> leagues = service.get_by_country(spain.id)
        >>> print([l.name for l in leagues])
        >>> # Output: ['La Liga', 'Segunda División', ...]
        >>> 
        >>> # Get top-tier leagues
        >>> top_leagues = service.get_by_tier(1)
        >>> print(f"Found {top_leagues.count()} tier 1 leagues")
        >>> 
        >>> # Search leagues
        >>> leagues = service.search_leagues('premier')
        >>> # Returns: Premier League, Scottish Premiership, etc.
    """
    
    def __init__(self):
        """
        Initialize leagues service with API provider and transformer.
        
        Retrieves API-Football API key from Django settings and initializes:
        - API-Football client (primary and only provider for leagues)
        - League data transformer for API-Football format
        
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
        self.transformer = LeagueTransformer()
        
        logger.info("Initialized LeaguesService with API-Football provider")
    
    # ==================== Basic CRUD Operations ====================
    
    def get_by_id(self, league_id: str) -> Optional[League]:
        """
        Get league by primary key ID.
        
        Args:
            league_id: League UUID string
            
        Returns:
            League object or None if not found
        """
        try:
            return League.objects.select_related('country').get(id=league_id)
        except League.DoesNotExist:
            logger.warning(f"League not found: {league_id}")
            return None
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QuerySet:
        """
        List leagues with optional filtering, ordering, and pagination.
        
        Args:
            filters: Dictionary of field filters (e.g., {'country_id': 'uuid-here'})
            order_by: List of fields to order by (e.g., ['tier', 'name'])
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            QuerySet of League objects with country pre-fetched
        """
        queryset = League.objects.select_related('country').all()
        
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
        Count leagues matching filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching leagues
        """
        queryset = League.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if any league matches filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            True if at least one league matches, False otherwise
        """
        return League.objects.filter(**filters).exists()
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> League:
        """
        Create a new league.
        
        Args:
            data: League data dictionary
            
        Returns:
            Created League object
            
        Raises:
            ValidationError: If data is invalid
        """
        # Basic validation
        required_fields = ['name', 'country_id']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate country exists
        country_id = data.get('country_id')
        if not Country.objects.filter(id=country_id).exists():
            raise ValidationError(f"Country not found: {country_id}")
        
        league = League.objects.create(**data)
        logger.info(
            f"Created league: {league.name} ({league.country.name}) - "
            f"ID: {league.id}"
        )
        return league
    
    @transaction.atomic
    def update(self, league_id: str, data: Dict[str, Any]) -> Optional[League]:
        """
        Update existing league.
        
        Args:
            league_id: League UUID string
            data: Updated league data
            
        Returns:
            Updated League object or None if not found
        """
        league = self.get_by_id(league_id)
        if not league:
            return None
        
        # Validate country if being updated
        if 'country_id' in data:
            country_id = data['country_id']
            if not Country.objects.filter(id=country_id).exists():
                raise ValidationError(f"Country not found: {country_id}")
        
        for field, value in data.items():
            setattr(league, field, value)
        
        league.save()
        logger.info(
            f"Updated league: {league.name} ({league.country.name}) - "
            f"ID: {league.id}"
        )
        return league
    
    @transaction.atomic
    def delete(self, league_id: str) -> bool:
        """
        Delete a league by ID.
        
        Args:
            league_id: League UUID string
            
        Returns:
            True if deleted, False if not found
        """
        league = self.get_by_id(league_id)
        if not league:
            return False
        
        league_name = league.name
        country_name = league.country.name
        league.delete()
        logger.info(
            f"Deleted league: {league_name} ({country_name}) - "
            f"ID: {league_id}"
        )
        return True
    
    @transaction.atomic
    def bulk_create(
        self,
        leagues_data: List[Dict[str, Any]]
    ) -> Tuple[List[League], List[str]]:
        """
        Bulk create leagues.
        
        Args:
            leagues_data: List of league data dictionaries
            
        Returns:
            Tuple of (created_leagues, error_messages)
        """
        created_leagues = []
        errors = []
        
        for idx, data in enumerate(leagues_data):
            try:
                league = self.create(data)
                created_leagues.append(league)
            except Exception as e:
                error_msg = (
                    f"League #{idx + 1} ({data.get('name', 'Unknown')}): {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk create: {len(created_leagues)} created, {len(errors)} failed"
        )
        return created_leagues, errors
    
    @transaction.atomic
    def bulk_upsert_leagues(
        self,
        leagues_data: List[Dict[str, Any]],
        match_field: str = 'external_id'
    ) -> Tuple[List[League], List[League], List[str]]:
        """
        Bulk create or update leagues based on match_field.
        
        Args:
            leagues_data: List of league data dictionaries
            match_field: Field to use for matching (default: 'external_id')
            
        Returns:
            Tuple of (created_leagues, updated_leagues, error_messages)
        """
        created_leagues = []
        updated_leagues = []
        errors = []
        
        for idx, data in enumerate(leagues_data):
            try:
                match_value = data.get(match_field)
                if not match_value:
                    raise ValueError(f"Missing {match_field} field")
                
                # Check if league exists
                existing_league = League.objects.filter(
                    **{match_field: match_value}
                ).first()
                
                if existing_league:
                    # Update existing league
                    for field, value in data.items():
                        setattr(existing_league, field, value)
                    existing_league.save()
                    updated_leagues.append(existing_league)
                    logger.debug(
                        f"Updated league: {existing_league.name} "
                        f"({existing_league.country.name})"
                    )
                else:
                    # Create new league
                    league = self.create(data)
                    created_leagues.append(league)
                    logger.debug(
                        f"Created league: {league.name} ({league.country.name})"
                    )
                    
            except Exception as e:
                error_msg = (
                    f"League #{idx + 1} ({data.get('name', 'Unknown')}): {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk upsert: {len(created_leagues)} created, "
            f"{len(updated_leagues)} updated, {len(errors)} failed"
        )
        return created_leagues, updated_leagues, errors
    
    def get_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[League, bool]:
        """
        Get existing league or create new one.
        
        Args:
            defaults: Default values for creation
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (League, created_boolean)
        """
        return League.objects.get_or_create(defaults=defaults, **kwargs)
    
    @transaction.atomic
    def update_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[League, bool]:
        """
        Update existing league or create new one.
        
        Args:
            defaults: Values to update/create with
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (League, created_boolean)
        """
        return League.objects.update_or_create(defaults=defaults, **kwargs)
    
    # ==================== League-Specific Operations ====================
    
    def get_by_external_id(self, external_id: str) -> Optional[League]:
        """
        Get league by external API identifier.
        
        Args:
            external_id: External ID (e.g., 'api-football-140')
            
        Returns:
            League object or None if not found
        """
        try:
            return League.objects.select_related('country').get(
                external_id=external_id
            )
        except League.DoesNotExist:
            logger.debug(f"League not found by external_id: {external_id}")
            return None
    
    def get_by_name(self, name: str, exact: bool = True) -> Optional[League]:
        """
        Get league by name.
        
        Args:
            name: League name
            exact: If True, exact match; if False, case-insensitive match
            
        Returns:
            League object or None if not found
        """
        try:
            if exact:
                return League.objects.select_related('country').get(name=name)
            else:
                return League.objects.select_related('country').get(
                    name__iexact=name
                )
        except League.DoesNotExist:
            logger.debug(f"League not found by name: {name}")
            return None
    
    def get_by_country(self, country_id: str) -> QuerySet:
        """
        Get all leagues for a specific country.
        
        Args:
            country_id: Country UUID string
            
        Returns:
            QuerySet of League objects ordered by tier and name
        """
        return League.objects.select_related('country').filter(
            country_id=country_id
        ).order_by('tier', 'name')
    
    def get_by_tier(self, tier: int) -> QuerySet:
        """
        Get all leagues of a specific tier.
        
        Args:
            tier: League tier (1-4)
            
        Returns:
            QuerySet of League objects ordered by country and name
        """
        return League.objects.select_related('country').filter(
            tier=tier
        ).order_by('country__name', 'name')
    
    def get_by_confederation(self, confederation: str) -> QuerySet:
        """
        Get all leagues from a specific confederation.
        
        Args:
            confederation: Confederation code (UEFA, CONMEBOL, AFC, CAF, 
                          CONCACAF, OFC)
            
        Returns:
            QuerySet of League objects ordered by country and tier
        """
        return League.objects.select_related('country').filter(
            confederation=confederation
        ).order_by('country__name', 'tier')
    
    def get_current_leagues(self) -> QuerySet:
        """
        Get all leagues with current active seasons.
        
        Returns:
            QuerySet of League objects with current_season populated
        """
        return League.objects.select_related('country').filter(
            current_season__isnull=False
        ).order_by('country__name', 'tier')
    
    def search_leagues(self, query: str) -> QuerySet:
        """
        Search leagues by name.
        
        Args:
            query: Search term
            
        Returns:
            QuerySet of matching League objects
        """
        return League.objects.select_related('country').filter(
            name__icontains=query
        ).order_by('tier', 'name')
    
    def get_top_leagues(self, limit: int = 20) -> QuerySet:
        """
        Get top-tier leagues (tier 1) from major countries.
        
        This is useful for focusing on the most important leagues for daily
        operations and match predictions.
        
        Args:
            limit: Maximum number of leagues to return
            
        Returns:
            QuerySet of top League objects ordered by country
        """
        return League.objects.select_related('country').filter(
            tier=1
        ).order_by('country__name')[:limit]
    
    # ==================== API Integration ====================
    
    @transaction.atomic
    def fetch_leagues_from_api(
        self,
        league_id: Optional[int] = None,
        current_only: bool = False,
        search: Optional[str] = None,
        country_id: Optional[str] = None,
        season: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch leagues from API-Football and save to database.
        
        This is the main method for populating/syncing league data.
        Recommended usage:
        - Initial population: fetch all leagues (no filters)
        - Seasonal sync: fetch with season parameter
        - Country-specific: fetch with country_id
        - Current leagues only: fetch with current_only=True
        
        Workflow:
        1. Fetch leagues from API-Football
        2. Transform to internal format
        3. Validate data
        4. Upsert to database (create new, update existing)
        
        Args:
            league_id: Optional specific league ID to fetch
            current_only: If True, fetch only leagues with current seasons
            search: Optional search term for league names
            country_id: Optional country UUID to filter by country
            season: Optional year to filter leagues by season
            
        Returns:
            Dictionary with operation statistics:
            {
                'fetched': 800,
                'transformed': 800,
                'saved': 800,
                'created': 600,
                'updated': 200,
                'failed': 0,
                'errors': []
            }
        """
        logger.info(
            f"fetch_leagues_from_api called: "
            f"league_id={league_id}, current={current_only}, "
            f"search={search}, country_id={country_id}, season={season}"
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
            # Convert country_id to country code if provided
            country_code = None
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    country_code = country.code
                    logger.info(
                        f"Filtering by country: {country.name} ({country_code})"
                    )
                except Country.DoesNotExist:
                    error_msg = f"Country not found: {country_id}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    return stats
            
            # Fetch leagues from API-Football
            logger.info("Fetching leagues from API-Football...")
            api_leagues = self.client.get_leagues(
                league_id=league_id,
                current=current_only,
                search=search,
                country=country_code,
                season=season
            )
            
            stats['fetched'] = len(api_leagues)
            logger.info(f"Fetched {stats['fetched']} leagues from API-Football")
            
            if not api_leagues:
                logger.warning("No leagues returned from API")
                return stats
            
            # Transform leagues data
            transformed_leagues = []
            for api_league in api_leagues:
                try:
                    # Transform league data
                    transformed = self.transformer.transform(
                        api_league,
                        provider='api-football'
                    )
                    
                    if transformed:
                        # Resolve country_id from country code
                        country_code = transformed.get('country_code')
                        if country_code:
                            try:
                                country = Country.objects.get(code=country_code)
                                transformed['country_id'] = str(country.id)
                                # Remove country_code as it's not a model field
                                del transformed['country_code']
                                
                                transformed_leagues.append(transformed)
                                stats['transformed'] += 1
                            except Country.DoesNotExist:
                                error_msg = (
                                    f"Country not found for league "
                                    f"{transformed.get('name', 'Unknown')}: "
                                    f"{country_code}"
                                )
                                stats['errors'].append(error_msg)
                                logger.warning(error_msg)
                        else:
                            error_msg = (
                                f"No country_code for league "
                                f"{transformed.get('name', 'Unknown')}"
                            )
                            stats['errors'].append(error_msg)
                            logger.warning(error_msg)
                    else:
                        error_msg = (
                            f"Transform returned None for "
                            f"{api_league.get('league', {}).get('name', 'Unknown')}"
                        )
                        stats['errors'].append(error_msg)
                        logger.warning(error_msg)
                        
                except Exception as e:
                    error_msg = (
                        f"Transform error for "
                        f"{api_league.get('league', {}).get('name', 'Unknown')}: "
                        f"{str(e)}"
                    )
                    stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Transformed {stats['transformed']} leagues")
            
            # Check transformer errors
            if self.transformer.has_errors():
                transformer_errors = self.transformer.get_errors()
                stats['errors'].extend(transformer_errors)
                logger.warning(
                    f"Transformer collected {len(transformer_errors)} errors"
                )
            
            # Save leagues to database (upsert)
            created, updated, save_errors = self.bulk_upsert_leagues(
                transformed_leagues,
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
            error_msg = f"Fatal error in fetch_leagues_from_api: {str(e)}"
            logger.exception(error_msg)
            stats['errors'].append(error_msg)
            raise
