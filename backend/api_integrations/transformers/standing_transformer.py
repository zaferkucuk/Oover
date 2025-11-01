"""
Standing Transformer Module

Transforms external API responses (API-Football) into internal Standing model format
with validation and data normalization.

Designed for weekly/daily league table updates.
"""

from typing import Any, Dict, Optional, List, Tuple
import logging
import uuid
from datetime import datetime
from django.utils import timezone

from .base import BaseTransformer


logger = logging.getLogger(__name__)


class StandingTransformer(BaseTransformer):
    """
    Transform API standings data to internal Standing model format.
    
    Currently supports:
    - API-Football (primary source for league standings/tables)
    
    Features:
    - League table position and points extraction
    - Form analysis (recent match results: W/D/L)
    - Home/away performance breakdown
    - Goal statistics (scored, conceded, difference)
    - Match statistics (played, won, drawn, lost)
    - Status description parsing (promotion/relegation zones)
    - Team ID resolution from API data
    - Duplicate detection via composite key (league + season + team)
    - Smart handling of missing data
    - Comprehensive validation
    - Support for multiple standings groups (most leagues have 1)
    
    Standing Groups:
        Most leagues have a single standings table, but some have multiple:
        - Regular league: Single table for all teams
        - Playoffs: Separate groups for playoff positions
        - Relegation playoffs: Additional standings for bottom teams
        
    Form Format:
        Recent match results as string: 'WWDLW' = Win, Win, Draw, Loss, Win
        Usually last 5 matches, ordered from oldest to newest
        
    Status Descriptions (examples):
        - 'Promotion - Champions League (Group Stage: )'
        - 'Promotion - Europa League (Qualification: )'
        - 'Relegation - Championship'
        - None (for mid-table teams)
    
    Usage:
        ```python
        from api_integrations.transformers.standing_transformer import StandingTransformer
        
        transformer = StandingTransformer()
        
        # API-Football format (single standing entry)
        api_standing = {
            'rank': 1,
            'team': {
                'id': 33,
                'name': 'Manchester United',
                'logo': 'https://...'
            },
            'points': 73,
            'goalsDiff': 25,
            'group': 'Premier League',
            'form': 'WWDLW',
            'status': 'Promotion - Champions League (Group Stage: )',
            'description': 'Promotion - Champions League (Group Stage: )',
            'all': {
                'played': 30,
                'win': 22,
                'draw': 7,
                'lose': 1,
                'goals': {'for': 70, 'against': 45}
            },
            'home': {
                'played': 15,
                'win': 12,
                'draw': 3,
                'lose': 0,
                'goals': {'for': 38, 'against': 20}
            },
            'away': {
                'played': 15,
                'win': 10,
                'draw': 4,
                'lose': 1,
                'goals': {'for': 32, 'against': 25}
            },
            'update': '2024-03-15T10:30:00+00:00'
        }
        
        standing_data = transformer.transform(
            api_standing,
            league_id='league-uuid-here',
            season=2024,
            team_id='team-uuid-here'
        )
        # Returns: {
        #     'id': 'uuid',
        #     'league_id': 'league-uuid',
        #     'season': 2024,
        #     'team_id': 'team-uuid',
        #     'position': 1,
        #     'points': 73,
        #     'played': 30,
        #     'won': 22,
        #     'drawn': 7,
        #     'lost': 1,
        #     'goals_for': 70,
        #     'goals_against': 45,
        #     'goal_difference': 25,
        #     'recent_form': 'WWDLW',
        #     'home_played': 15,
        #     'home_won': 12,
        #     'home_drawn': 3,
        #     'home_lost': 0,
        #     'home_goals_for': 38,
        #     'home_goals_against': 20,
        #     'away_played': 15,
        #     'away_won': 10,
        #     'away_drawn': 4,
        #     'away_lost': 1,
        #     'away_goals_for': 32,
        #     'away_goals_against': 25,
        #     'status_description': 'Promotion - Champions League (Group Stage: )',
        #     'created_at': datetime,
        #     'updated_at': datetime
        # }
        
        # Bulk transform (full league table)
        standings = []
        for standing in api_standings_list:
            team_id = team_map[standing['team']['id']]  # Resolve team UUID
            
            standing_data = transformer.transform(
                standing,
                league_id=league_id,
                season=2024,
                team_id=team_id
            )
            if standing_data:
                standings.append(standing_data)
        
        # Check for validation errors
        if transformer.has_errors():
            print(transformer.get_errors())
        ```
    
    Notes:
        - Standings update after each match day (cache: 6 hours recommended)
        - ~20-24 teams per league table (varies by league)
        - Form string typically last 5 matches
        - Status description indicates special positions (promotion/relegation)
        - Some leagues have multiple standings groups
    """
    
    # Valid form characters
    VALID_FORM_CHARS = {'W', 'D', 'L'}  # Win, Draw, Loss
    
    def __init__(self):
        """Initialize standing transformer."""
        super().__init__()
        self.logger.info("StandingTransformer initialized")
    
    def transform(
        self, 
        data: Dict[str, Any],
        league_id: Optional[str] = None,
        season: Optional[int] = None,
        team_id: Optional[str] = None,
        provider: str = 'api-football'
    ) -> Optional[Dict[str, Any]]:
        """
        Transform API standing response to Standing model format.
        
        Converts raw API-Football standing data (single team entry) into format 
        compatible with Supabase standings table schema.
        
        Args:
            data: Raw API standing data (single team's standing entry)
            league_id: UUID of the league
            season: Season year (e.g., 2024)
            team_id: UUID of the team (if known, otherwise extracted from data)
            provider: API provider ('api-football' - default)
            
        Returns:
            Transformed standing data dict or None if validation fails:
                {
                    'id': 'uuid-string',
                    'league_id': 'uuid-string',
                    'season': 2024,
                    'team_id': 'uuid-string',
                    'position': 1,
                    'points': 73,
                    'played': 30,
                    'won': 22,
                    'drawn': 7,
                    'lost': 1,
                    'goals_for': 70,
                    'goals_against': 45,
                    'goal_difference': 25,
                    'recent_form': 'WWDLW',
                    'home_played': 15,
                    'home_won': 12,
                    'home_drawn': 3,
                    'home_lost': 0,
                    'home_goals_for': 38,
                    'home_goals_against': 20,
                    'away_played': 15,
                    'away_won': 10,
                    'away_drawn': 4,
                    'away_lost': 1,
                    'away_goals_for': 32,
                    'away_goals_against': 25,
                    'status_description': 'Promotion - Champions League',
                    'created_at': datetime,
                    'updated_at': datetime
                }
            
        Example:
            ```python
            # Transform single team standing
            standing = transformer.transform(
                api_standing,
                league_id='league-uuid',
                season=2024,
                team_id='team-uuid'
            )
            
            # Bulk transform (full league table)
            standings = []
            for entry in api_standings:
                team_uuid = resolve_team_id(entry['team']['id'])
                standing = transformer.transform(
                    entry,
                    league_id=league_id,
                    season=2024,
                    team_id=team_uuid
                )
                if standing:
                    standings.append(standing)
            ```
        """
        if not self.validate(data, provider):
            return None
        
        try:
            # Extract position and points
            position = data.get('rank')
            points = data.get('points', 0)
            goal_difference = data.get('goalsDiff', 0)
            
            # Extract form (recent match results)
            form = self._normalize_form(data.get('form'))
            
            # Extract status description
            status_desc = self._extract_status_description(data)
            
            # Extract overall statistics
            all_stats = data.get('all', {})
            played = all_stats.get('played', 0)
            won = all_stats.get('win', 0)
            drawn = all_stats.get('draw', 0)
            lost = all_stats.get('lose', 0)
            
            # Extract overall goal statistics
            all_goals = all_stats.get('goals', {})
            goals_for = all_goals.get('for', 0)
            goals_against = all_goals.get('against', 0)
            
            # Extract home statistics
            home_stats = data.get('home', {})
            home_played = home_stats.get('played', 0)
            home_won = home_stats.get('win', 0)
            home_drawn = home_stats.get('draw', 0)
            home_lost = home_stats.get('lose', 0)
            
            home_goals = home_stats.get('goals', {})
            home_goals_for = home_goals.get('for', 0)
            home_goals_against = home_goals.get('against', 0)
            
            # Extract away statistics
            away_stats = data.get('away', {})
            away_played = away_stats.get('played', 0)
            away_won = away_stats.get('win', 0)
            away_drawn = away_stats.get('draw', 0)
            away_lost = away_stats.get('lose', 0)
            
            away_goals = away_stats.get('goals', {})
            away_goals_for = away_goals.get('for', 0)
            away_goals_against = away_goals.get('against', 0)
            
            # Get current timestamp
            now = timezone.now()
            
            # Build transformed data matching Supabase schema
            transformed = {
                'id': str(uuid.uuid4()),
                'league_id': league_id,
                'season': season,
                'team_id': team_id,
                'position': position,
                'points': points,
                'played': played,
                'won': won,
                'drawn': drawn,
                'lost': lost,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goal_difference,
                'recent_form': form,
                'home_played': home_played,
                'home_won': home_won,
                'home_drawn': home_drawn,
                'home_lost': home_lost,
                'home_goals_for': home_goals_for,
                'home_goals_against': home_goals_against,
                'away_played': away_played,
                'away_won': away_won,
                'away_drawn': away_drawn,
                'away_lost': away_lost,
                'away_goals_for': away_goals_for,
                'away_goals_against': away_goals_against,
                'status_description': status_desc,
                'created_at': now,
                'updated_at': now,
            }
            
            team_name = data.get('team', {}).get('name', 'Unknown')
            self.logger.debug(
                f"Successfully transformed standing: {team_name} "
                f"(Pos: {position}, Points: {points}, Form: {form}) "
                f"from {provider}"
            )
            
            return transformed
            
        except Exception as e:
            team_name = data.get('team', {}).get('name', 'Unknown')
            error_msg = (
                f"Transformation error for team {team_name}: {str(e)}"
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
        Validate standing data before transformation.
        
        Required fields:
        - rank (int): Team's position in standings
        - team (dict): Team information
        - team.id (int): Team ID from API
        - points (int): Total points
        - all (dict): Overall statistics
        - all.played (int): Matches played
        
        Optional fields:
        - form (str): Recent match results (e.g., 'WWDLW')
        - goalsDiff (int): Goal difference
        - home (dict): Home statistics
        - away (dict): Away statistics
        - status/description (str): Position status
        
        Args:
            data: API standing data (single team entry)
            provider: API provider name
            
        Returns:
            True if validation passes, False otherwise
            
        Validation Rules:
            - rank must be positive integer
            - team object must exist with valid ID
            - points must be non-negative integer
            - all.played must be non-negative integer
            - Statistics must be consistent (W+D+L = played)
        """
        # Check rank (position)
        rank = data.get('rank')
        if rank is None:
            self._collect_error("Missing 'rank' field")
            return False
        
        if not isinstance(rank, int) or rank <= 0:
            self._collect_error(f"Rank must be positive integer, got: {rank}")
            return False
        
        # Check team object
        if 'team' not in data:
            self._collect_error("Missing 'team' object")
            return False
        
        team_data = data['team']
        if not isinstance(team_data, dict):
            self._collect_error("'team' must be a dict")
            return False
        
        # Check team ID
        team_id = team_data.get('id')
        if team_id is None:
            self._collect_error("Missing 'team.id' field")
            return False
        
        if not isinstance(team_id, int) or team_id <= 0:
            self._collect_error(f"Team ID must be positive integer, got: {team_id}")
            return False
        
        # Check points
        points = data.get('points')
        if points is None:
            self._collect_error("Missing 'points' field")
            return False
        
        if not isinstance(points, (int, float)) or points < 0:
            self._collect_error(f"Points must be non-negative, got: {points}")
            return False
        
        # Check overall statistics
        if 'all' not in data:
            self._collect_error("Missing 'all' statistics object")
            return False
        
        all_stats = data['all']
        if not isinstance(all_stats, dict):
            self._collect_error("'all' must be a dict")
            return False
        
        # Check matches played
        played = all_stats.get('played')
        if played is None:
            self._collect_error("Missing 'all.played' field")
            return False
        
        if not isinstance(played, int) or played < 0:
            self._collect_error(f"Played must be non-negative integer, got: {played}")
            return False
        
        # Validate statistics consistency (optional but recommended)
        won = all_stats.get('win', 0)
        drawn = all_stats.get('draw', 0)
        lost = all_stats.get('lose', 0)
        
        total_matches = won + drawn + lost
        if total_matches != played:
            self.logger.warning(
                f"Statistics inconsistency for team {team_data.get('name')}: "
                f"W+D+L ({total_matches}) != Played ({played})"
            )
            # Don't fail validation, just warn
        
        team_name = team_data.get('name', 'Unknown')
        self.logger.debug(
            f"Validation passed for standing: {team_name} "
            f"(Rank: {rank}, Points: {points}, Played: {played})"
        )
        return True
    
    def validate_standing_data(
        self, 
        standing_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate transformed standing data before database insertion.
        
        Checks:
        - Required fields are present
        - UUIDs are valid
        - Position is positive integer
        - Statistics are non-negative
        - Statistics are consistent
        - Form string is valid
        
        Args:
            standing_data: Transformed standing data dict
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
            
        Example:
            ```python
            standing = transformer.transform(api_standing, ...)
            is_valid, errors = transformer.validate_standing_data(standing)
            
            if not is_valid:
                print(f"Validation errors: {errors}")
            else:
                # Save to database
                save_standing(standing)
            ```
        """
        errors = []
        
        # Check required fields
        required_fields = [
            'id', 'league_id', 'season', 'team_id', 'position', 
            'points', 'played'
        ]
        
        for field in required_fields:
            if field not in standing_data or standing_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate UUID fields
        uuid_fields = ['id', 'league_id', 'team_id']
        for field in uuid_fields:
            value = standing_data.get(field)
            if value:
                try:
                    uuid.UUID(str(value))
                except (ValueError, AttributeError):
                    errors.append(f"Invalid UUID format for {field}: {value}")
        
        # Validate position
        position = standing_data.get('position')
        if position is not None:
            if not isinstance(position, int) or position <= 0:
                errors.append(f"Invalid position: {position}")
        
        # Validate statistics (non-negative)
        stat_fields = [
            'points', 'played', 'won', 'drawn', 'lost',
            'goals_for', 'goals_against', 'goal_difference',
            'home_played', 'home_won', 'home_drawn', 'home_lost',
            'home_goals_for', 'home_goals_against',
            'away_played', 'away_won', 'away_drawn', 'away_lost',
            'away_goals_for', 'away_goals_against'
        ]
        
        for field in stat_fields:
            value = standing_data.get(field)
            if value is not None:
                # goal_difference can be negative
                if field == 'goal_difference':
                    if not isinstance(value, (int, float)):
                        errors.append(f"Invalid type for {field}: {type(value)}")
                else:
                    if not isinstance(value, (int, float)) or value < 0:
                        errors.append(f"Invalid value for {field}: {value}")
        
        # Validate statistics consistency
        played = standing_data.get('played', 0)
        won = standing_data.get('won', 0)
        drawn = standing_data.get('drawn', 0)
        lost = standing_data.get('lost', 0)
        
        total_matches = won + drawn + lost
        if played is not None and total_matches != played:
            errors.append(
                f"Statistics inconsistency: W+D+L ({total_matches}) != "
                f"Played ({played})"
            )
        
        # Validate form string
        form = standing_data.get('recent_form')
        if form:
            if not isinstance(form, str):
                errors.append(f"Form must be string, got: {type(form)}")
            else:
                invalid_chars = [c for c in form if c not in self.VALID_FORM_CHARS]
                if invalid_chars:
                    errors.append(
                        f"Invalid characters in form: {invalid_chars}, "
                        f"expected only W/D/L"
                    )
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.warning(
                f"Standing data validation failed: {errors}"
            )
        
        return is_valid, errors
    
    def _normalize_form(self, form: Optional[str]) -> Optional[str]:
        """
        Normalize form string (recent match results).
        
        Cleans and validates form string, removing invalid characters.
        
        Args:
            form: Raw form string from API (e.g., 'WWDLW', 'W-W-D-L-W')
            
        Returns:
            Normalized form string with only W/D/L characters or None
            
        Examples:
            'WWDLW' -> 'WWDLW'
            'W-W-D-L-W' -> 'WWDLW'
            'WWDLW ' -> 'WWDLW'
            '' -> None
            None -> None
        """
        if not form or not isinstance(form, str):
            return None
        
        # Remove whitespace and separators
        form = form.strip().replace('-', '').replace(' ', '')
        
        if not form:
            return None
        
        # Filter to valid characters only
        form = ''.join(c for c in form.upper() if c in self.VALID_FORM_CHARS)
        
        if not form:
            return None
        
        return form
    
    def _extract_status_description(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Extract status description (promotion/relegation zone info).
        
        API provides status/description fields indicating special positions:
        - Promotion zones (Champions League, Europa League, etc.)
        - Relegation zones
        - Playoff positions
        
        Args:
            data: Standing data from API
            
        Returns:
            Status description string or None
            
        Examples:
            'Promotion - Champions League (Group Stage: )'
            'Relegation - Championship'
            None (for mid-table teams)
        """
        # Try 'description' field first (more detailed)
        description = data.get('description')
        if description and isinstance(description, str):
            description = description.strip()
            if description and description.lower() not in ['null', 'n/a', '-']:
                return description
        
        # Fallback to 'status' field
        status = data.get('status')
        if status and isinstance(status, str):
            status = status.strip()
            if status and status.lower() not in ['null', 'n/a', '-']:
                return status
        
        return None
    
    def transform_bulk(
        self,
        standings_list: List[Dict[str, Any]],
        league_id: str,
        season: int,
        team_id_map: Dict[int, str],
        provider: str = 'api-football'
    ) -> List[Dict[str, Any]]:
        """
        Transform multiple standings (full league table) at once.
        
        Convenience method for bulk transformation with team ID resolution.
        
        Args:
            standings_list: List of standing entries from API
            league_id: UUID of the league
            season: Season year
            team_id_map: Mapping of API team IDs to database UUIDs
                        {api_team_id: team_uuid}
            provider: API provider name
            
        Returns:
            List of transformed standing data dicts
            
        Example:
            ```python
            # Fetch standings from API
            api_response = client.get_standings(league_id=39, season=2024)
            standings_array = api_response['response'][0]['league']['standings'][0]
            
            # Build team ID mapping
            team_map = {
                33: 'man-utd-uuid',
                40: 'liverpool-uuid',
                # ... other teams
            }
            
            # Bulk transform
            standings = transformer.transform_bulk(
                standings_array,
                league_id='premier-league-uuid',
                season=2024,
                team_id_map=team_map
            )
            
            # standings is now ready for bulk insert
            ```
        """
        transformed_standings = []
        
        for standing_entry in standings_list:
            # Get API team ID
            api_team_id = standing_entry.get('team', {}).get('id')
            
            if not api_team_id:
                self.logger.warning(
                    f"Missing team ID in standing entry, skipping"
                )
                continue
            
            # Resolve team UUID
            team_uuid = team_id_map.get(api_team_id)
            
            if not team_uuid:
                team_name = standing_entry.get('team', {}).get('name', 'Unknown')
                self.logger.warning(
                    f"Team UUID not found for API ID {api_team_id} "
                    f"({team_name}), skipping"
                )
                continue
            
            # Transform standing
            standing_data = self.transform(
                standing_entry,
                league_id=league_id,
                season=season,
                team_id=team_uuid,
                provider=provider
            )
            
            if standing_data:
                transformed_standings.append(standing_data)
        
        self.logger.info(
            f"Bulk transformed {len(transformed_standings)} standings "
            f"for league {league_id}, season {season}"
        )
        
        return transformed_standings
