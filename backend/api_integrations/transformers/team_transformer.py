"""
Team Transformer Module

Transforms external API responses (Football-Data.org, API-Football) into
internal Team model format with validation and country matching.

Supports multiple API providers with automatic format detection.
"""

from typing import Any, Dict, Optional
import logging
import uuid

from .base import BaseTransformer
from apps.core.models import Country


logger = logging.getLogger(__name__)


class TeamTransformer(BaseTransformer):
    """
    Transform API team data to internal Team model format.
    
    Supports multiple API providers:
    - Football-Data.org (primary)
    - API-Football (fallback)
    
    Features:
    - Country matching by name or code
    - Duplicate detection via external_id
    - Smart code generation from TLA or name
    - Optional field handling
    - Comprehensive validation
    
    Example:
        ```python
        transformer = TeamTransformer()
        
        # Football-Data.org format
        api_data = {
            'id': 66,
            'name': 'Manchester United FC',
            'tla': 'MUN',
            'crest': 'https://...',
            'founded': 1878,
            'area': {'name': 'England'}
        }
        
        team_data = transformer.transform(api_data, provider='football-data')
        # Returns: {'id': '...', 'name': 'Manchester United FC', ...}
        
        # Check for errors
        if transformer.has_errors():
            print(transformer.get_errors())
        ```
    """
    
    def __init__(self):
        """Initialize transformer with country cache."""
        super().__init__()
        self._country_cache: Dict[str, Optional[Country]] = {}
        self.logger.info("TeamTransformer initialized")
    
    def transform(
        self, 
        data: Dict[str, Any], 
        provider: str = 'football-data'
    ) -> Optional[Dict[str, Any]]:
        """
        Transform API response to Team model format.
        
        Args:
            data: Raw API response data
            provider: API provider ('football-data' or 'api-football')
            
        Returns:
            Transformed team data dict, or None if validation fails
            
        Example:
            ```python
            # Football-Data format
            team = transformer.transform(api_data, provider='football-data')
            
            # API-Football format
            team = transformer.transform(api_data, provider='api-football')
            ```
        """
        if not self.validate(data, provider):
            return None
        
        try:
            # Generate consistent external_id
            external_id = self._generate_external_id(data, provider)
            
            # Extract team code (TLA, code, or generate from name)
            code = self._extract_code(data, provider)
            
            # Match country (from area/country field)
            country_id = self._match_country(data, provider)
            
            # Extract optional fields
            logo = self._extract_logo(data, provider)
            website = self._extract_website(data, provider)
            founded = self._extract_founded(data, provider)
            market_value = None  # Future: extract from Transfermarkt
            
            # Build transformed data
            transformed = {
                'id': str(uuid.uuid4()),  # Generate new UUID for database
                'external_id': external_id,
                'name': data.get('name'),
                'code': code,
                'country_id': country_id,
                'logo': logo,
                'website': website,
                'founded': founded,
                'market_value': market_value,
                'is_active': True,
            }
            
            self.logger.debug(
                f"Successfully transformed team: {data.get('name')} "
                f"({provider})"
            )
            
            return transformed
            
        except Exception as e:
            error_msg = f"Transformation error for {data.get('name')}: {str(e)}"
            self._collect_error(error_msg)
            self.logger.exception(error_msg)
            return None
    
    def validate(self, data: Dict[str, Any], provider: str = 'football-data') -> bool:
        """
        Validate team data before transformation.
        
        Required fields:
        - id (int)
        - name (str)
        
        Optional fields vary by provider.
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ['id', 'name']
        if not self._validate_required_fields(data, required_fields):
            return False
        
        # Type validation
        if not self._validate_field_type(data['id'], int, 'id'):
            return False
        
        if not self._validate_field_type(data['name'], str, 'name'):
            return False
        
        # Name must not be empty
        if not data['name'].strip():
            self._collect_error("Team name cannot be empty")
            return False
        
        self.logger.debug(f"Validation passed for team: {data.get('name')}")
        return True
    
    def _generate_external_id(self, data: Dict[str, Any], provider: str) -> str:
        """
        Generate consistent external_id for duplicate detection.
        
        Format: {provider}-{api_id}
        Example: 'football-data-66' or 'api-football-33'
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            External ID string
        """
        api_id = data['id']
        return f"{provider}-{api_id}"
    
    def _extract_code(self, data: Dict[str, Any], provider: str) -> Optional[str]:
        """
        Extract or generate team code (3-letter abbreviation).
        
        Priority:
        1. TLA field (Football-Data) or code field (API-Football)
        2. Short name first 3 chars
        3. Full name first 3 chars (uppercase)
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            Team code (max 10 chars), or None
            
        Example:
            'Manchester United FC' -> 'MUN' (from TLA)
            'Real Madrid' -> 'RMA' (from TLA)
            'Unknown Team' -> 'UNK' (from name)
        """
        # Try TLA/code field first
        if provider == 'football-data':
            code = data.get('tla')
        else:  # api-football
            code = data.get('code')
        
        if code and len(code) <= 10:
            return code.upper()
        
        # Try short name
        short_name = data.get('shortName', '')
        if short_name and len(short_name) >= 3:
            return short_name[:3].upper()
        
        # Generate from full name
        name = data.get('name', '')
        if name:
            # Take first 3 letters of first word
            first_word = name.split()[0] if name.split() else name
            return first_word[:3].upper()
        
        return None
    
    def _match_country(self, data: Dict[str, Any], provider: str) -> Optional[str]:
        """
        Match team's country to database Country record.
        
        Uses country name from 'area' (Football-Data) or 'country' (API-Football).
        Caches results for performance.
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            Country UUID string, or None if not found
            
        Example:
            {'area': {'name': 'England'}} -> Country UUID for 'England'
            {'country': 'Spain'} -> Country UUID for 'Spain'
        """
        # Extract country name
        if provider == 'football-data':
            country_name = data.get('area', {}).get('name')
        else:  # api-football
            country_name = data.get('country')
        
        if not country_name:
            self.logger.debug(f"No country data for team: {data.get('name')}")
            return None
        
        # Check cache first
        if country_name in self._country_cache:
            country = self._country_cache[country_name]
            return str(country.id) if country else None
        
        # Query database
        try:
            country = Country.objects.filter(
                name__iexact=country_name
            ).first()
            
            # Cache result (even if None)
            self._country_cache[country_name] = country
            
            if country:
                self.logger.debug(f"Matched country: {country_name} -> {country.id}")
                return str(country.id)
            else:
                self.logger.warning(
                    f"Country not found in database: {country_name} "
                    f"(team: {data.get('name')})"
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Error matching country {country_name}: {str(e)}")
            return None
    
    def _extract_logo(self, data: Dict[str, Any], provider: str) -> Optional[str]:
        """
        Extract team logo URL.
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            Logo URL string, or None
        """
        if provider == 'football-data':
            return data.get('crest')
        else:  # api-football
            return data.get('logo')
    
    def _extract_website(self, data: Dict[str, Any], provider: str) -> Optional[str]:
        """
        Extract official website URL.
        
        Only available from Football-Data.org API.
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            Website URL string, or None
        """
        if provider == 'football-data':
            return data.get('website')
        # API-Football doesn't provide website
        return None
    
    def _extract_founded(self, data: Dict[str, Any], provider: str) -> Optional[int]:
        """
        Extract team founding year.
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            Founding year integer, or None
        """
        founded = data.get('founded')
        
        # Validate year is reasonable (1800-2100)
        if founded and isinstance(founded, int):
            if 1800 <= founded <= 2100:
                return founded
            else:
                self.logger.warning(
                    f"Invalid founding year {founded} for {data.get('name')}, "
                    f"ignoring"
                )
        
        return None
    
    def clear_cache(self) -> None:
        """
        Clear country cache.
        
        Useful when country data might have changed or when
        processing a new batch of teams.
        """
        self._country_cache.clear()
        self.logger.debug("Cleared country cache")
