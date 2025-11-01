"""
League Transformer Module

Transforms external API responses (API-Football) into internal League model format
with validation and data normalization.

Designed for seasonal updates and periodic sync operations.
"""

from typing import Any, Dict, Optional, List
import logging
import uuid
from django.utils import timezone

from .base import BaseTransformer


logger = logging.getLogger(__name__)


class LeagueTransformer(BaseTransformer):
    """
    Transform API league data to internal League model format.
    
    Currently supports:
    - API-Football (primary source for leagues)
    
    Features:
    - League ID and name validation
    - Country relationship mapping via external_id
    - Season data parsing (current season detection)
    - Logo URL extraction and validation
    - League type normalization (League/Cup)
    - Confederation detection from country
    - Tier detection from league name patterns
    - Duplicate detection via external_id
    - Smart handling of missing data
    - Comprehensive validation
    
    Usage:
        ```python
        from api_integrations.transformers.league_transformer import LeagueTransformer
        
        transformer = LeagueTransformer()
        
        # API-Football format
        api_data = {
            'league': {
                'id': 39,
                'name': 'Premier League',
                'type': 'League',
                'logo': 'https://...'
            },
            'country': {
                'name': 'England',
                'code': 'GB',
                'flag': 'https://...'
            },
            'seasons': [
                {
                    'year': 2023,
                    'start': '2023-08-11',
                    'end': '2024-05-19',
                    'current': True
                }
            ]
        }
        
        league_data = transformer.transform(api_data, country_id='uuid-here')
        # Returns: {
        #     'id': '...',
        #     'name': 'Premier League',
        #     'country_id': 'uuid-here',
        #     'logo': 'https://...',
        #     'external_id': 'api-football-39',
        #     'tier': 1,
        #     'confederation': 'UEFA',
        #     ...
        # }
        
        # Check for validation errors
        if transformer.has_errors():
            print(transformer.get_errors())
        ```
    
    Notes:
        - Leagues update seasonally (6-month cache recommended)
        - ~800 leagues available from API-Football
        - Season data is parsed but stored separately in future
        - Country relationship required for proper mapping
        - Some leagues are multi-country (e.g., Champions League)
    """
    
    # Confederation mapping from country codes
    CONFEDERATION_MAP = {
        # UEFA (Europe)
        'UEFA': ['GB', 'ES', 'DE', 'IT', 'FR', 'PT', 'NL', 'BE', 'TR', 'GR', 
                 'RU', 'UA', 'PL', 'CZ', 'AT', 'CH', 'SE', 'NO', 'DK', 'RO',
                 'HR', 'RS', 'BG', 'SK', 'SI', 'HU', 'FI', 'IE', 'AL', 'BA',
                 'CY', 'EE', 'FO', 'GE', 'IS', 'XK', 'LV', 'LI', 'LT', 'LU',
                 'MK', 'MD', 'ME', 'MT', 'SM', 'AD', 'AZ', 'BY', 'GI'],
        
        # CONMEBOL (South America)
        'CONMEBOL': ['AR', 'BR', 'UY', 'CL', 'CO', 'EC', 'PE', 'VE', 'PY', 'BO'],
        
        # CONCACAF (North/Central America & Caribbean)
        'CONCACAF': ['US', 'MX', 'CA', 'CR', 'HN', 'SV', 'GT', 'PA', 'JM', 'CU',
                     'TT', 'HT', 'BS', 'BB', 'BZ', 'GY', 'SR', 'NI', 'DO', 'KN',
                     'AG', 'DM', 'LC', 'VC', 'GD', 'AW', 'BQ', 'CW', 'SX', 'MQ',
                     'GP', 'GF', 'MF', 'BM', 'KY', 'TC', 'VG', 'AI', 'MS', 'PM'],
        
        # AFC (Asia)
        'AFC': ['JP', 'KR', 'CN', 'SA', 'IR', 'AE', 'QA', 'IQ', 'UZ', 'AU',
                'SY', 'OM', 'JO', 'LB', 'PS', 'BH', 'KW', 'VN', 'TH', 'MY',
                'ID', 'SG', 'PH', 'KH', 'MM', 'LA', 'BN', 'TL', 'MV', 'IN',
                'PK', 'BD', 'AF', 'NP', 'BT', 'LK', 'TJ', 'TM', 'KG', 'KZ',
                'MN', 'HK', 'MO', 'TW', 'GU', 'MP', 'NC', 'PG', 'SB', 'FJ',
                'VU', 'WS', 'CK', 'TO', 'AS', 'PF', 'KI'],
        
        # CAF (Africa)
        'CAF': ['EG', 'MA', 'TN', 'DZ', 'NG', 'GH', 'CI', 'CM', 'SN', 'ML',
                'BF', 'ZA', 'KE', 'UG', 'TZ', 'ET', 'ZW', 'ZM', 'MW', 'MZ',
                'AO', 'GA', 'CG', 'CD', 'CF', 'TD', 'NE', 'BJ', 'TG', 'LR',
                'SL', 'GN', 'GW', 'GM', 'MR', 'CV', 'ST', 'GQ', 'RW', 'BI',
                'DJ', 'SO', 'ER', 'SD', 'SS', 'LY', 'NA', 'BW', 'LS', 'SZ',
                'SC', 'MU', 'KM', 'MG', 'RE', 'YT'],
        
        # OFC (Oceania)
        'OFC': ['NZ', 'FJ', 'NC', 'PG', 'SB', 'VU', 'WS', 'CK', 'TO', 'AS',
                'PF', 'KI', 'TV', 'NR', 'NU', 'TK'],
    }
    
    def __init__(self):
        """Initialize league transformer."""
        super().__init__()
        self.logger.info("LeagueTransformer initialized")
    
    def transform(
        self, 
        data: Dict[str, Any],
        country_id: Optional[str] = None,
        sport_id: str = 'football',
        provider: str = 'api-football'
    ) -> Optional[Dict[str, Any]]:
        """
        Transform API response to League model format.
        
        Converts raw API-Football league data into format compatible with
        Supabase leagues table schema.
        
        Args:
            data: Raw API response data with structure:
                {
                    'league': {
                        'id': 39,
                        'name': 'Premier League',
                        'type': 'League',
                        'logo': 'https://...'
                    },
                    'country': {
                        'name': 'England',
                        'code': 'GB',
                        'flag': 'https://...'
                    },
                    'seasons': [
                        {
                            'year': 2023,
                            'start': '2023-08-11',
                            'end': '2024-05-19',
                            'current': True
                        }
                    ]
                }
            country_id: UUID of the country this league belongs to
            sport_id: Sport identifier (default: 'football')
            provider: API provider ('api-football' - default)
            
        Returns:
            Transformed league data dict with structure:
                {
                    'id': 'uuid-string',
                    'name': 'Premier League',
                    'sport_id': 'football',
                    'country_id': 'uuid-string',
                    'tier': 1,
                    'confederation': 'UEFA',
                    'logo': 'https://...',
                    'external_id': 'api-football-39',
                    'is_active': True,
                    'created_at': datetime,
                    'updated_at': datetime
                }
            Returns None if validation fails.
            
        Example:
            ```python
            # Transform single league
            league = transformer.transform(
                api_data,
                country_id='country-uuid-here',
                sport_id='football'
            )
            
            # Bulk transform
            leagues = [
                transformer.transform(l, country_id=country_map[l['country']['code']])
                for l in api_leagues
            ]
            leagues = [l for l in leagues if l is not None]  # Filter failed
            ```
        """
        if not self.validate(data, provider):
            return None
        
        try:
            # Extract league sub-object
            league_data = data.get('league', {})
            country_data = data.get('country', {})
            
            # Generate consistent external_id for duplicate detection
            external_id = self._generate_external_id(league_data, provider)
            
            # Extract and normalize fields
            name = self._normalize_name(league_data.get('name'))
            logo = self._extract_logo(league_data)
            
            # Detect tier from league name
            tier = self._detect_tier(name)
            
            # Detect confederation from country code
            confederation = self._detect_confederation(country_data.get('code'))
            
            # Get current timestamp for both created_at and updated_at
            now = timezone.now()
            
            # Build transformed data matching Supabase schema
            transformed = {
                'id': str(uuid.uuid4()),  # Generate new UUID for database
                'name': name,
                'sport_id': sport_id,
                'country_id': country_id,  # Required for FK
                'tier': tier,
                'confederation': confederation,
                'logo': logo,
                'external_id': external_id,
                'is_active': True,
                'created_at': now,
                'updated_at': now,
            }
            
            self.logger.debug(
                f"Successfully transformed league: {name} "
                f"(ID: {league_data.get('id')}) from {provider}"
            )
            
            return transformed
            
        except Exception as e:
            error_msg = (
                f"Transformation error for league {data.get('league', {}).get('name')}: "
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
        Validate league data before transformation.
        
        Required fields:
        - league.id (int): League ID from API
        - league.name (str): League name
        - league.type (str): League type (League/Cup)
        - country.name (str): Country name
        - country.code (str): Country code
        
        Optional fields:
        - league.logo (str): Logo URL
        - seasons (list): Season information
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            True if validation passes, False otherwise
            
        Validation Rules:
            - league sub-object must exist
            - league.id must be positive integer
            - league.name must be non-empty string
            - league.type must be valid type
            - country sub-object must exist
            - country.code must be valid
        """
        # Check league sub-object exists
        if 'league' not in data:
            self._collect_error("Missing 'league' object in response")
            return False
        
        league_data = data['league']
        
        # Check required league fields
        required_league_fields = ['id', 'name', 'type']
        for field in required_league_fields:
            if field not in league_data:
                self._collect_error(f"Missing required field: league.{field}")
                return False
        
        # Validate league ID
        league_id = league_data.get('id')
        if not isinstance(league_id, int) or league_id <= 0:
            self._collect_error(
                f"League ID must be positive integer, got: {league_id}"
            )
            return False
        
        # Validate league name
        name = league_data.get('name')
        if not isinstance(name, str) or not name.strip():
            self._collect_error("League name cannot be empty")
            return False
        
        # Validate league type
        league_type = league_data.get('type')
        valid_types = ['League', 'Cup']
        if league_type not in valid_types:
            self.logger.warning(
                f"Unexpected league type: {league_type} for {name}, "
                f"expected one of: {valid_types}"
            )
            # Don't fail validation, just warn
        
        # Check country sub-object exists
        if 'country' not in data:
            self.logger.warning(
                f"Missing 'country' object for league {name}, "
                "will be set to NULL (international league?)"
            )
            # Don't fail - some leagues are international
        else:
            country_data = data['country']
            
            # Validate country code
            country_code = country_data.get('code')
            if not country_code or not isinstance(country_code, str):
                self.logger.warning(
                    f"Invalid country code for league {name}: {country_code}"
                )
                # Don't fail - country can be NULL
        
        # Validate logo URL if provided
        logo = league_data.get('logo')
        if logo and not self._validate_url(logo):
            self.logger.warning(
                f"Invalid logo URL for {name}: {logo}, will be set to None"
            )
            # Don't fail validation, just warn
        
        self.logger.debug(
            f"Validation passed for league: {name} (ID: {league_id})"
        )
        return True
    
    def _generate_external_id(
        self, 
        league_data: Dict[str, Any],
        provider: str
    ) -> str:
        """
        Generate consistent external_id for duplicate detection.
        
        Format: {provider}-{league_id}
        
        Using league ID instead of name because:
        - IDs are stable across API versions
        - Names can change (e.g., sponsorship changes)
        - IDs are unique and numeric
        
        Args:
            league_data: League sub-object from API response
            provider: API provider name
            
        Returns:
            External ID string
            
        Examples:
            'api-football-39' (Premier League)
            'api-football-140' (La Liga)
            'api-football-78' (Bundesliga)
        """
        league_id = league_data['id']
        return f"{provider}-{league_id}"
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize league name for consistency.
        
        Operations:
        - Strip leading/trailing whitespace
        - Preserve original casing (league names are proper nouns)
        
        Args:
            name: Raw league name from API
            
        Returns:
            Normalized league name
            
        Examples:
            ' Premier League ' -> 'Premier League'
            'La Liga' -> 'La Liga'
            'Bundesliga  ' -> 'Bundesliga'
        """
        return name.strip()
    
    def _extract_logo(self, league_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract and validate league logo URL.
        
        Handles missing logos gracefully by returning None.
        Invalid URLs are logged but don't fail transformation.
        
        Args:
            league_data: League sub-object from API response
            
        Returns:
            Logo URL string, or None if not available/invalid
            
        Examples:
            Valid: 'https://media.api-sports.io/football/leagues/39.png'
            Missing: None
            Invalid: None (with warning logged)
        """
        logo = league_data.get('logo')
        
        if not logo:
            return None
        
        # Validate URL format
        if not self._validate_url(logo):
            self.logger.warning(
                f"Invalid logo URL for {league_data.get('name')}: {logo}"
            )
            return None
        
        return logo
    
    def _detect_tier(self, name: str) -> Optional[int]:
        """
        Detect league tier/division from name.
        
        Uses pattern matching on league name to identify tier:
        - Tier 1: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, etc.
        - Tier 2: Championship, Segunda División, 2. Bundesliga, Serie B, Ligue 2
        - Tier 3: League One, Segunda División B, 3. Liga, Serie C
        - etc.
        
        Args:
            name: League name
            
        Returns:
            Tier number (1-5) or None if cannot be determined
            
        Examples:
            'Premier League' -> 1
            'Championship' -> 2
            'League One' -> 3
            'Champions League' -> None (international competition)
        """
        name_lower = name.lower()
        
        # International competitions have no tier
        international_keywords = [
            'champions league', 'europa league', 'world cup', 
            'euro', 'copa america', 'copa libertadores', 'confederation'
        ]
        if any(keyword in name_lower for keyword in international_keywords):
            return None
        
        # Tier 1 patterns
        tier1_patterns = [
            'premier league', 'la liga', 'bundesliga', 'serie a', 'ligue 1',
            'primeira liga', 'eredivisie', 'süper lig', 'süper lig',
            'primera división', 'first division', 'division 1',
            'primeira division', 'pro league'
        ]
        if any(pattern in name_lower for pattern in tier1_patterns):
            # But exclude "segunda" division variations
            if 'segunda' not in name_lower and '2.' not in name_lower:
                return 1
        
        # Tier 2 patterns
        tier2_patterns = [
            'championship', 'segunda división', 'segunda division', 
            '2. bundesliga', 'serie b', 'ligue 2', 'segunda liga',
            'championship', 'second division', 'division 2', '2nd division'
        ]
        if any(pattern in name_lower for pattern in tier2_patterns):
            return 2
        
        # Tier 3 patterns
        tier3_patterns = [
            'league one', 'tercera división', '3. liga', 'serie c',
            'third division', 'division 3', '3rd division'
        ]
        if any(pattern in name_lower for pattern in tier3_patterns):
            return 3
        
        # Tier 4 patterns
        tier4_patterns = [
            'league two', 'cuarta división', '4. liga', 'serie d',
            'fourth division', 'division 4', '4th division'
        ]
        if any(pattern in name_lower for pattern in tier4_patterns):
            return 4
        
        # Default to None if cannot determine
        return None
    
    def _detect_confederation(self, country_code: Optional[str]) -> Optional[str]:
        """
        Detect football confederation from country code.
        
        Maps country codes to their respective football confederations:
        - UEFA: Europe
        - CONMEBOL: South America
        - CONCACAF: North/Central America & Caribbean
        - AFC: Asia
        - CAF: Africa
        - OFC: Oceania
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
            
        Returns:
            Confederation code or None if cannot be determined
            
        Examples:
            'GB' -> 'UEFA' (England)
            'ES' -> 'UEFA' (Spain)
            'BR' -> 'CONMEBOL' (Brazil)
            'US' -> 'CONCACAF' (United States)
            None -> None (international/multi-country leagues)
        """
        if not country_code:
            return None
        
        # Normalize country code
        country_code = country_code.upper().strip()
        
        # Search in confederation map
        for confederation, countries in self.CONFEDERATION_MAP.items():
            if country_code in countries:
                return confederation
        
        # Log warning if country not found in any confederation
        self.logger.warning(
            f"Country code {country_code} not found in any confederation map"
        )
        return None
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Basic validation checks:
        - Starts with http:// or https://
        - Contains at least one dot (domain)
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL appears valid, False otherwise
        """
        if not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # Must start with http:// or https://
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        # Must contain at least one dot (domain)
        if '.' not in url:
            return False
        
        return True
    
    def parse_current_season(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse current season information from API response.
        
        Extracts the currently active season from the seasons array.
        Season data will be used for future league_seasons table.
        
        Args:
            data: Full API response data with seasons array
            
        Returns:
            Current season dict or None:
                {
                    'year': 2023,
                    'start': '2023-08-11',
                    'end': '2024-05-19',
                    'current': True
                }
                
        Example:
            ```python
            season = transformer.parse_current_season(api_data)
            if season:
                print(f"Current season: {season['year']}")
            ```
        
        Note:
            Season data is NOT stored in leagues table.
            This method is for future use when league_seasons table is implemented.
        """
        seasons = data.get('seasons', [])
        
        if not seasons:
            return None
        
        # Find current season
        for season in seasons:
            if season.get('current'):
                return season
        
        # If no current season found, return the latest one
        if seasons:
            return seasons[-1]
        
        return None
