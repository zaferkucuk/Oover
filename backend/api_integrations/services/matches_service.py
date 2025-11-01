"""
Matches Service

Business logic for managing match/fixture data from external APIs and database operations.

This service provides comprehensive match management including:
- CRUD operations on Match model
- Fetching fixtures from API-Football
- Data transformation and validation
- Match status tracking (upcoming, live, completed)
- Team-based and league-based queries
- Date range filtering
- Live match updates
- Bulk operations with transaction support

Matches data is highly dynamic with different update frequencies:
- Upcoming fixtures: check hourly (can be postponed)
- Live matches: check every 5 minutes (rapid changes)
- Completed matches: rarely change (final results)

This service is designed for:
- Daily updates: fetch today's and upcoming fixtures
- Live tracking: monitor in-progress matches
- Historical data: fetch completed matches for analysis
- Team tracking: follow specific team's fixtures
- League monitoring: track all fixtures in a league

Dependencies:
- providers.api_football.client: APIFootballClient
- transformers.match_transformer: MatchTransformer
- apps.core.models: Match, Team, League

Author: Oover Development Team
Date: November 2025
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date

from django.db import transaction
from django.db.models import QuerySet, Q
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from apps.core.models import Match, Team, League
from api_integrations.providers.api_football.client import APIFootballClient
from api_integrations.transformers.match_transformer import MatchTransformer

logger = logging.getLogger(__name__)


class MatchesService:
    """
    Service for managing match/fixture data from external APIs and database operations.
    
    This service provides three layers of functionality:
    
    1. Base CRUD Operations:
       - get_by_id, list, count, exists
       - create, update, delete
       - bulk_create, bulk_upsert
       - get_or_create, update_or_create
    
    2. Match-Specific Operations:
       - get_by_external_id, get_by_status
       - get_by_team (home/away), get_by_league
       - get_upcoming_matches, get_live_matches
       - get_completed_matches, get_by_date_range
       - search_matches
    
    3. API Integration:
       - fetch_fixtures_from_api
       - update_fixture_from_api
       - bulk_update_live_matches
       - Transform + Validate + Save pipeline
       - Duplicate detection via external_id
       - Error handling and statistics
    
    Usage Notes:
        - Matches are highly dynamic (status changes frequently)
        - Upcoming fixtures: cache 1 hour, check daily
        - Live matches: cache 5 minutes, check actively
        - Completed matches: cache 7 days, rarely update
        - Focus on current season fixtures
        - Update live matches in near real-time
    
    Example Usage:
        >>> from api_integrations.services.matches_service import MatchesService
        >>> from apps.core.models import League, Team
        >>> 
        >>> service = MatchesService()
        >>> 
        >>> # Fetch today's fixtures for a league
        >>> league = League.objects.get(name='Premier League')
        >>> result = service.fetch_fixtures_from_api(
        ...     league_id=league.external_id.split('-')[-1],
        ...     season=2025,
        ...     date=date.today()
        ... )
        >>> print(f"Saved {result['saved']} fixtures")
        >>> # Output: Saved 10 fixtures
        >>> 
        >>> # Get upcoming matches for next 7 days
        >>> upcoming = service.get_upcoming_matches(days_ahead=7)
        >>> print(f"Found {upcoming.count()} upcoming matches")
        >>> 
        >>> # Get currently live matches
        >>> live = service.get_live_matches()
        >>> for match in live:
        ...     print(f"{match.home_team.name} vs {match.away_team.name}")
        ...     print(f"Status: {match.status} ({match.elapsed_time}')")
        >>> 
        >>> # Get team's recent matches
        >>> team = Team.objects.get(name='Manchester United')
        >>> result = service.fetch_fixtures_from_api(
        ...     team_id=team.external_id.split('-')[-1],
        ...     season=2025,
        ...     last=10
        ... )
        >>> 
        >>> # Update live matches (e.g., via Celery task every 5 minutes)
        >>> stats = service.bulk_update_live_matches()
        >>> print(f"Updated {stats['updated']} live matches")
    """
    
    def __init__(self):
        """
        Initialize matches service with API provider and transformer.
        
        Retrieves API-Football API key from Django settings and initializes:
        - API-Football client (primary provider for fixtures)
        - Match data transformer for API-Football format
        
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
        self.transformer = MatchTransformer()
        
        logger.info("Initialized MatchesService with API-Football provider")
    
    # ==================== Basic CRUD Operations ====================
    
    def get_by_id(self, match_id: str) -> Optional[Match]:
        """
        Get match by primary key ID.
        
        Args:
            match_id: Match UUID string
            
        Returns:
            Match object or None if not found
        """
        try:
            return Match.objects.select_related(
                'league', 'league__country', 'home_team', 'away_team'
            ).get(id=match_id)
        except Match.DoesNotExist:
            logger.warning(f"Match not found: {match_id}")
            return None
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QuerySet:
        """
        List matches with optional filtering, ordering, and pagination.
        
        Args:
            filters: Dictionary of field filters (e.g., {'league_id': 'uuid-here'})
            order_by: List of fields to order by (e.g., ['-date', 'time'])
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            QuerySet of Match objects with related data pre-fetched
        """
        queryset = Match.objects.select_related(
            'league', 'league__country', 'home_team', 'away_team'
        ).all()
        
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
        Count matches matching filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching matches
        """
        queryset = Match.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if any match matches filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            True if at least one match matches, False otherwise
        """
        return Match.objects.filter(**filters).exists()
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> Match:
        """
        Create a new match.
        
        Args:
            data: Match data dictionary
            
        Returns:
            Created Match object
            
        Raises:
            ValidationError: If data is invalid
        """
        # Basic validation
        required_fields = ['league_id', 'home_team_id', 'away_team_id', 'date']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate foreign keys exist
        league_id = data.get('league_id')
        if not League.objects.filter(id=league_id).exists():
            raise ValidationError(f"League not found: {league_id}")
        
        home_team_id = data.get('home_team_id')
        if not Team.objects.filter(id=home_team_id).exists():
            raise ValidationError(f"Home team not found: {home_team_id}")
        
        away_team_id = data.get('away_team_id')
        if not Team.objects.filter(id=away_team_id).exists():
            raise ValidationError(f"Away team not found: {away_team_id}")
        
        match = Match.objects.create(**data)
        logger.info(
            f"Created match: {match.home_team.name} vs {match.away_team.name} "
            f"({match.date}) - ID: {match.id}"
        )
        return match
    
    @transaction.atomic
    def update(self, match_id: str, data: Dict[str, Any]) -> Optional[Match]:
        """
        Update existing match.
        
        Args:
            match_id: Match UUID string
            data: Updated match data
            
        Returns:
            Updated Match object or None if not found
        """
        match = self.get_by_id(match_id)
        if not match:
            return None
        
        # Validate foreign keys if being updated
        if 'league_id' in data:
            league_id = data['league_id']
            if not League.objects.filter(id=league_id).exists():
                raise ValidationError(f"League not found: {league_id}")
        
        if 'home_team_id' in data:
            home_team_id = data['home_team_id']
            if not Team.objects.filter(id=home_team_id).exists():
                raise ValidationError(f"Home team not found: {home_team_id}")
        
        if 'away_team_id' in data:
            away_team_id = data['away_team_id']
            if not Team.objects.filter(id=away_team_id).exists():
                raise ValidationError(f"Away team not found: {away_team_id}")
        
        for field, value in data.items():
            setattr(match, field, value)
        
        match.save()
        logger.info(
            f"Updated match: {match.home_team.name} vs {match.away_team.name} "
            f"({match.date}) - ID: {match.id}"
        )
        return match
    
    @transaction.atomic
    def delete(self, match_id: str) -> bool:
        """
        Delete a match by ID.
        
        Args:
            match_id: Match UUID string
            
        Returns:
            True if deleted, False if not found
        """
        match = self.get_by_id(match_id)
        if not match:
            return False
        
        match_desc = (
            f"{match.home_team.name} vs {match.away_team.name} ({match.date})"
        )
        match.delete()
        logger.info(f"Deleted match: {match_desc} - ID: {match_id}")
        return True
    
    @transaction.atomic
    def bulk_create(
        self,
        matches_data: List[Dict[str, Any]]
    ) -> Tuple[List[Match], List[str]]:
        """
        Bulk create matches.
        
        Args:
            matches_data: List of match data dictionaries
            
        Returns:
            Tuple of (created_matches, error_messages)
        """
        created_matches = []
        errors = []
        
        for idx, data in enumerate(matches_data):
            try:
                match = self.create(data)
                created_matches.append(match)
            except Exception as e:
                home = data.get('home_team_id', 'Unknown')
                away = data.get('away_team_id', 'Unknown')
                error_msg = f"Match #{idx + 1} ({home} vs {away}): {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk create: {len(created_matches)} created, {len(errors)} failed"
        )
        return created_matches, errors
    
    @transaction.atomic
    def bulk_upsert_matches(
        self,
        matches_data: List[Dict[str, Any]],
        match_field: str = 'external_id'
    ) -> Tuple[List[Match], List[Match], List[str]]:
        """
        Bulk create or update matches based on match_field.
        
        Args:
            matches_data: List of match data dictionaries
            match_field: Field to use for matching (default: 'external_id')
            
        Returns:
            Tuple of (created_matches, updated_matches, error_messages)
        """
        created_matches = []
        updated_matches = []
        errors = []
        
        for idx, data in enumerate(matches_data):
            try:
                match_value = data.get(match_field)
                if not match_value:
                    raise ValueError(f"Missing {match_field} field")
                
                # Check if match exists
                existing_match = Match.objects.filter(
                    **{match_field: match_value}
                ).first()
                
                if existing_match:
                    # Update existing match
                    for field, value in data.items():
                        setattr(existing_match, field, value)
                    existing_match.save()
                    updated_matches.append(existing_match)
                    logger.debug(
                        f"Updated match: {existing_match.home_team.name} vs "
                        f"{existing_match.away_team.name} ({existing_match.date})"
                    )
                else:
                    # Create new match
                    match = self.create(data)
                    created_matches.append(match)
                    logger.debug(
                        f"Created match: {match.home_team.name} vs "
                        f"{match.away_team.name} ({match.date})"
                    )
                    
            except Exception as e:
                error_msg = f"Match #{idx + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Bulk upsert: {len(created_matches)} created, "
            f"{len(updated_matches)} updated, {len(errors)} failed"
        )
        return created_matches, updated_matches, errors
    
    # ==================== Match-Specific Operations ====================
    
    def get_by_external_id(self, external_id: str) -> Optional[Match]:
        """
        Get match by external API identifier.
        
        Args:
            external_id: External ID (e.g., 'api-football-867946')
            
        Returns:
            Match object or None if not found
        """
        try:
            return Match.objects.select_related(
                'league', 'home_team', 'away_team'
            ).get(external_id=external_id)
        except Match.DoesNotExist:
            logger.debug(f"Match not found by external_id: {external_id}")
            return None
    
    def get_by_status(self, status: str) -> QuerySet:
        """
        Get all matches with a specific status.
        
        Args:
            status: Match status code (TBD, NS, 1H, HT, 2H, ET, BT, P, 
                   SUSP, INT, FT, AET, PEN, PST, CANC, ABD, AWD, WO, LIVE)
            
        Returns:
            QuerySet of Match objects ordered by date
        """
        return Match.objects.select_related(
            'league', 'home_team', 'away_team'
        ).filter(status=status).order_by('date', 'time')
    
    def get_by_team(
        self,
        team_id: str,
        home_only: bool = False,
        away_only: bool = False
    ) -> QuerySet:
        """
        Get all matches for a specific team.
        
        Args:
            team_id: Team UUID string
            home_only: If True, return only home matches
            away_only: If True, return only away matches
            
        Returns:
            QuerySet of Match objects ordered by date descending
        """
        if home_only:
            queryset = Match.objects.filter(home_team_id=team_id)
        elif away_only:
            queryset = Match.objects.filter(away_team_id=team_id)
        else:
            queryset = Match.objects.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id)
            )
        
        return queryset.select_related(
            'league', 'home_team', 'away_team'
        ).order_by('-date', '-time')
    
    def get_by_league(self, league_id: str, season: Optional[int] = None) -> QuerySet:
        """
        Get all matches for a specific league.
        
        Args:
            league_id: League UUID string
            season: Optional year to filter by season
            
        Returns:
            QuerySet of Match objects ordered by date
        """
        queryset = Match.objects.filter(league_id=league_id)
        
        if season:
            queryset = queryset.filter(season=season)
        
        return queryset.select_related(
            'league', 'home_team', 'away_team'
        ).order_by('date', 'time')
    
    def get_upcoming_matches(
        self,
        league_id: Optional[str] = None,
        team_id: Optional[str] = None,
        days_ahead: int = 7
    ) -> QuerySet:
        """
        Get upcoming matches (not yet started).
        
        Args:
            league_id: Optional league UUID to filter
            team_id: Optional team UUID to filter
            days_ahead: Number of days to look ahead (default: 7)
            
        Returns:
            QuerySet of upcoming Match objects ordered by date
        """
        today = timezone.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        queryset = Match.objects.filter(
            date__gte=today,
            date__lte=end_date,
            status__in=['TBD', 'NS']  # Not started yet
        )
        
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        if team_id:
            queryset = queryset.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id)
            )
        
        return queryset.select_related(
            'league', 'home_team', 'away_team'
        ).order_by('date', 'time')
    
    def get_live_matches(self, league_id: Optional[str] = None) -> QuerySet:
        """
        Get currently live matches.
        
        Args:
            league_id: Optional league UUID to filter
            
        Returns:
            QuerySet of live Match objects ordered by elapsed time
        """
        live_statuses = ['1H', 'HT', '2H', 'ET', 'BT', 'P', 'LIVE']
        queryset = Match.objects.filter(status__in=live_statuses)
        
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        return queryset.select_related(
            'league', 'home_team', 'away_team'
        ).order_by('-elapsed_time')
    
    def get_completed_matches(
        self,
        league_id: Optional[str] = None,
        team_id: Optional[str] = None,
        days_back: int = 7
    ) -> QuerySet:
        """
        Get completed matches.
        
        Args:
            league_id: Optional league UUID to filter
            team_id: Optional team UUID to filter
            days_back: Number of days to look back (default: 7)
            
        Returns:
            QuerySet of completed Match objects ordered by date descending
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=days_back)
        
        completed_statuses = ['FT', 'AET', 'PEN']
        queryset = Match.objects.filter(
            date__gte=start_date,
            date__lte=today,
            status__in=completed_statuses
        )
        
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        if team_id:
            queryset = queryset.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id)
            )
        
        return queryset.select_related(
            'league', 'home_team', 'away_team'
        ).order_by('-date', '-time')
    
    def get_by_date(self, target_date: date) -> QuerySet:
        """
        Get all matches on a specific date.
        
        Args:
            target_date: Date to filter by
            
        Returns:
            QuerySet of Match objects ordered by time
        """
        return Match.objects.select_related(
            'league', 'home_team', 'away_team'
        ).filter(date=target_date).order_by('time')
    
    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        league_id: Optional[str] = None
    ) -> QuerySet:
        """
        Get matches within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            league_id: Optional league UUID to filter
            
        Returns:
            QuerySet of Match objects ordered by date and time
        """
        queryset = Match.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        return queryset.select_related(
            'league', 'home_team', 'away_team'
        ).order_by('date', 'time')
    
    # ==================== API Integration ====================
    
    @transaction.atomic
    def fetch_fixtures_from_api(
        self,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
        team_id: Optional[int] = None,
        date: Optional[date] = None,
        status: Optional[str] = None,
        timezone_str: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        last: Optional[int] = None,
        next: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch fixtures from API-Football and save to database.
        
        This is the main method for populating/syncing fixture data.
        
        Recommended usage patterns:
        - Today's fixtures: date=today
        - Upcoming week: from_date=today, to_date=today+7days
        - League fixtures: league_id + season
        - Team fixtures: team_id + season
        - Live matches: status='LIVE'
        
        Args:
            league_id: API-Football league ID
            season: Year (e.g., 2025)
            team_id: API-Football team ID
            date: Specific date (YYYY-MM-DD)
            status: Match status filter
            timezone_str: Timezone (e.g., 'Europe/London')
            from_date: Start date for range
            to_date: End date for range
            last: Number of last fixtures
            next: Number of next fixtures
            
        Returns:
            Dictionary with operation statistics
        """
        logger.info(
            f"fetch_fixtures_from_api called: league_id={league_id}, "
            f"season={season}, team_id={team_id}, date={date}, "
            f"status={status}"
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
            # Fetch fixtures from API-Football
            logger.info("Fetching fixtures from API-Football...")
            
            # Convert dates to strings
            date_str = date.strftime('%Y-%m-%d') if date else None
            from_str = from_date.strftime('%Y-%m-%d') if from_date else None
            to_str = to_date.strftime('%Y-%m-%d') if to_date else None
            
            api_fixtures = self.client.get_fixtures(
                fixture_id=None,
                league_id=league_id,
                season=season,
                team_id=team_id,
                date=date_str,
                status=status,
                timezone=timezone_str,
                from_date=from_str,
                to_date=to_str,
                last=last,
                next=next
            )
            
            stats['fetched'] = len(api_fixtures)
            logger.info(f"Fetched {stats['fetched']} fixtures from API-Football")
            
            if not api_fixtures:
                logger.warning("No fixtures returned from API")
                return stats
            
            # Transform fixtures data
            transformed_fixtures = []
            for api_fixture in api_fixtures:
                try:
                    # Transform fixture data
                    transformed = self.transformer.transform(
                        api_fixture,
                        provider='api-football'
                    )
                    
                    if transformed:
                        # Resolve foreign key IDs
                        league_ext_id = transformed.get('league_external_id')
                        home_ext_id = transformed.get('home_team_external_id')
                        away_ext_id = transformed.get('away_team_external_id')
                        
                        # Get league ID
                        if league_ext_id:
                            try:
                                league = League.objects.get(external_id=league_ext_id)
                                transformed['league_id'] = str(league.id)
                            except League.DoesNotExist:
                                error_msg = (
                                    f"League not found: {league_ext_id} for fixture "
                                    f"{transformed.get('external_id')}"
                                )
                                stats['errors'].append(error_msg)
                                logger.warning(error_msg)
                                continue
                        
                        # Get home team ID
                        if home_ext_id:
                            try:
                                home_team = Team.objects.get(external_id=home_ext_id)
                                transformed['home_team_id'] = str(home_team.id)
                            except Team.DoesNotExist:
                                error_msg = (
                                    f"Home team not found: {home_ext_id} for fixture "
                                    f"{transformed.get('external_id')}"
                                )
                                stats['errors'].append(error_msg)
                                logger.warning(error_msg)
                                continue
                        
                        # Get away team ID
                        if away_ext_id:
                            try:
                                away_team = Team.objects.get(external_id=away_ext_id)
                                transformed['away_team_id'] = str(away_team.id)
                            except Team.DoesNotExist:
                                error_msg = (
                                    f"Away team not found: {away_ext_id} for fixture "
                                    f"{transformed.get('external_id')}"
                                )
                                stats['errors'].append(error_msg)
                                logger.warning(error_msg)
                                continue
                        
                        # Remove external_id helper fields
                        transformed.pop('league_external_id', None)
                        transformed.pop('home_team_external_id', None)
                        transformed.pop('away_team_external_id', None)
                        
                        transformed_fixtures.append(transformed)
                        stats['transformed'] += 1
                    else:
                        error_msg = (
                            f"Transform returned None for fixture "
                            f"{api_fixture.get('fixture', {}).get('id', 'Unknown')}"
                        )
                        stats['errors'].append(error_msg)
                        logger.warning(error_msg)
                        
                except Exception as e:
                    error_msg = (
                        f"Transform error for fixture "
                        f"{api_fixture.get('fixture', {}).get('id', 'Unknown')}: "
                        f"{str(e)}"
                    )
                    stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Transformed {stats['transformed']} fixtures")
            
            # Check transformer errors
            if self.transformer.has_errors():
                transformer_errors = self.transformer.get_errors()
                stats['errors'].extend(transformer_errors)
                logger.warning(
                    f"Transformer collected {len(transformer_errors)} errors"
                )
            
            # Save fixtures to database (upsert)
            created, updated, save_errors = self.bulk_upsert_matches(
                transformed_fixtures,
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
            error_msg = f"Fatal error in fetch_fixtures_from_api: {str(e)}"
            logger.exception(error_msg)
            stats['errors'].append(error_msg)
            raise
    
    @transaction.atomic
    def update_fixture_from_api(self, fixture_id: int) -> Dict[str, Any]:
        """
        Update a specific fixture from API-Football.
        
        Useful for updating live matches or checking for status changes.
        
        Args:
            fixture_id: API-Football fixture ID
            
        Returns:
            Dictionary with operation result
        """
        logger.info(f"Updating fixture {fixture_id} from API-Football")
        
        result = {
            'success': False,
            'fixture_id': fixture_id,
            'error': None
        }
        
        try:
            # Fetch single fixture
            api_fixtures = self.client.get_fixtures(fixture_id=fixture_id)
            
            if not api_fixtures:
                result['error'] = f"Fixture {fixture_id} not found in API"
                logger.warning(result['error'])
                return result
            
            api_fixture = api_fixtures[0]
            
            # Transform
            transformed = self.transformer.transform(
                api_fixture,
                provider='api-football'
            )
            
            if not transformed:
                result['error'] = "Transform failed"
                return result
            
            # Resolve foreign keys
            league = League.objects.get(
                external_id=transformed.get('league_external_id')
            )
            home_team = Team.objects.get(
                external_id=transformed.get('home_team_external_id')
            )
            away_team = Team.objects.get(
                external_id=transformed.get('away_team_external_id')
            )
            
            transformed['league_id'] = str(league.id)
            transformed['home_team_id'] = str(home_team.id)
            transformed['away_team_id'] = str(away_team.id)
            
            # Remove helper fields
            transformed.pop('league_external_id', None)
            transformed.pop('home_team_external_id', None)
            transformed.pop('away_team_external_id', None)
            
            # Upsert
            external_id = transformed.get('external_id')
            existing = Match.objects.filter(external_id=external_id).first()
            
            if existing:
                for field, value in transformed.items():
                    setattr(existing, field, value)
                existing.save()
                logger.info(f"Updated fixture {fixture_id}")
            else:
                match = self.create(transformed)
                logger.info(f"Created fixture {fixture_id}")
            
            result['success'] = True
            return result
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error updating fixture {fixture_id}: {str(e)}")
            return result
    
    @transaction.atomic
    def bulk_update_live_matches(self) -> Dict[str, Any]:
        """
        Update all currently live matches from API-Football.
        
        This should be called periodically (e.g., every 5 minutes) to keep
        live match data up-to-date.
        
        Returns:
            Dictionary with operation statistics
        """
        logger.info("Updating all live matches")
        
        stats = {
            'checked': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Fetch all live fixtures from API
            result = self.fetch_fixtures_from_api(status='LIVE')
            
            stats['checked'] = result['fetched']
            stats['updated'] = result['saved']
            stats['failed'] = result['failed']
            stats['errors'] = result['errors']
            
            logger.info(
                f"Live matches update: {stats['updated']} updated, "
                f"{stats['failed']} failed"
            )
            
            return stats
            
        except Exception as e:
            error_msg = f"Error updating live matches: {str(e)}"
            logger.exception(error_msg)
            stats['errors'].append(error_msg)
            return stats
