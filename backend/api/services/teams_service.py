"""
Teams Service - Core business logic for team management

This module provides the TeamsService class that handles all team-related
operations including CRUD, duplicate detection, bulk operations, and
country relationship management.

Example Usage:
    from api.services.teams_service import TeamsService
    from api.models import Team
    
    # Initialize service
    teams_service = TeamsService()
    
    # Get team by ID
    team = teams_service.get_by_id(team_id)
    
    # Get or create by external_id
    team, created = teams_service.get_or_create_by_external_id(
        external_id="football-data-12345",
        defaults={
            'name': 'Arsenal FC',
            'code': 'ARS',
            'country_id': country.id
        }
    )
    
    # Bulk upsert teams
    results = teams_service.bulk_upsert_teams(teams_data)
    
    # Sync teams from API
    sync_results = teams_service.sync_teams(
        provider='football-data',
        competition_id='PL',
        deactivate_missing=False
    )
"""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, QuerySet

from api.models import Team, Country
from .base import BaseAPIService

logger = logging.getLogger(__name__)


class TeamsService(BaseAPIService[Team]):
    """
    Service class for Team model operations.
    
    Provides CRUD operations, duplicate detection, bulk operations,
    and country relationship management for teams.
    
    Attributes:
        model: Team model class
    """
    
    model = Team
    
    def get_by_external_id(self, external_id: str) -> Optional[Team]:
        """
        Get team by external_id.
        
        Args:
            external_id: External provider ID (format: provider-api_id)
            
        Returns:
            Team object if found, None otherwise
            
        Example:
            >>> team = teams_service.get_by_external_id("football-data-12345")
            >>> if team:
            >>>     print(f"Found team: {team.name}")
        """
        try:
            return self.get_by_field(external_id=external_id)
        except Team.DoesNotExist:
            logger.debug(f"Team not found with external_id: {external_id}")
            return None
    
    def get_or_create_by_external_id(
        self,
        external_id: str,
        defaults: Optional[Dict] = None
    ) -> Tuple[Team, bool]:
        """
        Get existing team by external_id or create new one.
        
        This method is the primary way to handle team data from external APIs.
        It prevents duplicates while ensuring all teams are properly created.
        
        Args:
            external_id: External provider ID (format: provider-api_id)
            defaults: Default values if team needs to be created
            
        Returns:
            Tuple of (Team object, created boolean)
            
        Raises:
            ValidationError: If defaults are invalid
            
        Example:
            >>> team, created = teams_service.get_or_create_by_external_id(
            >>>     external_id="football-data-12345",
            >>>     defaults={
            >>>         'name': 'Arsenal FC',
            >>>         'code': 'ARS',
            >>>         'country_id': country_id
            >>>     }
            >>> )
            >>> if created:
            >>>     print(f"Created new team: {team.name}")
            >>> else:
            >>>     print(f"Found existing team: {team.name}")
        """
        defaults = defaults or {}
        
        try:
            # Try to get existing team
            team = self.get_by_external_id(external_id)
            if team:
                logger.info(f"Found existing team: {team.name} ({external_id})")
                return team, False
            
            # Create new team
            defaults['external_id'] = external_id
            team = self.create(defaults)
            logger.info(f"Created new team: {team.name} ({external_id})")
            return team, True
            
        except ValidationError as e:
            logger.error(f"Validation error for external_id {external_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_or_create_by_external_id for {external_id}: {e}")
            raise
    
    def get_by_country(
        self,
        country_id: UUID,
        is_active: Optional[bool] = None
    ) -> QuerySet[Team]:
        """
        Get teams by country.
        
        Args:
            country_id: Country UUID
            is_active: Filter by active status (None = all teams)
            
        Returns:
            QuerySet of teams
            
        Example:
            >>> # Get all active teams in England
            >>> teams = teams_service.get_by_country(
            >>>     country_id=england.id,
            >>>     is_active=True
            >>> )
        """
        filters = {'country_id': country_id}
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.list(filters=filters)
    
    def search_teams(
        self,
        query: str,
        is_active: Optional[bool] = None
    ) -> QuerySet[Team]:
        """
        Search teams by name or code.
        
        Args:
            query: Search string (searches name and code)
            is_active: Filter by active status (None = all teams)
            
        Returns:
            QuerySet of matching teams
            
        Example:
            >>> # Search for Arsenal
            >>> teams = teams_service.search_teams(
            >>>     query="Arsenal",
            >>>     is_active=True
            >>> )
        """
        q_filter = Q(name__icontains=query) | Q(code__icontains=query)
        
        if is_active is not None:
            q_filter &= Q(is_active=is_active)
        
        queryset = Team.objects.filter(q_filter)
        logger.info(f"Found {queryset.count()} teams matching '{query}'")
        return queryset
    
    def get_active_teams(self, country_id: Optional[UUID] = None) -> QuerySet[Team]:
        """
        Get all active teams, optionally filtered by country.
        
        Args:
            country_id: Optional country UUID to filter by
            
        Returns:
            QuerySet of active teams
            
        Example:
            >>> # Get all active teams
            >>> teams = teams_service.get_active_teams()
            >>> 
            >>> # Get active teams in England
            >>> teams = teams_service.get_active_teams(country_id=england.id)
        """
        filters = {'is_active': True}
        if country_id:
            filters['country_id'] = country_id
        
        return self.list(filters=filters)
    
    def deactivate_team(self, team_id: UUID) -> Team:
        """
        Deactivate a team (soft delete).
        
        Args:
            team_id: Team UUID
            
        Returns:
            Updated team object
            
        Example:
            >>> team = teams_service.deactivate_team(team_id)
            >>> assert team.is_active == False
        """
        team = self.update(team_id, {'is_active': False})
        logger.info(f"Deactivated team: {team.name} ({team_id})")
        return team
    
    def activate_team(self, team_id: UUID) -> Team:
        """
        Activate a team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Updated team object
            
        Example:
            >>> team = teams_service.activate_team(team_id)
            >>> assert team.is_active == True
        """
        team = self.update(team_id, {'is_active': True})
        logger.info(f"Activated team: {team.name} ({team_id})")
        return team
    
    @transaction.atomic
    def bulk_create_teams(
        self,
        teams_data: List[Dict],
        batch_size: int = 100
    ) -> Dict[str, any]:
        """
        Bulk create teams with error handling.
        
        Args:
            teams_data: List of team data dictionaries
            batch_size: Number of teams per batch
            
        Returns:
            Dictionary with success count, errors, and created teams
            
        Example:
            >>> teams_data = [
            >>>     {
            >>>         'external_id': 'football-data-12345',
            >>>         'name': 'Arsenal FC',
            >>>         'code': 'ARS',
            >>>         'country_id': country_id
            >>>     },
            >>>     # ... more teams
            >>> ]
            >>> results = teams_service.bulk_create_teams(teams_data)
            >>> print(f"Created {results['success_count']} teams")
            >>> if results['errors']:
            >>>     print(f"Errors: {results['errors']}")
        """
        created_teams = []
        errors = []
        
        try:
            for i in range(0, len(teams_data), batch_size):
                batch = teams_data[i:i + batch_size]
                
                # Create team objects
                team_objects = []
                for data in batch:
                    try:
                        team = Team(**data)
                        team.full_clean()  # Validate
                        team_objects.append(team)
                    except Exception as e:
                        errors.append({
                            'data': data,
                            'error': str(e)
                        })
                
                # Bulk create
                if team_objects:
                    created = Team.objects.bulk_create(
                        team_objects,
                        ignore_conflicts=False
                    )
                    created_teams.extend(created)
            
            result = {
                'success_count': len(created_teams),
                'error_count': len(errors),
                'teams': created_teams,
                'errors': errors
            }
            
            logger.info(
                f"Bulk created {len(created_teams)} teams "
                f"with {len(errors)} errors"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk_create_teams: {e}")
            raise
    
    @transaction.atomic
    def bulk_upsert_teams(
        self,
        teams_data: List[Dict],
        batch_size: int = 100
    ) -> Dict[str, any]:
        """
        Bulk upsert teams (update existing, create new).
        
        This method uses external_id to determine if a team exists.
        Existing teams are updated, new teams are created.
        
        Args:
            teams_data: List of team data dictionaries (must include external_id)
            batch_size: Number of teams per batch
            
        Returns:
            Dictionary with created_count, updated_count, errors, and teams
            
        Example:
            >>> teams_data = [
            >>>     {
            >>>         'external_id': 'football-data-12345',
            >>>         'name': 'Arsenal FC',
            >>>         'code': 'ARS',
            >>>         'country_id': country_id
            >>>     },
            >>>     # ... more teams
            >>> ]
            >>> results = teams_service.bulk_upsert_teams(teams_data)
            >>> print(f"Created: {results['created_count']}, "
            >>>       f"Updated: {results['updated_count']}")
        """
        created_teams = []
        updated_teams = []
        errors = []
        
        try:
            for i in range(0, len(teams_data), batch_size):
                batch = teams_data[i:i + batch_size]
                
                for data in batch:
                    try:
                        external_id = data.get('external_id')
                        if not external_id:
                            errors.append({
                                'data': data,
                                'error': 'external_id is required'
                            })
                            continue
                        
                        # Try to get existing team
                        existing_team = self.get_by_external_id(external_id)
                        
                        if existing_team:
                            # Update existing
                            updated_team = self.update(
                                existing_team.id,
                                data
                            )
                            updated_teams.append(updated_team)
                        else:
                            # Create new
                            created_team = self.create(data)
                            created_teams.append(created_team)
                            
                    except Exception as e:
                        errors.append({
                            'data': data,
                            'error': str(e)
                        })
            
            result = {
                'created_count': len(created_teams),
                'updated_count': len(updated_teams),
                'error_count': len(errors),
                'created_teams': created_teams,
                'updated_teams': updated_teams,
                'errors': errors
            }
            
            logger.info(
                f"Bulk upsert completed: "
                f"{len(created_teams)} created, "
                f"{len(updated_teams)} updated, "
                f"{len(errors)} errors"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk_upsert_teams: {e}")
            raise
    
    def validate_country_exists(self, country_id: UUID) -> bool:
        """
        Validate that a country exists.
        
        Args:
            country_id: Country UUID
            
        Returns:
            True if country exists, False otherwise
            
        Example:
            >>> if teams_service.validate_country_exists(country_id):
            >>>     # Create team
            >>>     pass
        """
        return Country.objects.filter(id=country_id).exists()
    
    @transaction.atomic
    def sync_teams(
        self,
        provider: str,
        competition_id: Optional[str] = None,
        league_id: Optional[int] = None,
        deactivate_missing: bool = False
    ) -> Dict[str, any]:
        """
        Sync teams from external API (periodic update).
        
        This method fetches teams from the specified provider and:
        1. Updates existing teams with latest data
        2. Creates new teams that don't exist
        3. Optionally deactivates teams not returned by API
        
        Args:
            provider: API provider name ('football-data' or 'api-football')
            competition_id: Competition ID for Football-Data.org
            league_id: League ID for API-Football
            deactivate_missing: If True, deactivate teams not in API response
            
        Returns:
            Dictionary with sync statistics:
                - fetched: Number of teams fetched from API
                - created: Number of new teams created
                - updated: Number of existing teams updated
                - deactivated: Number of teams deactivated
                - errors: List of errors encountered
                
        Raises:
            ValueError: If provider parameters are invalid
            Exception: If API fetch or sync fails
            
        Example:
            >>> # Sync Premier League teams from Football-Data
            >>> results = teams_service.sync_teams(
            >>>     provider='football-data',
            >>>     competition_id='PL',
            >>>     deactivate_missing=False
            >>> )
            >>> print(f"Synced: {results['updated']} updated, "
            >>>       f"{results['created']} created")
            >>> 
            >>> # Sync La Liga teams from API-Football
            >>> results = teams_service.sync_teams(
            >>>     provider='api-football',
            >>>     league_id=140,
            >>>     deactivate_missing=True
            >>> )
        """
        logger.info(
            f"Starting team sync for provider: {provider}, "
            f"competition_id: {competition_id}, league_id: {league_id}"
        )
        
        # Initialize statistics
        stats = {
            'fetched': 0,
            'created': 0,
            'updated': 0,
            'deactivated': 0,
            'errors': []
        }
        
        try:
            # Step 1: Fetch teams from API
            fetch_results = self.fetch_teams_from_provider(
                provider=provider,
                competition_id=competition_id,
                league_id=league_id
            )
            
            if not fetch_results['success']:
                stats['errors'].append({
                    'stage': 'fetch',
                    'message': 'Failed to fetch teams from API'
                })
                logger.error("Failed to fetch teams from API")
                return stats
            
            stats['fetched'] = fetch_results['fetched']
            
            # Step 2: Extract external_ids from fetched teams
            fetched_external_ids = [
                team.external_id 
                for team in fetch_results.get('created_teams', [])
            ] + [
                team.external_id 
                for team in fetch_results.get('updated_teams', [])
            ]
            
            stats['created'] = fetch_results['created']
            stats['updated'] = fetch_results['updated']
            
            # Step 3: Deactivate missing teams (optional)
            if deactivate_missing and fetched_external_ids:
                logger.info(
                    f"Checking for teams to deactivate "
                    f"(not in {len(fetched_external_ids)} fetched teams)"
                )
                
                # Find teams with this provider prefix that weren't in API response
                provider_prefix = f"{provider}-"
                existing_teams = Team.objects.filter(
                    external_id__startswith=provider_prefix,
                    is_active=True
                ).exclude(
                    external_id__in=fetched_external_ids
                )
                
                deactivated_count = 0
                for team in existing_teams:
                    try:
                        self.deactivate_team(team.id)
                        deactivated_count += 1
                        logger.info(
                            f"Deactivated team not in API response: "
                            f"{team.name} ({team.external_id})"
                        )
                    except Exception as e:
                        stats['errors'].append({
                            'stage': 'deactivate',
                            'team_id': str(team.id),
                            'team_name': team.name,
                            'error': str(e)
                        })
                        logger.error(
                            f"Error deactivating team {team.name}: {e}"
                        )
                
                stats['deactivated'] = deactivated_count
                logger.info(f"Deactivated {deactivated_count} missing teams")
            
            # Add any fetch errors to stats
            if fetch_results.get('errors'):
                stats['errors'].extend(fetch_results['errors'])
            
            # Log final statistics
            logger.info(
                f"Team sync completed: "
                f"Fetched: {stats['fetched']}, "
                f"Created: {stats['created']}, "
                f"Updated: {stats['updated']}, "
                f"Deactivated: {stats['deactivated']}, "
                f"Errors: {len(stats['errors'])}"
            )
            
            return stats
            
        except Exception as e:
            error_msg = f"Error during team sync: {e}"
            logger.error(error_msg)
            stats['errors'].append({
                'stage': 'sync',
                'error': str(e)
            })
            raise
