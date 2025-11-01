"""
Country Transformer Module

Transforms external API responses (API-Football) into internal Country model format
with validation and data normalization.

Designed for one-time population and periodic sync operations.
"""

from typing import Any, Dict, Optional
import logging
import uuid
from django.utils import timezone

from .base import BaseTransformer


logger = logging.getLogger(__name__)


class CountryTransformer(BaseTransformer):
    """
    Transform API country data to internal Country model format.
    
    Currently supports:
    - API-Football (primary source for countries)
    
    Features:
    - ISO code validation (2-letter country codes)
    - Flag URL extraction and validation
    - Duplicate detection via external_id
    - Smart handling of missing data
    - Comprehensive validation
    
    Usage:
        ```python
        from api_integrations.transformers.country_transformer import CountryTransformer
        
        transformer = CountryTransformer()
        
        # API-Football format
        api_data = {
            'name': 'England',
            'code': 'GB',
            'flag': 'https://media.api-sports.io/flags/gb.svg'
        }
        
        country_data = transformer.transform(api_data)
        # Returns: {
        #     'id': '...',
        #     'name': 'England',
        #     'code': 'GB',
        #     'flag': 'https://...',
        #     'external_id': 'api-football-GB',
        #     ...
        # }
        
        # Check for validation errors
        if transformer.has_errors():
            print(transformer.get_errors())
        ```
    
    Notes:
        - Countries are relatively static data (yearly updates)
        - Should be cached for 1 year after initial sync
        - ~200 countries returned from API-Football
        - Some countries may not have active football leagues
    """
    
    def __init__(self):
        """Initialize country transformer."""
        super().__init__()
        self.logger.info("CountryTransformer initialized")
    
    def transform(
        self, 
        data: Dict[str, Any],
        provider: str = 'api-football'
    ) -> Optional[Dict[str, Any]]:
        """
        Transform API response to Country model format.
        
        Converts raw API-Football country data into format compatible with
        Supabase countries table schema.
        
        Args:
            data: Raw API response data with structure:
                {
                    'name': 'England',
                    'code': 'GB',  # ISO 3166-1 alpha-2
                    'flag': 'https://media.api-sports.io/flags/gb.svg'
                }
            provider: API provider ('api-football' - default)
            
        Returns:
            Transformed country data dict with structure:
                {
                    'id': 'uuid-string',
                    'name': 'England',
                    'code': 'GB',
                    'flag': 'https://...',
                    'external_id': 'api-football-GB',
                    'created_at': datetime,
                    'updated_at': datetime
                }
            Returns None if validation fails.
            
        Example:
            ```python
            # Transform single country
            country = transformer.transform({
                'name': 'Spain',
                'code': 'ES',
                'flag': 'https://media.api-sports.io/flags/es.svg'
            })
            
            # Bulk transform
            countries = [transformer.transform(c) for c in api_countries]
            countries = [c for c in countries if c is not None]  # Filter failed
            ```
        """
        if not self.validate(data, provider):
            return None
        
        try:
            # Generate consistent external_id for duplicate detection
            external_id = self._generate_external_id(data, provider)
            
            # Extract and normalize fields
            name = self._normalize_name(data.get('name'))
            code = self._normalize_code(data.get('code'))
            flag = self._extract_flag(data)
            
            # Get current timestamp for both created_at and updated_at
            now = timezone.now()
            
            # Build transformed data matching Supabase schema
            transformed = {
                'id': str(uuid.uuid4()),  # Generate new UUID for database
                'name': name,
                'code': code,
                'flag': flag,
                'external_id': external_id,
                'created_at': now,
                'updated_at': now,
            }
            
            self.logger.debug(
                f"Successfully transformed country: {name} ({code}) from {provider}"
            )
            
            return transformed
            
        except Exception as e:
            error_msg = (
                f"Transformation error for country {data.get('name')}: {str(e)}"
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
        Validate country data before transformation.
        
        Required fields:
        - name (str): Country name
        - code (str): ISO 3166-1 alpha-2 code (2 letters)
        
        Optional fields:
        - flag (str): Flag image URL
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            True if validation passes, False otherwise
            
        Validation Rules:
            - Name must be non-empty string
            - Code must be exactly 2 uppercase letters (ISO standard)
            - Flag URL must be valid URL format if provided
        """
        # Check required fields exist
        required_fields = ['name', 'code']
        if not self._validate_required_fields(data, required_fields):
            return False
        
        # Validate field types
        if not self._validate_field_type(data['name'], str, 'name'):
            return False
        
        if not self._validate_field_type(data['code'], str, 'code'):
            return False
        
        # Name must not be empty
        if not data['name'].strip():
            self._collect_error("Country name cannot be empty")
            return False
        
        # Code must be exactly 2 characters (ISO 3166-1 alpha-2)
        code = data['code'].strip()
        if len(code) != 2:
            self._collect_error(
                f"Country code must be 2 characters (ISO 3166-1 alpha-2), "
                f"got: {code} ({len(code)} chars)"
            )
            return False
        
        # Code must be alphabetic
        if not code.isalpha():
            self._collect_error(
                f"Country code must contain only letters, got: {code}"
            )
            return False
        
        # Validate flag URL if provided
        flag = data.get('flag')
        if flag and not self._validate_url(flag):
            self.logger.warning(
                f"Invalid flag URL for {data['name']}: {flag}, will be set to None"
            )
            # Don't fail validation, just warn
        
        self.logger.debug(
            f"Validation passed for country: {data.get('name')} ({data.get('code')})"
        )
        return True
    
    def _generate_external_id(
        self, 
        data: Dict[str, Any],
        provider: str
    ) -> str:
        """
        Generate consistent external_id for duplicate detection.
        
        Format: {provider}-{country_code}
        
        Using country code instead of numeric ID because:
        - Codes are stable across API versions
        - Human-readable for debugging
        - Matches ISO 3166-1 alpha-2 standard
        
        Args:
            data: API response data
            provider: API provider name
            
        Returns:
            External ID string
            
        Examples:
            'api-football-GB' (England)
            'api-football-ES' (Spain)
            'api-football-TR' (Turkey)
        """
        code = data['code'].upper()
        return f"{provider}-{code}"
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize country name for consistency.
        
        Operations:
        - Strip leading/trailing whitespace
        - Ensure title case for consistency
        
        Args:
            name: Raw country name from API
            
        Returns:
            Normalized country name
            
        Examples:
            'england' -> 'England'
            ' SPAIN ' -> 'Spain'
            'TURKEY' -> 'Turkey'
        """
        return name.strip().title()
    
    def _normalize_code(self, code: str) -> str:
        """
        Normalize country code to ISO 3166-1 alpha-2 standard.
        
        Operations:
        - Strip whitespace
        - Convert to uppercase
        
        Args:
            code: Raw country code from API
            
        Returns:
            Normalized 2-letter uppercase country code
            
        Examples:
            'gb' -> 'GB'
            ' es ' -> 'ES'
            'TR' -> 'TR'
        """
        return code.strip().upper()
    
    def _extract_flag(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Extract and validate country flag URL.
        
        Handles missing flags gracefully by returning None.
        Invalid URLs are logged but don't fail transformation.
        
        Args:
            data: API response data
            
        Returns:
            Flag URL string, or None if not available/invalid
            
        Examples:
            Valid: 'https://media.api-sports.io/flags/gb.svg'
            Missing: None
            Invalid: None (with warning logged)
        """
        flag = data.get('flag')
        
        if not flag:
            return None
        
        # Validate URL format
        if not self._validate_url(flag):
            self.logger.warning(
                f"Invalid flag URL for {data.get('name')}: {flag}"
            )
            return None
        
        return flag
    
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
