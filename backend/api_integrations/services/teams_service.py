"""
Teams Service

Business logic for managing team data from external APIs and database operations.

This service provides comprehensive team management including:
- CRUD operations on Team model
- Fetching teams from external APIs (Football-Data.org, API-Football)
- Data transformation and validation
- Bulk operations with transaction support
- Country relationship management

Dependencies:
- providers.football_data_org.client: FootballDataClient
- providers.api_football.client: APIFootballClient
- transformers.team_transformer: TeamTransformer
- transformers.validators: TeamValidator
- apps.core.models: Team, Country

Author: Oover Development Team
Date: October 2025
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet, Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from apps.core.models import Team, Country
from api_integrations.providers.football_data_org.client import FootballDataClient
from api_integrations.providers.api_football.client import APIFootballClient
from api_integrations.transformers.team_transformer import TeamTransformer
from api_integrations.transformers.validators import TeamValidator

logger = logging.getLogger(__name__)


class TeamsService:
    """
    Service for managing team data from external APIs and database operations.
    
    This service provides three layers of functionality:
    
    1. Base CRUD Operations (Phase 5.1):
       - get_by_id, list, count, exists
       - create, update, delete
       - bulk_create, bulk_update, bulk_upsert
       - get_or_create, update_or_create
    
    2. Team-Specific Operations (Phase 5.2):
       - get_by_external_id, get_by_country
       - search_teams, get_active_teams
       - activate/deactivate teams
       - Country validation
    
    3. API Integration (Phase 5.3):
       - fetch_teams_from_provider
       - Provider selection (Football-Data.org primary, API-Football fallback)
       - Transform + Validate + Save pipeline
       - Error handling and statistics
    
    Example Usage:
        >>> service = TeamsService()
        >>> 
        >>> # Fetch teams from API
        >>> result = service.fetch_teams_from_provider(
        ...     provider='football-data',
        ...     competition_id='PL'
        ... )
        >>> print(f"Saved {result['saved']} teams")
        >>> 
        >>> # Get team by external ID
        >>> team = service.get_by_external_id('football-data-33')
        >>> 
        >>> # Search teams
        >>> teams = service.search_teams('Manchester')
        >>> 
        >>> # Bulk upsert
        >>> team_data = [
        ...     {'name': 'Team A', 'code': 'TEA', 'country_id': country.id},
        ...     {'name': 'Team B', 'code': 'TEB', 'country_id': country.id}
        ... ]
        >>> created, updated = service.bulk_upsert_teams(team_data)
    """
    
    def __init__(self):
        """Initialize teams service with providers and transformers."""
        self.primary_provider = FootballDataClient()
        self.fallback_provider = APIFootballClient()
        self.transformer = TeamTransformer()
        self.validator = TeamValidator()
        logger.info("Initialized TeamsService with providers and transformers")
    
    # ================================================================
    # PHASE 5.1: BASE CRUD OPERATIONS
    # ================================================================
    
    def get_by_id(self, team_id: str) -> Optional[Team]:
        """
        Get team by ID.
        
        Args:
            team_id: Team primary key (text UUID)
        
        Returns:
            Team object if found, None otherwise
        
        Example:
            >>> team = service.get_by_id('550e8400-e29b-41d4-a716-446655440000')
        """
        try:
            return Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            logger.warning(f"Team not found: {team_id}")
            return None
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QuerySet:
        """
        List teams with optional filtering, ordering, and pagination.
        
        Args:
            filters: Django ORM filter kwargs (e.g., {'is_active': True})
            order_by: List of fields to order by (e.g., ['name', '-created_at'])
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            QuerySet of Team objects
        
        Example:
            >>> teams = service.list(
            ...     filters={'is_active': True, 'country__code': 'GB'},
            ...     order_by=['name'],
            ...     limit=20
            ... )
        """
        queryset = Team.objects.all()
        
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
        Count teams with optional filtering.
        
        Args:
            filters: Django ORM filter kwargs
        
        Returns:
            Number of teams matching filters
        
        Example:
            >>> count = service.count({'is_active': True})
        """
        queryset = Team.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if team exists with given filters.
        
        Args:
            filters: Django ORM filter kwargs
        
        Returns:
            True if team exists, False otherwise
        
        Example:
            >>> exists = service.exists({'external_id': 'football-data-33'})
        """
        return Team.objects.filter(**filters).exists()
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> Team:
        """
        Create a new team with validation.
        
        Args:
            data: Team data dictionary
        
        Returns:
            Created Team object
        
        Raises:
            ValidationError: If validation fails
        
        Example:
            >>> team = service.create({
            ...     'name': 'Manchester United',
            ...     'code': 'MUN',
            ...     'country_id': country.id,
            ...     'logo': 'https://...'
            ... })
        """
        # Validate data
        validation_errors = self.validator.validate(data)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Team validation failed: {error_msg}")
            raise ValidationError(error_msg)
        
        # Create team
        team = Team.objects.create(**data)
        logger.info(f"Created team: {team.name} (ID: {team.id})")
        return team
    
    @transaction.atomic
    def update(self, team_id: str, data: Dict[str, Any]) -> Optional[Team]:
        """
        Update team by ID with validation.
        
        Args:
            team_id: Team primary key
            data: Fields to update
        
        Returns:
            Updated Team object if found, None otherwise
        
        Raises:
            ValidationError: If validation fails
        
        Example:
            >>> team = service.update(
            ...     '550e8400-e29b-41d4-a716-446655440000',
            ...     {'market_value': 1500000000}
            ... )
        """
        team = self.get_by_id(team_id)
        if not team:
            return None
        
        # Validate update data
        validation_errors = self.validator.validate(data, partial=True)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Team update validation failed: {error_msg}")
            raise ValidationError(error_msg)
        
        # Update fields
        for field, value in data.items():
            setattr(team, field, value)
        
        team.save()
        logger.info(f"Updated team: {team.name} (ID: {team.id})")
        return team
    
    @transaction.atomic
    def delete(self, team_id: str) -> bool:
        """
        Delete team by ID.
        
        Args:
            team_id: Team primary key
        
        Returns:
            True if deleted, False if not found
        
        Example:
            >>> deleted = service.delete('550e8400-e29b-41d4-a716-446655440000')
        """
        team = self.get_by_id(team_id)
        if not team:
            return False
        
        team_name = team.name
        team.delete()
        logger.info(f"Deleted team: {team_name} (ID: {team_id})")
        return True
    
    @transaction.atomic
    def bulk_create(self, teams_data: List[Dict[str, Any]]) -> Tuple[List[Team], List[str]]:
        """
        Create multiple teams with validation.
        
        Args:
            teams_data: List of team data dictionaries
        
        Returns:
            Tuple of (created teams, error messages)
        
        Example:
            >>> data = [
            ...     {'name': 'Team A', 'code': 'TEA', 'country_id': country.id},
            ...     {'name': 'Team B', 'code': 'TEB', 'country_id': country.id}
            ... ]
            >>> teams, errors = service.bulk_create(data)
        """
        created_teams = []
        errors = []
        
        for idx, data in enumerate(teams_data):
            try:
                team = self.create(data)
                created_teams.append(team)
            except Exception as e:
                error_msg = f"Team #{idx + 1} ({data.get('name', 'Unknown')}): {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Bulk create: {len(created_teams)} created, {len(errors)} failed")
        return created_teams, errors
    
    @transaction.atomic
    def bulk_upsert_teams(
        self,
        teams_data: List[Dict[str, Any]],
        match_field: str = 'external_id'
    ) -> Tuple[List[Team], List[Team], List[str]]:
        """
        Create or update multiple teams (smart merge).
        
        Args:
            teams_data: List of team data dictionaries
            match_field: Field to match existing teams (default: 'external_id')
        
        Returns:
            Tuple of (created teams, updated teams, error messages)
        
        Example:
            >>> teams_data = [
            ...     {
            ...         'external_id': 'football-data-33',
            ...         'name': 'Manchester United',
            ...         'code': 'MUN',
            ...         'country_id': country.id
            ...     }
            ... ]
            >>> created, updated, errors = service.bulk_upsert_teams(teams_data)
        """
        created_teams = []
        updated_teams = []
        errors = []
        
        for idx, data in enumerate(teams_data):
            try:
                match_value = data.get(match_field)
                if not match_value:
                    raise ValueError(f"Missing {match_field} field")
                
                # Try to find existing team
                existing_team = Team.objects.filter(**{match_field: match_value}).first()
                
                if existing_team:
                    # Update existing team
                    for field, value in data.items():
                        setattr(existing_team, field, value)
                    existing_team.save()
                    updated_teams.append(existing_team)
                    logger.debug(f"Updated team: {existing_team.name}")
                else:
                    # Create new team
                    team = self.create(data)
                    created_teams.append(team)
                    logger.debug(f"Created team: {team.name}")
            
            except Exception as e:
                error_msg = f"Team #{idx + 1} ({data.get('name', 'Unknown')}): {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk upsert: {len(created_teams)} created, "
            f"{len(updated_teams)} updated, {len(errors)} failed"
        )
        return created_teams, updated_teams, errors
    
    def get_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[Team, bool]:
        """
        Get existing team or create new one.
        
        Args:
            defaults: Fields to set on creation
            **kwargs: Fields to match existing team
        
        Returns:
            Tuple of (team, created boolean)
        
        Example:
            >>> team, created = service.get_or_create(
            ...     external_id='football-data-33',
            ...     defaults={'name': 'Manchester United', 'code': 'MUN'}
            ... )
        """
        return Team.objects.get_or_create(defaults=defaults, **kwargs)
    
    @transaction.atomic
    def update_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[Team, bool]:
        """
        Update existing team or create new one.
        
        Args:
            defaults: Fields to update/set
            **kwargs: Fields to match existing team
        
        Returns:
            Tuple of (team, created boolean)
        
        Example:
            >>> team, created = service.update_or_create(
            ...     external_id='football-data-33',
            ...     defaults={'name': 'Manchester United', 'code': 'MUN'}
            ... )
        """
        return Team.objects.update_or_create(defaults=defaults, **kwargs)
    
    # ================================================================
    # PHASE 5.2: TEAM-SPECIFIC OPERATIONS
    # ================================================================
    
    def get_by_external_id(self, external_id: str) -> Optional[Team]:
        """
        Get team by external provider ID.
        
        Args:
            external_id: External API identifier (e.g., 'football-data-33')
        
        Returns:
            Team object if found, None otherwise
        
        Example:
            >>> team = service.get_by_external_id('football-data-33')
        """
        try:
            return Team.objects.get(external_id=external_id)
        except Team.DoesNotExist:
            logger.debug(f"Team not found by external_id: {external_id}")
            return None
    
    def get_or_create_by_external_id(
        self,
        external_id: str,
        defaults: Dict[str, Any]
    ) -> Tuple[Team, bool]:
        """
        Get team by external_id or create new one (smart duplicate detection).
        
        Args:
            external_id: External API identifier
            defaults: Fields to set on creation
        
        Returns:
            Tuple of (team, created boolean)
        
        Example:
            >>> team, created = service.get_or_create_by_external_id(
            ...     'football-data-33',
            ...     {'name': 'Manchester United', 'code': 'MUN'}
            ... )
        """
        return self.get_or_create(external_id=external_id, defaults=defaults)
    
    def get_by_country(
        self,
        country_id: UUID,
        is_active: Optional[bool] = None
    ) -> QuerySet:
        """
        Get teams by country.
        
        Args:
            country_id: Country UUID
            is_active: Optional filter by active status
        
        Returns:
            QuerySet of Team objects
        
        Example:
            >>> teams = service.get_by_country(country.id, is_active=True)
        """
        filters = {'country_id': country_id}
        if is_active is not None:
            filters['is_active'] = is_active
        
        return Team.objects.filter(**filters)
    
    def search_teams(self, query: str, is_active: Optional[bool] = None) -> QuerySet:
        """
        Search teams by name or code.
        
        Args:
            query: Search string (case-insensitive)
            is_active: Optional filter by active status
        
        Returns:
            QuerySet of Team objects
        
        Example:
            >>> teams = service.search_teams('Manchester', is_active=True)
        """
        filters = Q(name__icontains=query) | Q(code__icontains=query)
        
        if is_active is not None:
            filters &= Q(is_active=is_active)
        
        return Team.objects.filter(filters)
    
    def get_active_teams(self, country_id: Optional[UUID] = None) -> QuerySet:
        """
        Get active teams with optional country filter.
        
        Args:
            country_id: Optional country UUID filter
        
        Returns:
            QuerySet of active Team objects
        
        Example:
            >>> teams = service.get_active_teams(country_id=country.id)
        """
        filters = {'is_active': True}
        if country_id:
            filters['country_id'] = country_id
        
        return Team.objects.filter(**filters)
    
    @transaction.atomic
    def deactivate_team(self, team_id: str) -> bool:
        """
        Deactivate team (soft delete).
        
        Args:
            team_id: Team primary key
        
        Returns:
            True if deactivated, False if not found
        
        Example:
            >>> deactivated = service.deactivate_team('550e8400-e29b-41d4-a716-446655440000')
        """
        team = self.get_by_id(team_id)
        if not team:
            return False
        
        team.is_active = False
        team.save()
        logger.info(f"Deactivated team: {team.name} (ID: {team_id})")
        return True
    
    @transaction.atomic
    def activate_team(self, team_id: str) -> bool:
        """
        Activate team.
        
        Args:
            team_id: Team primary key
        
        Returns:
            True if activated, False if not found
        
        Example:
            >>> activated = service.activate_team('550e8400-e29b-41d4-a716-446655440000')
        """
        team = self.get_by_id(team_id)
        if not team:
            return False
        
        team.is_active = True
        team.save()
        logger.info(f"Activated team: {team.name} (ID: {team_id})")
        return True
    
    def validate_country_exists(self, country_id: UUID) -> bool:
        """
        Validate that country exists.
        
        Args:
            country_id: Country UUID
        
        Returns:
            True if country exists, False otherwise
        
        Example:
            >>> valid = service.validate_country_exists(country.id)
        """
        try:
            Country.objects.get(id=country_id)
            return True
        except Country.DoesNotExist:
            logger.warning(f"Country not found: {country_id}")
            return False
    
    # ================================================================
    # PHASE 5.3: API INTEGRATION LAYER
    # ================================================================
    
    @transaction.atomic
    def fetch_teams_from_provider(
        self,
        provider: str = 'football-data',
        competition_id: Optional[str] = None,
        country_code: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch teams from external API provider with Transform + Validate + Save pipeline.
        
        This method:
        1. Selects the appropriate provider (Football-Data.org or API-Football)
        2. Fetches teams data from the API
        3. Transforms API response to Team model format
        4. Validates transformed data
        5. Saves valid teams to database (create or update)
        6. Returns statistics and errors
        
        Args:
            provider: 'football-data' (primary) or 'api-football' (fallback)
            competition_id: Competition/League ID (provider-specific)
                - Football-Data.org: 'PL' (Premier League), 'PD' (La Liga), etc.
                - API-Football: '39' (Premier League), '140' (La Liga), etc.
            country_code: Country code filter (e.g., 'GB', 'ES')
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Dictionary with statistics:
            {
                'provider': 'football-data',
                'fetched': 20,           # Teams fetched from API
                'transformed': 20,       # Successfully transformed
                'validated': 18,         # Passed validation
                'saved': 18,             # Saved to database
                'created': 5,            # Newly created
                'updated': 13,           # Updated existing
                'failed': 2,             # Failed to save
                'errors': [...]          # List of error messages
            }
        
        Raises:
            ValueError: If provider is invalid or required parameters missing
            Exception: If API request fails or transaction rollback needed
        
        Examples:
            >>> # Fetch Premier League teams from Football-Data.org
            >>> result = service.fetch_teams_from_provider(
            ...     provider='football-data',
            ...     competition_id='PL'
            ... )
            >>> print(f"Saved {result['saved']} teams ({result['created']} new)")
            >>> 
            >>> # Fetch teams from API-Football (fallback)
            >>> result = service.fetch_teams_from_provider(
            ...     provider='api-football',
            ...     competition_id='39',  # Premier League
            ...     season=2024
            ... )
            >>> 
            >>> # Handle errors
            >>> if result['errors']:
            ...     for error in result['errors']:
            ...         print(f"Error: {error}")
        """
        logger.info(
            f"fetch_teams_from_provider called: provider={provider}, "
            f"competition_id={competition_id}, country_code={country_code}"
        )
        
        # Initialize statistics
        stats = {
            'provider': provider,
            'fetched': 0,
            'transformed': 0,
            'validated': 0,
            'saved': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Step 1: Select provider and fetch teams
            if provider == 'football-data':
                if not competition_id:
                    raise ValueError("competition_id required for football-data provider")
                
                logger.info(f"Fetching teams from Football-Data.org: {competition_id}")
                api_teams = self.primary_provider.get_teams_by_competition(
                    competition_id=competition_id,
                    **kwargs
                )
            
            elif provider == 'api-football':
                if not competition_id:
                    raise ValueError("competition_id required for api-football provider")
                
                logger.info(f"Fetching teams from API-Football: {competition_id}")
                api_teams = self.fallback_provider.get_teams_by_league(
                    league_id=competition_id,
                    **kwargs
                )
            
            else:
                raise ValueError(f"Invalid provider: {provider}. Use 'football-data' or 'api-football'")
            
            stats['fetched'] = len(api_teams)
            logger.info(f"Fetched {stats['fetched']} teams from {provider}")
            
            if not api_teams:
                logger.warning(f"No teams returned from {provider}")
                return stats
            
            # Step 2: Transform API responses to Team model format
            transformed_teams = []
            for api_team in api_teams:
                try:
                    transformed = self.transformer.transform(api_team, provider=provider)
                    if transformed:
                        transformed_teams.append(transformed)
                        stats['transformed'] += 1
                except Exception as e:
                    error_msg = f"Transform error for {api_team.get('name', 'Unknown')}: {str(e)}"
                    stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Transformed {stats['transformed']} teams")
            
            # Step 3: Validate transformed data
            validated_teams = []
            for team_data in transformed_teams:
                validation_errors = self.validator.validate(team_data)
                if validation_errors:
                    error_msg = (
                        f"Validation failed for {team_data.get('name', 'Unknown')}: "
                        f"{'; '.join(validation_errors)}"
                    )
                    stats['errors'].append(error_msg)
                    logger.warning(error_msg)
                else:
                    validated_teams.append(team_data)
                    stats['validated'] += 1
            
            logger.info(f"Validated {stats['validated']} teams")
            
            # Step 4: Save teams to database (bulk upsert)
            created, updated, save_errors = self.bulk_upsert_teams(
                validated_teams,
                match_field='external_id'
            )
            
            stats['created'] = len(created)
            stats['updated'] = len(updated)
            stats['saved'] = stats['created'] + stats['updated']
            stats['failed'] = len(save_errors)
            stats['errors'].extend(save_errors)
            
            # Log final statistics
            logger.info(
                f"Fetch complete: {stats['fetched']} fetched, "
                f"{stats['saved']} saved ({stats['created']} new, {stats['updated']} updated), "
                f"{stats['failed']} failed"
            )
            
            if stats['errors']:
                logger.warning(f"Encountered {len(stats['errors'])} errors during fetch")
            
            return stats
        
        except Exception as e:
            error_msg = f"Fatal error in fetch_teams_from_provider: {str(e)}"
            logger.exception(error_msg)
            stats['errors'].append(error_msg)
            # Re-raise to trigger transaction rollback
            raise
    
    def sync_teams(
        self,
        provider: str = 'football-data',
        competition_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Periodic sync of team data (Phase 5.4 placeholder).
        
        This will be implemented in Phase 5.4 with:
        - Incremental updates (only changed data)
        - Activity status management
        - Detailed statistics and logging
        
        Args:
            provider: API provider to sync from
            competition_id: Competition/League ID
            **kwargs: Additional parameters
        
        Returns:
            Sync statistics dictionary
        
        Note:
            Currently calls fetch_teams_from_provider.
            Will be enhanced in Phase 5.4.
        """
        logger.info("sync_teams called (currently uses fetch_teams_from_provider)")
        return self.fetch_teams_from_provider(
            provider=provider,
            competition_id=competition_id,
            **kwargs
        )
