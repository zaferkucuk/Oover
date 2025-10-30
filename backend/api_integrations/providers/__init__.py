"""
API Providers Module

Implementations of specific API providers:
- football_data_org/: Football-Data.org API (primary)
- api_football/: API-Football via RapidAPI (fallback)
- transfermarkt/: Web scraping fallback (future)

This module exports:
- VALID_PROVIDERS: List of valid provider names for validation
- FootballDataProvider: Football-Data.org API provider
- ApiFootballProvider: API-Football provider
"""

from .football_data_org.provider import FootballDataProvider
from .api_football.provider import ApiFootballProvider

# Valid provider names for validation and selection
# Used by management commands and API endpoints
VALID_PROVIDERS = [
    'football-data',  # Football-Data.org API (primary)
    'api-football',   # API-Football via RapidAPI (fallback)
]

# Export all providers and constants
__all__ = [
    'VALID_PROVIDERS',
    'FootballDataProvider',
    'ApiFootballProvider',
]
