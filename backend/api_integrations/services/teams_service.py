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
from django.conf import settings

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
        """
        Initialize teams service with API providers and transformers.
        
        Retrieves API keys from Django settings and initializes:
        - Football-Data.org client (primary provider)
        - API-Football client (fallback provider)
        - Team data transformer
        - Team data validator
        
        Raises:
            ValueError: If FOOTBALL_DATA_API_KEY is not configured
        """
        # Get API key from Django settings
        api_key = settings.FOOTBALL_DATA_CONFIG.get('API_KEY')
        if not api_key:
            error_msg = (
                "FOOTBALL_DATA_API_KEY not configured. "
                "Please set FOOTBALL_DATA_API_KEY in your .env file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize providers with API keys
        self.primary_provider = FootballDataClient(api_key=api_key)
        
        # API-Football may not be configured yet (fallback provider)
        try:
            api_football_key = settings.API_FOOTBALL_CONFIG.get('API_KEY')
            if api_football_key:
                self.fallback_provider = APIFootballClient(api_key=api_football_key)
            else:
                self.fallback_provider = None
                logger.warning("API-Football not configured, fallback provider unavailable")
        except Exception as e:
            self.fallback_provider = None
            logger.warning(f"Failed to initialize API-Football client: {e}")
        
        # Initialize transformers and validators
        self.transformer = TeamTransformer()
        self.validator = TeamValidator()
        
        logger.info("Initialized TeamsService with providers and transformers")
    
    # [Methods remain exactly the same until fetch_teams_from_provider...]
    
    def get_by_id(self, team_id: str) -> Optional[Team]:
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
        queryset = Team.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        return Team.objects.filter(**filters).exists()
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> Team:
        is_valid, validation_errors = self.validator.validate(data)
        if not is_valid:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Team validation failed: {error_msg}")
            raise ValidationError(error_msg)
        team = Team.objects.create(**data)
        logger.info(f"Created team: {team.name} (ID: {team.id})")
        return team
    
    @transaction.atomic
    def update(self, team_id: str, data: Dict[str, Any]) -> Optional[Team]:
        team = self.get_by_id(team_id)
        if not team:
            return None
        is_valid, validation_errors = self.validator.validate(data)
        if not is_valid:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Team update validation failed: {error_msg}")
            raise ValidationError(error_msg)
        for field, value in data.items():
            setattr(team, field, value)
        team.save()
        logger.info(f"Updated team: {team.name} (ID: {team.id})")
        return team
    
    @transaction.atomic
    def delete(self, team_id: str) -> bool:
        team = self.get_by_id(team_id)
        if not team:
            return False
        team_name = team.name
        team.delete()
        logger.info(f"Deleted team: {team_name} (ID: {team_id})")
        return True
    
    @transaction.atomic
    def bulk_create(self, teams_data: List[Dict[str, Any]]) -> Tuple[List[Team], List[str]]:
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
        created_teams = []
        updated_teams = []
        errors = []
        for idx, data in enumerate(teams_data):
            try:
                match_value = data.get(match_field)
                if not match_value:
                    raise ValueError(f"Missing {match_field} field")
                existing_team = Team.objects.filter(**{match_field: match_value}).first()
                if existing_team:
                    for field, value in data.items():
                        setattr(existing_team, field, value)
                    existing_team.save()
                    updated_teams.append(existing_team)
                    logger.debug(f"Updated team: {existing_team.name}")
                else:
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
        return Team.objects.get_or_create(defaults=defaults, **kwargs)
    
    @transaction.atomic
    def update_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[Team, bool]:
        return Team.objects.update_or_create(defaults=defaults, **kwargs)
    
    def get_by_external_id(self, external_id: str) -> Optional[Team]:
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
        return self.get_or_create(external_id=external_id, defaults=defaults)
    
    def get_by_country(
        self,
        country_id: UUID,
        is_active: Optional[bool] = None
    ) -> QuerySet:
        filters = {'country_id': country_id}
        if is_active is not None:
            filters['is_active'] = is_active
        return Team.objects.filter(**filters)
    
    def search_teams(self, query: str, is_active: Optional[bool] = None) -> QuerySet:
        filters = Q(name__icontains=query) | Q(code__icontains=query)
        if is_active is not None:
            filters &= Q(is_active=is_active)
        return Team.objects.filter(filters)
    
    def get_active_teams(self, country_id: Optional[UUID] = None) -> QuerySet:
        filters = {'is_active': True}
        if country_id:
            filters['country_id'] = country_id
        return Team.objects.filter(**filters)
    
    @transaction.atomic
    def deactivate_team(self, team_id: str) -> bool:
        team = self.get_by_id(team_id)
        if not team:
            return False
        team.is_active = False
        team.save()
        logger.info(f"Deactivated team: {team.name} (ID: {team_id})")
        return True
    
    @transaction.atomic
    def activate_team(self, team_id: str) -> bool:
        team = self.get_by_id(team_id)
        if not team:
            return False
        team.is_active = True
        team.save()
        logger.info(f"Activated team: {team.name} (ID: {team_id})")
        return True
    
    def validate_country_exists(self, country_id: UUID) -> bool:
        try:
            Country.objects.get(id=country_id)
            return True
        except Country.DoesNotExist:
            logger.warning(f"Country not found: {country_id}")
            return False
    
    @transaction.atomic
    def fetch_teams_from_provider(
        self,
        provider: str = 'football-data',
        competition_id: Optional[str] = None,
        country_code: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Fetch teams from external API provider.
        
        Args:
            provider: Provider name ('football-data' or 'api-football')
            competition_id: Competition code (e.g., 'PL' for Premier League)
            country_code: Country code for filtering (optional)
            limit: Maximum number of teams to process (applied after fetch)
        
        Returns:
            Dictionary with statistics about the fetch operation
        """
        logger.info(
            f"fetch_teams_from_provider called: provider={provider}, "
            f"competition_id={competition_id}, country_code={country_code}, limit={limit}"
        )
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
            # Fetch teams from provider
            if provider == 'football-data':
                if not competition_id:
                    raise ValueError("competition_id required for football-data provider")
                logger.info(f"Fetching teams from Football-Data.org: {competition_id}")
                
                # Football-Data.org client doesn't accept extra parameters
                # Fetch all teams and limit after
                api_teams = self.primary_provider.get_teams_by_competition(
                    competition_id=competition_id
                )
                
            elif provider == 'api-football':
                if not competition_id:
                    raise ValueError("competition_id required for api-football provider")
                if not self.fallback_provider:
                    raise ValueError("API-Football provider not configured")
                logger.info(f"Fetching teams from API-Football: {competition_id}")
                
                # API-Football client  - pass competition_id as league_id
                api_teams = self.fallback_provider.get_teams_by_league(
                    league_id=competition_id
                )
                
            else:
                raise ValueError(f"Invalid provider: {provider}")
            
            # Apply limit if specified (after fetch, since clients don't support limit)
            if limit and limit > 0:
                api_teams = api_teams[:limit]
                logger.info(f"Limited results to {limit} teams")
            
            stats['fetched'] = len(api_teams)
            logger.info(f"Fetched {stats['fetched']} teams from {provider}")
            
            if not api_teams:
                logger.warning(f"No teams returned from {provider}")
                return stats
            
            # Transform teams data
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
            
            # Validate teams data
            validated_teams = []
            for team_data in transformed_teams:
                is_valid, validation_errors = self.validator.validate(team_data)
                if not is_valid:
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
            
            # Save teams to database (upsert)
            created, updated, save_errors = self.bulk_upsert_teams(
                validated_teams,
                match_field='external_id'
            )
            
            stats['created'] = len(created)
            stats['updated'] = len(updated)
            stats['saved'] = stats['created'] + stats['updated']
            stats['failed'] = len(save_errors)
            stats['errors'].extend(save_errors)
            
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
            raise
    
    def sync_teams(
        self,
        provider: str = 'football-data',
        competition_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Sync teams data from external provider.
        
        Currently uses fetch_teams_from_provider internally.
        Future implementation will add intelligent sync logic.
        """
        logger.info("sync_teams called (currently uses fetch_teams_from_provider)")
        return self.fetch_teams_from_provider(
            provider=provider,
            competition_id=competition_id,
            **kwargs
        )
