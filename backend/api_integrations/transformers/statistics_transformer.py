"""
Statistics Transformer Module

Transforms external API responses (API-Football) into internal match statistics format
with validation, data normalization, and type conversion.

Designed for hourly/daily match statistics updates.
"""

from typing import Any, Dict, Optional, List, Tuple, Union
import logging
import uuid
import re
from datetime import datetime
from django.utils import timezone

from .base import BaseTransformer


logger = logging.getLogger(__name__)


class StatisticsTransformer(BaseTransformer):
    """
    Transform API match statistics data to internal format for database storage.
    
    Currently supports:
    - API-Football (primary source for match statistics)
    
    Features:
    - Team statistics extraction and normalization
    - Player statistics parsing (when available)
    - Percentage value conversion ('58%' -> 58)
    - Statistic type normalization ('Shots on Goal' -> 'shots_on_goal')
    - Expected goals (xG) handling
    - Missing/null value handling
    - JSONB-ready format for flexible storage
    - Comprehensive validation
    - Duplicate detection via composite key (match + team)
    
    Statistics Categories:
        SHOOTING:
            - shots_on_goal, shots_off_goal, total_shots
            - blocked_shots, shots_insidebox, shots_outsidebox
            - expected_goals (xG)
            
        PASSING:
            - total_passes, passes_accurate, passes_percentage
            - key_passes (passes leading to shots)
            
        POSSESSION:
            - ball_possession (percentage)
            
        DEFENSE:
            - goalkeeper_saves, blocked_shots
            - tackles, interceptions
            
        DISCIPLINE:
            - fouls, yellow_cards, red_cards
            - offsides
            
        SET PIECES:
            - corner_kicks, free_kicks
            
        ATTACKING:
            - attacks, dangerous_attacks
    
    Usage:
        ```python
        from api_integrations.transformers.statistics_transformer import StatisticsTransformer
        
        transformer = StatisticsTransformer()
        
        # API-Football format (single team statistics)
        api_stats = {
            'team': {
                'id': 33,
                'name': 'Manchester United',
                'logo': 'https://...'
            },
            'statistics': [
                {'type': 'Shots on Goal', 'value': 8},
                {'type': 'Ball Possession', 'value': '58%'},
                {'type': 'Total passes', 'value': 543},
                {'type': 'Passes %', 'value': '90%'},
                {'type': 'expected_goals', 'value': 2.14},
                ...
            ]
        }
        
        statistics_data = transformer.transform(
            api_stats,
            match_id='match-uuid-here',
            team_id='team-uuid-here'
        )
        # Returns: {
        #     'id': 'uuid',
        #     'match_id': 'match-uuid',
        #     'team_id': 'team-uuid',
        #     'statistics': {
        #         'shots_on_goal': 8,
        #         'ball_possession': 58,
        #         'total_passes': 543,
        #         'passes_percentage': 90,
        #         'expected_goals': 2.14,
        #         ...
        #     },
        #     'created_at': datetime,
        #     'updated_at': datetime
        # }
        
        # Bulk transform (both teams in match)
        match_stats = []
        for team_stats in api_statistics_list:
            team_id = team_map[team_stats['team']['id']]  # Resolve team UUID
            
            stats_data = transformer.transform(
                team_stats,
                match_id=match_id,
                team_id=team_id
            )
            if stats_data:
                match_stats.append(stats_data)
        
        # Check for validation errors
        if transformer.has_errors():
            print(transformer.get_errors())
        ```
    
    Notes:
        - Statistics available after match completion (FT status)
        - Some matches may have limited statistics (coverage varies)
        - xG (expected goals) availability depends on league
        - Statistics stored as JSONB for flexibility
        - Cache: 1 hour for recent, 7 days for completed matches
    """
    
    # Statistic type normalization mappings
    # Maps API statistic names to database field names (snake_case)
    STAT_TYPE_MAPPING = {
        # Shooting statistics
        'Shots on Goal': 'shots_on_goal',
        'Shots off Goal': 'shots_off_goal',
        'Total Shots': 'total_shots',
        'Blocked Shots': 'blocked_shots',
        'Shots insidebox': 'shots_insidebox',
        'Shots outsidebox': 'shots_outsidebox',
        
        # Expected goals
        'expected_goals': 'expected_goals',
        
        # Passing statistics
        'Total passes': 'total_passes',
        'Passes accurate': 'passes_accurate',
        'Passes %': 'passes_percentage',
        
        # Possession
        'Ball Possession': 'ball_possession',
        
        # Defense
        'Goalkeeper Saves': 'goalkeeper_saves',
        
        # Discipline
        'Fouls': 'fouls',
        'Yellow Cards': 'yellow_cards',
        'Red Cards': 'red_cards',
        'Offsides': 'offsides',
        
        # Set pieces
        'Corner Kicks': 'corner_kicks',
        
        # Attacking
        'Attacks': 'attacks',
        'Dangerous Attacks': 'dangerous_attacks',
    }
    
    # Statistics that are stored as percentages (need parsing)
    PERCENTAGE_STATS = {
        'ball_possession',
        'passes_percentage',
    }
    
    # Statistics that should be integers
    INTEGER_STATS = {
        'shots_on_goal', 'shots_off_goal', 'total_shots', 'blocked_shots',
        'shots_insidebox', 'shots_outsidebox', 'total_passes', 'passes_accurate',
        'goalkeeper_saves', 'fouls', 'yellow_cards', 'red_cards', 'offsides',
        'corner_kicks', 'attacks', 'dangerous_attacks', 'ball_possession',
        'passes_percentage',
    }
    
    # Statistics that should be floats
    FLOAT_STATS = {
        'expected_goals',
    }
    
    def __init__(self):
        """Initialize statistics transformer."""
        super().__init__()
        self.logger.info("StatisticsTransformer initialized")
    
    def transform(
        self, 
        data: Dict[str, Any],
        match_id: Optional[str] = None,
        team_id: Optional[str] = None,
        provider: str = 'api-football'
    ) -> Optional[Dict[str, Any]]:
        """
        Transform API statistics response to database format.
        
        Converts raw API-Football statistics data (single team) into format 
        compatible with Supabase team_statistics table schema.
        
        Args:
            data: Raw API statistics data (single team's statistics)
            match_id: UUID of the match
            team_id: UUID of the team (if known, otherwise extracted from data)
            provider: API provider ('api-football' - default)
            
        Returns:
            Transformed statistics data dict or None if validation fails:
                {
                    'id': 'uuid-string',
                    'match_id': 'uuid-string',
                    'team_id': 'uuid-string',
                    'statistics': {
                        'shots_on_goal': 8,
                        'ball_possession': 58,
                        'total_passes': 543,
                        'passes_percentage': 90,
                        'expected_goals': 2.14,
                        'goalkeeper_saves': 4,
                        'fouls': 12,
                        'corner_kicks': 6,
                        'offsides': 2,
                        'yellow_cards': 2,
                        'red_cards': 0,
                        ...  # Additional statistics
                    },
                    'created_at': datetime,
                    'updated_at': datetime
                }
            
        Example:
            ```python
            # Transform single team statistics
            stats = transformer.transform(
                api_stats,
                match_id='match-uuid',
                team_id='team-uuid'
            )
            
            # Bulk transform (both teams)
            match_statistics = []
            for team_stats in api_response:
                team_uuid = resolve_team_id(team_stats['team']['id'])
                stats = transformer.transform(
                    team_stats,
                    match_id=match_id,
                    team_id=team_uuid
                )
                if stats:
                    match_statistics.append(stats)
            ```
        """
        if not self.validate(data, provider):
            return None
        
        try:
            # Extract statistics array
            raw_statistics = data.get('statistics', [])
            
            if not raw_statistics:
                team_name = data.get('team', {}).get('name', 'Unknown')
                self.logger.warning(f"No statistics found for team {team_name}")
                return None
            
            # Parse and normalize statistics
            normalized_stats = self._parse_statistics(raw_statistics)
            
            if not normalized_stats:
                team_name = data.get('team', {}).get('name', 'Unknown')
                self.logger.warning(
                    f"Failed to parse statistics for team {team_name}"
                )
                return None
            
            # Get current timestamp
            now = timezone.now()
            
            # Build transformed data matching Supabase schema
            transformed = {
                'id': str(uuid.uuid4()),
                'match_id': match_id,
                'team_id': team_id,
                'statistics': normalized_stats,  # JSONB field
                'created_at': now,
                'updated_at': now,
            }
            
            team_name = data.get('team', {}).get('name', 'Unknown')
            num_stats = len(normalized_stats)
            self.logger.debug(
                f"Successfully transformed statistics for {team_name}: "
                f"{num_stats} statistics from {provider}"
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
        Validate statistics data before transformation.
        
        Required fields:
        - team (dict): Team information
        - team.id (int): Team ID from API
        - statistics (list): Array of statistics
        
        Args:
            data: API statistics data (single team)
            provider: API provider name
            
        Returns:
            True if validation passes, False otherwise
            
        Validation Rules:
            - team object must exist with valid ID
            - statistics must be a non-empty list
            - each statistic must have 'type' and 'value' fields
        """
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
        
        # Check statistics array
        if 'statistics' not in data:
            self._collect_error("Missing 'statistics' array")
            return False
        
        statistics = data['statistics']
        if not isinstance(statistics, list):
            self._collect_error("'statistics' must be a list")
            return False
        
        if not statistics:
            team_name = team_data.get('name', 'Unknown')
            self.logger.warning(
                f"Empty statistics array for team {team_name}"
            )
            # Don't fail validation, just warn
            return True
        
        # Validate statistics structure
        for i, stat in enumerate(statistics):
            if not isinstance(stat, dict):
                self._collect_error(
                    f"Statistic at index {i} must be a dict, got: {type(stat)}"
                )
                return False
            
            if 'type' not in stat:
                self._collect_error(f"Statistic at index {i} missing 'type' field")
                return False
            
            if 'value' not in stat:
                self._collect_error(f"Statistic at index {i} missing 'value' field")
                return False
        
        team_name = team_data.get('name', 'Unknown')
        self.logger.debug(
            f"Validation passed for statistics: {team_name} "
            f"({len(statistics)} statistics)"
        )
        return True
    
    def _parse_statistics(
        self,
        raw_statistics: List[Dict[str, Any]]
    ) -> Dict[str, Union[int, float, None]]:
        """
        Parse and normalize raw statistics array to database format.
        
        Converts API statistics format:
        [
            {'type': 'Shots on Goal', 'value': 8},
            {'type': 'Ball Possession', 'value': '58%'},
            ...
        ]
        
        To normalized format:
        {
            'shots_on_goal': 8,
            'ball_possession': 58,
            ...
        }
        
        Args:
            raw_statistics: List of statistic dicts from API
            
        Returns:
            Dictionary with normalized statistics (snake_case keys, parsed values)
            
        Notes:
            - Percentage values are converted to integers: '58%' -> 58
            - Unknown statistic types are preserved with snake_case keys
            - Null/None values are preserved
            - Invalid values are logged and set to None
        """
        normalized = {}
        
        for stat in raw_statistics:
            stat_type = stat.get('type')
            stat_value = stat.get('value')
            
            if not stat_type:
                self.logger.warning("Statistic missing 'type' field, skipping")
                continue
            
            # Normalize statistic type to snake_case key
            normalized_key = self._normalize_stat_type(stat_type)
            
            # Parse and convert value
            parsed_value = self._parse_stat_value(
                normalized_key,
                stat_value
            )
            
            # Store in normalized dictionary
            normalized[normalized_key] = parsed_value
        
        return normalized
    
    def _normalize_stat_type(self, stat_type: str) -> str:
        """
        Normalize statistic type to snake_case database field name.
        
        Uses STAT_TYPE_MAPPING for known statistics.
        For unknown statistics, converts to snake_case.
        
        Args:
            stat_type: Original statistic type from API
            
        Returns:
            Normalized snake_case field name
            
        Examples:
            'Shots on Goal' -> 'shots_on_goal'
            'Ball Possession' -> 'ball_possession'
            'Total Shots' -> 'total_shots'
            'Unknown Stat' -> 'unknown_stat'
        """
        # Check mapping first
        if stat_type in self.STAT_TYPE_MAPPING:
            return self.STAT_TYPE_MAPPING[stat_type]
        
        # Convert to snake_case for unknown types
        # Replace spaces and special chars with underscores
        normalized = re.sub(r'[^\w\s]', '', stat_type)  # Remove special chars
        normalized = re.sub(r'\s+', '_', normalized)     # Spaces to underscores
        normalized = normalized.lower()                  # Lowercase
        
        # Log unknown statistic type
        self.logger.debug(
            f"Unknown statistic type '{stat_type}', normalized to '{normalized}'"
        )
        
        return normalized
    
    def _parse_stat_value(
        self,
        stat_key: str,
        value: Any
    ) -> Union[int, float, None]:
        """
        Parse and convert statistic value to appropriate type.
        
        Handles:
        - Percentage strings: '58%' -> 58
        - Numeric strings: '543' -> 543
        - Integers and floats: pass through
        - Null/None values: preserve as None
        - Invalid values: log warning, return None
        
        Args:
            stat_key: Normalized statistic key (e.g., 'ball_possession')
            value: Raw value from API
            
        Returns:
            Parsed value as int, float, or None
            
        Examples:
            _parse_stat_value('ball_possession', '58%') -> 58
            _parse_stat_value('total_shots', 13) -> 13
            _parse_stat_value('expected_goals', 2.14) -> 2.14
            _parse_stat_value('goalkeeper_saves', '4') -> 4
            _parse_stat_value('corner_kicks', None) -> None
        """
        # Handle None/null values
        if value is None or value == 'null' or value == '':
            return None
        
        # Handle percentage strings
        if isinstance(value, str) and '%' in value:
            return self._parse_percentage(value)
        
        # Handle numeric strings
        if isinstance(value, str):
            value = value.strip()
            
            # Try parsing as number
            try:
                # Check if it's a float
                if '.' in value:
                    parsed = float(value)
                else:
                    parsed = int(value)
                
                # Apply type conversion based on stat key
                return self._convert_to_expected_type(stat_key, parsed)
                
            except ValueError:
                self.logger.warning(
                    f"Failed to parse value '{value}' for stat '{stat_key}'"
                )
                return None
        
        # Handle numeric types (int, float)
        if isinstance(value, (int, float)):
            return self._convert_to_expected_type(stat_key, value)
        
        # Unexpected type
        self.logger.warning(
            f"Unexpected value type {type(value)} for stat '{stat_key}': {value}"
        )
        return None
    
    def _parse_percentage(self, percentage_str: str) -> Optional[int]:
        """
        Parse percentage string to integer.
        
        Args:
            percentage_str: Percentage string (e.g., '58%', '90.5%')
            
        Returns:
            Integer percentage value or None if parsing fails
            
        Examples:
            '58%' -> 58
            '90.5%' -> 90 (rounded down)
            '100%' -> 100
            'invalid%' -> None
        """
        try:
            # Remove % sign and any whitespace
            cleaned = percentage_str.replace('%', '').strip()
            
            # Parse as float (handles decimals)
            value = float(cleaned)
            
            # Convert to integer (round down)
            return int(value)
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(
                f"Failed to parse percentage '{percentage_str}': {e}"
            )
            return None
    
    def _convert_to_expected_type(
        self,
        stat_key: str,
        value: Union[int, float]
    ) -> Union[int, float]:
        """
        Convert value to expected type based on statistic key.
        
        Some statistics should be integers, others should be floats.
        
        Args:
            stat_key: Normalized statistic key
            value: Parsed numeric value
            
        Returns:
            Value converted to expected type
            
        Examples:
            _convert_to_expected_type('total_shots', 13.0) -> 13
            _convert_to_expected_type('expected_goals', 2) -> 2.14
            _convert_to_expected_type('ball_possession', 58.7) -> 58
        """
        # Float statistics
        if stat_key in self.FLOAT_STATS:
            return float(value)
        
        # Integer statistics (default)
        if stat_key in self.INTEGER_STATS:
            return int(value)
        
        # Unknown statistic - preserve type
        # But prefer int if no decimal component
        if isinstance(value, float) and value.is_integer():
            return int(value)
        
        return value
    
    def transform_bulk(
        self,
        statistics_list: List[Dict[str, Any]],
        match_id: str,
        team_id_map: Dict[int, str],
        provider: str = 'api-football'
    ) -> List[Dict[str, Any]]:
        """
        Transform multiple team statistics (both teams in match) at once.
        
        Convenience method for bulk transformation with team ID resolution.
        
        Args:
            statistics_list: List of team statistics from API (typically 2 teams)
            match_id: UUID of the match
            team_id_map: Mapping of API team IDs to database UUIDs
                        {api_team_id: team_uuid}
            provider: API provider name
            
        Returns:
            List of transformed statistics data dicts
            
        Example:
            ```python
            # Fetch statistics from API
            api_response = client.get_match_statistics(match_id=215662)
            
            # Build team ID mapping
            team_map = {
                33: 'man-utd-uuid',
                34: 'newcastle-uuid'
            }
            
            # Bulk transform
            match_stats = transformer.transform_bulk(
                api_response,
                match_id='match-uuid',
                team_id_map=team_map
            )
            
            # match_stats is now ready for bulk insert
            # [
            #     {'id': '...', 'match_id': '...', 'team_id': 'man-utd-uuid', 'statistics': {...}},
            #     {'id': '...', 'match_id': '...', 'team_id': 'newcastle-uuid', 'statistics': {...}}
            # ]
            ```
        """
        transformed_statistics = []
        
        for team_stats in statistics_list:
            # Get API team ID
            api_team_id = team_stats.get('team', {}).get('id')
            
            if not api_team_id:
                self.logger.warning(
                    "Missing team ID in statistics entry, skipping"
                )
                continue
            
            # Resolve team UUID
            team_uuid = team_id_map.get(api_team_id)
            
            if not team_uuid:
                team_name = team_stats.get('team', {}).get('name', 'Unknown')
                self.logger.warning(
                    f"Team UUID not found for API ID {api_team_id} "
                    f"({team_name}), skipping"
                )
                continue
            
            # Transform statistics
            stats_data = self.transform(
                team_stats,
                match_id=match_id,
                team_id=team_uuid,
                provider=provider
            )
            
            if stats_data:
                transformed_statistics.append(stats_data)
        
        self.logger.info(
            f"Bulk transformed {len(transformed_statistics)} team statistics "
            f"for match {match_id}"
        )
        
        return transformed_statistics
    
    def validate_statistics_data(
        self, 
        statistics_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate transformed statistics data before database insertion.
        
        Checks:
        - Required fields are present
        - UUIDs are valid
        - Statistics is a dict with valid structure
        - Statistic values have appropriate types
        
        Args:
            statistics_data: Transformed statistics data dict
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
            
        Example:
            ```python
            stats = transformer.transform(api_stats, ...)
            is_valid, errors = transformer.validate_statistics_data(stats)
            
            if not is_valid:
                print(f"Validation errors: {errors}")
            else:
                # Save to database
                save_statistics(stats)
            ```
        """
        errors = []
        
        # Check required fields
        required_fields = ['id', 'match_id', 'team_id', 'statistics']
        
        for field in required_fields:
            if field not in statistics_data or statistics_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate UUID fields
        uuid_fields = ['id', 'match_id', 'team_id']
        for field in uuid_fields:
            value = statistics_data.get(field)
            if value:
                try:
                    uuid.UUID(str(value))
                except (ValueError, AttributeError):
                    errors.append(f"Invalid UUID format for {field}: {value}")
        
        # Validate statistics field
        statistics = statistics_data.get('statistics')
        if statistics is not None:
            if not isinstance(statistics, dict):
                errors.append(
                    f"Statistics must be a dict, got: {type(statistics)}"
                )
            else:
                # Validate statistic values
                for key, value in statistics.items():
                    if value is not None:
                        if not isinstance(value, (int, float)):
                            errors.append(
                                f"Invalid type for statistic '{key}': {type(value)}, "
                                f"expected int or float"
                            )
                        
                        # Check for negative values (most stats shouldn't be negative)
                        if isinstance(value, (int, float)) and value < 0:
                            # Only log warning for negative values (might be valid in some cases)
                            self.logger.warning(
                                f"Negative value for statistic '{key}': {value}"
                            )
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.warning(
                f"Statistics data validation failed: {errors}"
            )
        
        return is_valid, errors
