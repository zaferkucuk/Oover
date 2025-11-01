"""
Match Transformer Module

Transforms external API responses (API-Football) into internal Match model format
with validation and data normalization.

Designed for daily updates and real-time match tracking.
"""

from typing import Any, Dict, Optional, List, Tuple
import logging
import uuid
from datetime import datetime
from django.utils import timezone

from .base import BaseTransformer


logger = logging.getLogger(__name__)


class MatchTransformer(BaseTransformer):
    """
    Transform API fixture data to internal Match model format.
    
    Currently supports:
    - API-Football (primary source for fixtures/matches)
    
    Features:
    - Fixture ID and date validation
    - Match status normalization (NS, LIVE, FT, PST, etc.)
    - Teams information extraction (home/away, scores, winner)
    - Score breakdown parsing (halftime, fulltime, extra time, penalties)
    - League and season context mapping
    - Referee and venue information extraction
    - Duplicate detection via external_id
    - Smart handling of missing data
    - Comprehensive validation
    - Real-time match status tracking
    
    Match Status Codes:
        Pre-match:
        - TBD: Time to be defined
        - NS: Not started
        - PST: Postponed
        - CANC: Cancelled
        - ABD: Abandoned
        - AWD: Technical loss (awarded)
        - WO: Walkover
        
        Live:
        - 1H: First half
        - HT: Halftime
        - 2H: Second half
        - ET: Extra time
        - BT: Break time (extra time)
        - P: Penalty shootout
        - SUSP: Suspended
        - INT: Interrupted
        - LIVE: Live (generic)
        
        Finished:
        - FT: Full time
        - AET: After extra time
        - PEN: Finished after penalties
        
    Usage:
        ```python
        from api_integrations.transformers.match_transformer import MatchTransformer
        
        transformer = MatchTransformer()
        
        # API-Football format
        api_fixture = {
            'fixture': {
                'id': 1035086,
                'referee': 'A. Taylor',
                'timezone': 'UTC',
                'date': '2024-08-17T11:30:00+00:00',
                'timestamp': 1723893000,
                'periods': {'first': 1723893000, 'second': 1723896600},
                'venue': {
                    'id': 494,
                    'name': 'Old Trafford',
                    'city': 'Manchester'
                },
                'status': {
                    'long': 'Match Finished',
                    'short': 'FT',
                    'elapsed': 90
                }
            },
            'league': {
                'id': 39,
                'name': 'Premier League',
                'country': 'England',
                'logo': 'https://...',
                'flag': 'https://...',
                'season': 2024,
                'round': 'Regular Season - 1'
            },
            'teams': {
                'home': {
                    'id': 33,
                    'name': 'Manchester United',
                    'logo': 'https://...',
                    'winner': True
                },
                'away': {
                    'id': 40,
                    'name': 'Liverpool',
                    'logo': 'https://...',
                    'winner': False
                }
            },
            'goals': {
                'home': 2,
                'away': 1
            },
            'score': {
                'halftime': {'home': 1, 'away': 0},
                'fulltime': {'home': 2, 'away': 1},
                'extratime': {'home': None, 'away': None},
                'penalty': {'home': None, 'away': None}
            }
        }
        
        match_data = transformer.transform(
            api_fixture,
            league_id='league-uuid-here',
            home_team_id='home-team-uuid',
            away_team_id='away-team-uuid'
        )
        # Returns: {
        #     'id': 'uuid',
        #     'league_id': 'league-uuid',
        #     'home_team_id': 'home-team-uuid',
        #     'away_team_id': 'away-team-uuid',
        #     'match_date': datetime,
        #     'status': 'FT',
        #     'home_score': 2,
        #     'away_score': 1,
        #     'half_time_home_score': 1,
        #     'half_time_away_score': 0,
        #     'referee': 'A. Taylor',
        #     'venue': 'Old Trafford',
        #     'external_id': 'api-football-1035086',
        #     ...
        # }
        
        # Check for validation errors
        if transformer.has_errors():
            print(transformer.get_errors())
        ```
    
    Notes:
        - Matches update frequently (cache: 1h upcoming, 5min live, 7d completed)
        - ~50,000+ fixtures available per season
        - Real-time status updates critical for live tracking
        - Score breakdown stored for detailed analysis
        - Venue information may be missing for some matches
    """
    
    # Valid match status codes
    VALID_STATUS_CODES = {
        # Pre-match
        'TBD', 'NS', 'PST', 'CANC', 'ABD', 'AWD', 'WO',
        # Live
        '1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE',
        # Finished
        'FT', 'AET', 'PEN'
    }
    
    # Status categories for filtering
    STATUS_CATEGORIES = {
        'pre_match': {'TBD', 'NS'},
        'live': {'1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE'},
        'finished': {'FT', 'AET', 'PEN'},
        'cancelled': {'PST', 'CANC', 'ABD', 'AWD', 'WO'}
    }
    
    def __init__(self):
        """Initialize match transformer."""
        super().__init__()
        self.logger.info("MatchTransformer initialized")
    
    def transform(
        self, 
        data: Dict[str, Any],
        league_id: Optional[str] = None,
        home_team_id: Optional[str] = None,
        away_team_id: Optional[str] = None,
        season: Optional[int] = None,
        provider: str = 'api-football'
    ) -> Optional[Dict[str, Any]]:
        """
        Transform API fixture response to Match model format.
        
        Converts raw API-Football fixture data into format compatible with
        Supabase matches table schema.
        
        Args:
            data: Raw API response data (single fixture object)
            league_id: UUID of the league this match belongs to
            home_team_id: UUID of the home team
            away_team_id: UUID of the away team
            season: Season year (e.g., 2024)
            provider: API provider ('api-football' - default)
            
        Returns:
            Transformed match data dict or None if validation fails:
                {
                    'id': 'uuid-string',
                    'league_id': 'uuid-string',
                    'season': 2024,
                    'home_team_id': 'uuid-string',
                    'away_team_id': 'uuid-string',
                    'match_date': datetime,
                    'status': 'FT',
                    'home_score': 2,
                    'away_score': 1,
                    'half_time_home_score': 1,
                    'half_time_away_score': 0,
                    'full_time_home_score': 2,
                    'full_time_away_score': 1,
                    'extra_time_home_score': None,
                    'extra_time_away_score': None,
                    'penalty_home_score': None,
                    'penalty_away_score': None,
                    'referee': 'A. Taylor',
                    'venue': 'Old Trafford',
                    'round': 'Regular Season - 1',
                    'external_id': 'api-football-1035086',
                    'created_at': datetime,
                    'updated_at': datetime
                }
            
        Example:
            ```python
            # Transform single match
            match = transformer.transform(
                api_fixture,
                league_id='league-uuid',
                home_team_id='home-uuid',
                away_team_id='away-uuid',
                season=2024
            )
            
            # Bulk transform
            matches = []
            for fixture in api_fixtures:
                match = transformer.transform(
                    fixture,
                    league_id=league_id,
                    home_team_id=team_map[fixture['teams']['home']['id']],
                    away_team_id=team_map[fixture['teams']['away']['id']],
                    season=2024
                )
                if match:
                    matches.append(match)
            ```
        """
        if not self.validate(data, provider):
            return None
        
        try:
            # Extract sub-objects
            fixture_data = data.get('fixture', {})
            league_data = data.get('league', {})
            teams_data = data.get('teams', {})
            goals_data = data.get('goals', {})
            score_data = data.get('score', {})
            
            # Generate consistent external_id for duplicate detection
            external_id = self._generate_external_id(fixture_data, provider)
            
            # Extract fixture metadata
            match_date = self._parse_match_date(fixture_data)
            status = self._normalize_status(fixture_data.get('status', {}))
            referee = self._extract_referee(fixture_data)
            venue = self._extract_venue(fixture_data)
            round_info = league_data.get('round')
            
            # Extract team information
            home_score = goals_data.get('home')
            away_score = goals_data.get('away')
            
            # Extract score breakdown
            scores = self._extract_scores(score_data)
            
            # Use season from league data if not provided
            if season is None:
                season = league_data.get('season')
            
            # Get current timestamp
            now = timezone.now()
            
            # Build transformed data matching Supabase schema
            transformed = {
                'id': str(uuid.uuid4()),
                'league_id': league_id,
                'season': season,
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'match_date': match_date,
                'status': status,
                'home_score': home_score,
                'away_score': away_score,
                'half_time_home_score': scores['halftime']['home'],
                'half_time_away_score': scores['halftime']['away'],
                'full_time_home_score': scores['fulltime']['home'],
                'full_time_away_score': scores['fulltime']['away'],
                'extra_time_home_score': scores['extratime']['home'],
                'extra_time_away_score': scores['extratime']['away'],
                'penalty_home_score': scores['penalty']['home'],
                'penalty_away_score': scores['penalty']['away'],
                'referee': referee,
                'venue': venue,
                'round': round_info,
                'external_id': external_id,
                'created_at': now,
                'updated_at': now,
            }
            
            self.logger.debug(
                f"Successfully transformed match: {teams_data.get('home', {}).get('name')} vs "
                f"{teams_data.get('away', {}).get('name')} "
                f"(ID: {fixture_data.get('id')}, Status: {status}) from {provider}"
            )
            
            return transformed
            
        except Exception as e:
            error_msg = (
                f"Transformation error for fixture {data.get('fixture', {}).get('id')}: "
                f"{str(e)}"
            )
            self._collect_error(error_msg)
            self.logger.exception(error_msg)
            return None
    
    def validate(
        self, 
        data: Dict[str, Any],
        provider: str = 'api-football'
    ) -> bool:
        """
        Validate fixture data before transformation.
        
        Required fields:
        - fixture.id (int): Fixture ID from API
        - fixture.date (str): Match date/time
        - fixture.status.short (str): Status code
        - teams.home.id (int): Home team ID
        - teams.away.id (int): Away team ID
        - league.id (int): League ID
        
        Optional fields:
        - fixture.referee (str): Referee name
        - fixture.venue (dict): Venue information
        - goals (dict): Current scores
        - score (dict): Detailed score breakdown
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            True if validation passes, False otherwise
            
        Validation Rules:
            - fixture sub-object must exist
            - fixture.id must be positive integer
            - fixture.date must be valid datetime string
            - fixture.status.short must be valid status code
            - teams sub-object must exist with home/away
            - league sub-object must exist
        """
        # Check fixture sub-object exists
        if 'fixture' not in data:
            self._collect_error("Missing 'fixture' object in response")
            return False
        
        fixture_data = data['fixture']
        
        # Check required fixture fields
        required_fields = ['id', 'date', 'status']
        for field in required_fields:
            if field not in fixture_data:
                self._collect_error(f"Missing required field: fixture.{field}")
                return False
        
        # Validate fixture ID
        fixture_id = fixture_data.get('id')
        if not isinstance(fixture_id, int) or fixture_id <= 0:
            self._collect_error(
                f"Fixture ID must be positive integer, got: {fixture_id}"
            )
            return False
        
        # Validate match date
        match_date = fixture_data.get('date')
        if not isinstance(match_date, str) or not match_date.strip():
            self._collect_error("Match date cannot be empty")
            return False
        
        # Validate status
        status_data = fixture_data.get('status', {})
        if not isinstance(status_data, dict):
            self._collect_error("fixture.status must be a dict")
            return False
        
        status_code = status_data.get('short')
        if not status_code:
            self._collect_error("Missing status code (fixture.status.short)")
            return False
        
        if status_code not in self.VALID_STATUS_CODES:
            self.logger.warning(
                f"Unexpected status code: {status_code} for fixture {fixture_id}, "
                f"expected one of: {self.VALID_STATUS_CODES}"
            )
            # Don't fail validation, just warn
        
        # Check teams sub-object exists
        if 'teams' not in data:
            self._collect_error("Missing 'teams' object in response")
            return False
        
        teams_data = data['teams']
        
        # Validate home team
        if 'home' not in teams_data:
            self._collect_error("Missing teams.home object")
            return False
        
        home_team = teams_data['home']
        if 'id' not in home_team:
            self._collect_error("Missing teams.home.id")
            return False
        
        # Validate away team
        if 'away' not in teams_data:
            self._collect_error("Missing teams.away object")
            return False
        
        away_team = teams_data['away']
        if 'id' not in away_team:
            self._collect_error("Missing teams.away.id")
            return False
        
        # Check league sub-object exists
        if 'league' not in data:
            self._collect_error("Missing 'league' object in response")
            return False
        
        league_data = data['league']
        if 'id' not in league_data:
            self._collect_error("Missing league.id")
            return False
        
        self.logger.debug(
            f"Validation passed for fixture: {fixture_id} "
            f"({home_team.get('name')} vs {away_team.get('name')})"
        )
        return True
    
    def validate_match_data(
        self, 
        match_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate transformed match data before database insertion.
        
        Checks:
        - Required fields are present
        - UUIDs are valid
        - Scores are non-negative (if present)
        - Status code is valid
        - Match date is valid
        
        Args:
            match_data: Transformed match data dict
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
            
        Example:
            ```python
            match = transformer.transform(api_fixture, ...)
            is_valid, errors = transformer.validate_match_data(match)
            
            if not is_valid:
                print(f"Validation errors: {errors}")
            else:
                # Save to database
                save_match(match)
            ```
        """
        errors = []
        
        # Check required fields
        required_fields = [
            'id', 'league_id', 'home_team_id', 'away_team_id',
            'match_date', 'status', 'external_id'
        ]
        
        for field in required_fields:
            if field not in match_data or match_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate UUID fields
        uuid_fields = ['id', 'league_id', 'home_team_id', 'away_team_id']
        for field in uuid_fields:
            value = match_data.get(field)
            if value:
                try:
                    uuid.UUID(str(value))
                except (ValueError, AttributeError):
                    errors.append(f"Invalid UUID format for {field}: {value}")
        
        # Validate scores (if present)
        score_fields = [
            'home_score', 'away_score',
            'half_time_home_score', 'half_time_away_score',
            'full_time_home_score', 'full_time_away_score',
            'extra_time_home_score', 'extra_time_away_score',
            'penalty_home_score', 'penalty_away_score'
        ]
        
        for field in score_fields:
            score = match_data.get(field)
            if score is not None:
                if not isinstance(score, (int, float)) or score < 0:
                    errors.append(f"Invalid score for {field}: {score}")
        
        # Validate status code
        status = match_data.get('status')
        if status and status not in self.VALID_STATUS_CODES:
            errors.append(f"Invalid status code: {status}")
        
        # Validate match date
        match_date = match_data.get('match_date')
        if match_date and not isinstance(match_date, datetime):
            errors.append(f"Invalid match_date type: {type(match_date)}")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.warning(
                f"Match data validation failed: {errors}"
            )
        
        return is_valid, errors
    
    def _generate_external_id(
        self, 
        fixture_data: Dict[str, Any],
        provider: str
    ) -> str:
        """
        Generate consistent external_id for duplicate detection.
        
        Format: {provider}-{fixture_id}
        
        Using fixture ID because:
        - IDs are stable and unique
        - Can be used to check for updates
        - Prevents duplicate insertions
        
        Args:
            fixture_data: Fixture sub-object from API response
            provider: API provider name
            
        Returns:
            External ID string
            
        Examples:
            'api-football-1035086'
            'api-football-867543'
        """
        fixture_id = fixture_data['id']
        return f"{provider}-{fixture_id}"
    
    def _parse_match_date(self, fixture_data: Dict[str, Any]) -> datetime:
        """
        Parse match date from API response.
        
        API-Football provides date in ISO 8601 format with timezone.
        Convert to timezone-aware datetime object.
        
        Args:
            fixture_data: Fixture sub-object from API response
            
        Returns:
            Timezone-aware datetime object
            
        Examples:
            '2024-08-17T11:30:00+00:00' -> datetime(2024, 8, 17, 11, 30, tzinfo=UTC)
        """
        date_str = fixture_data.get('date')
        
        try:
            # Parse ISO 8601 format
            match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Ensure timezone-aware
            if match_date.tzinfo is None:
                match_date = timezone.make_aware(match_date)
            
            return match_date
            
        except (ValueError, AttributeError) as e:
            self.logger.error(f"Error parsing match date '{date_str}': {e}")
            # Return current time as fallback
            return timezone.now()
    
    def _normalize_status(self, status_data: Dict[str, Any]) -> str:
        """
        Normalize match status code.
        
        Extract short status code from status object.
        
        Args:
            status_data: Status sub-object from fixture
            
        Returns:
            Normalized status code (e.g., 'FT', 'NS', '1H')
            
        Examples:
            {'short': 'FT', 'long': 'Match Finished'} -> 'FT'
            {'short': 'NS', 'long': 'Not Started'} -> 'NS'
        """
        return status_data.get('short', 'TBD').upper().strip()
    
    def _extract_referee(self, fixture_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract referee name from fixture data.
        
        Handles missing referee information gracefully.
        
        Args:
            fixture_data: Fixture sub-object from API response
            
        Returns:
            Referee name or None if not available
            
        Examples:
            Valid: 'A. Taylor'
            Missing: None
        """
        referee = fixture_data.get('referee')
        
        if not referee or not isinstance(referee, str):
            return None
        
        referee = referee.strip()
        
        if not referee or referee.lower() in ['null', 'n/a', 'tbc']:
            return None
        
        return referee
    
    def _extract_venue(self, fixture_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract venue name from fixture data.
        
        Handles missing venue information gracefully.
        
        Args:
            fixture_data: Fixture sub-object from API response
            
        Returns:
            Venue name or None if not available
            
        Examples:
            Valid: 'Old Trafford'
            Missing: None
        """
        venue_data = fixture_data.get('venue', {})
        
        if not isinstance(venue_data, dict):
            return None
        
        venue_name = venue_data.get('name')
        
        if not venue_name or not isinstance(venue_name, str):
            return None
        
        venue_name = venue_name.strip()
        
        if not venue_name or venue_name.lower() in ['null', 'n/a', 'tbc']:
            return None
        
        return venue_name
    
    def _extract_scores(self, score_data: Dict[str, Any]) -> Dict[str, Dict[str, Optional[int]]]:
        """
        Extract detailed score breakdown from score object.
        
        Parses halftime, fulltime, extra time, and penalty scores
        for both home and away teams.
        
        Args:
            score_data: Score sub-object from API response
            
        Returns:
            Dict with score breakdown:
                {
                    'halftime': {'home': 1, 'away': 0},
                    'fulltime': {'home': 2, 'away': 1},
                    'extratime': {'home': None, 'away': None},
                    'penalty': {'home': None, 'away': None}
                }
        """
        scores = {
            'halftime': {'home': None, 'away': None},
            'fulltime': {'home': None, 'away': None},
            'extratime': {'home': None, 'away': None},
            'penalty': {'home': None, 'away': None}
        }
        
        if not isinstance(score_data, dict):
            return scores
        
        # Extract halftime scores
        halftime = score_data.get('halftime', {})
        if isinstance(halftime, dict):
            scores['halftime']['home'] = halftime.get('home')
            scores['halftime']['away'] = halftime.get('away')
        
        # Extract fulltime scores
        fulltime = score_data.get('fulltime', {})
        if isinstance(fulltime, dict):
            scores['fulltime']['home'] = fulltime.get('home')
            scores['fulltime']['away'] = fulltime.get('away')
        
        # Extract extra time scores
        extratime = score_data.get('extratime', {})
        if isinstance(extratime, dict):
            scores['extratime']['home'] = extratime.get('home')
            scores['extratime']['away'] = extratime.get('away')
        
        # Extract penalty scores
        penalty = score_data.get('penalty', {})
        if isinstance(penalty, dict):
            scores['penalty']['home'] = penalty.get('home')
            scores['penalty']['away'] = penalty.get('away')
        
        return scores
    
    def get_status_category(self, status_code: str) -> Optional[str]:
        """
        Get category of a status code.
        
        Categories:
        - pre_match: TBD, NS
        - live: 1H, HT, 2H, ET, BT, P, SUSP, INT, LIVE
        - finished: FT, AET, PEN
        - cancelled: PST, CANC, ABD, AWD, WO
        
        Args:
            status_code: Match status code
            
        Returns:
            Category name or None if unknown
            
        Example:
            ```python
            category = transformer.get_status_category('FT')
            print(category)  # 'finished'
            
            category = transformer.get_status_category('1H')
            print(category)  # 'live'
            ```
        """
        status_code = status_code.upper().strip()
        
        for category, codes in self.STATUS_CATEGORIES.items():
            if status_code in codes:
                return category
        
        return None
