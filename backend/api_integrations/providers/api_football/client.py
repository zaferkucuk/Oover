"""
API-Football Client

Implementation of BaseAPIClient for API-Football (RapidAPI).
Provides methods for fetching leagues and teams data via RapidAPI.
"""

from typing import Dict, Any, List, Optional
import logging
import requests

from api_integrations.base import BaseAPIClient
from api_integrations.base.exceptions import APIError, ValidationError

logger = logging.getLogger(__name__)


class APIFootballClient(BaseAPIClient):
    """
    Client for API-Football v3 via RapidAPI.
    
    Provides methods to fetch:
    - Leagues (optionally filtered by country)
    - Teams in leagues
    - Team details
    
    Authentication:
        Uses X-RapidAPI-Key and X-RapidAPI-Host headers with RapidAPI key.
    
    Rate Limits:
        - Free tier: 100 requests/day
        - Response headers include rate limit info (X-RateLimit-*)
    
    Documentation:
        https://www.api-football.com/documentation-v3
        https://rapidapi.com/api-sports/api/api-football
    
    Example:
        >>> from django.conf import settings
        >>> client = APIFootballClient(settings.API_FOOTBALL_CONFIG['api_key'])
        >>> leagues = client.get_leagues(country='England')
        >>> teams = client.get_teams_by_league(39, 2023)  # Premier League 2023
        >>> team = client.get_team_details(42)  # Arsenal
    """
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize API-Football client.
        
        Args:
            api_key: RapidAPI key for API-Football
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        super().__init__(
            base_url='https://v3.football.api-sports.io',
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        logger.info("Initialized APIFootballClient")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API-Football requests via RapidAPI.
        
        API-Football requires RapidAPI authentication headers:
        - X-RapidAPI-Key: Your RapidAPI subscription key
        - X-RapidAPI-Host: The API host (v3.football.api-sports.io)
        
        Returns:
            Dictionary with RapidAPI authentication headers
        """
        return {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io',
            'Content-Type': 'application/json',
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle and parse API-Football API response.
        
        API-Football returns JSON responses with this structure:
        - Success: { "get": "endpoint", "results": N, "response": [...] }
        - Error: { "message": "Error message", "errors": {...} }
        
        Also extracts rate limit info from headers:
        - X-RateLimit-Limit: Total requests allowed per day
        - X-RateLimit-Remaining: Remaining requests today
        
        Args:
            response: Raw requests.Response object
            
        Returns:
            Parsed response data as dictionary
            
        Raises:
            ValidationError: If response JSON is invalid
            APIError: If response contains an error message
        """
        try:
            data = response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValidationError(
                f"Invalid JSON response from API-Football: {str(e)}",
                status_code=response.status_code,
            )
        
        # Log rate limit info from headers
        rate_limit = response.headers.get('X-RateLimit-Limit')
        remaining = response.headers.get('X-RateLimit-Remaining')
        if rate_limit and remaining:
            logger.debug(
                f"Rate limit: {remaining}/{rate_limit} requests remaining today"
            )
        
        # Check for error response
        if 'errors' in data and data['errors']:
            errors = data.get('errors', {})
            message = data.get('message', 'Unknown error')
            logger.error(f"API error: {message}, errors: {errors}")
            raise APIError(
                f"API-Football API error: {message}",
                status_code=response.status_code,
                response_data=data,
            )
        
        return data
    
    # ==================== Endpoint Methods ====================
    
    def get_leagues(
        self, 
        country: Optional[str] = None,
        season: Optional[int] = None,
        league_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all available leagues, optionally filtered by country.
        
        Returns leagues with details:
        - League ID, name, type, logo
        - Country information
        - Season coverage
        
        Args:
            country: Optional country name filter (e.g., 'England', 'Spain')
            season: Optional season year filter (e.g., 2023)
            league_type: Optional type filter ('league', 'cup')
        
        Returns:
            List of league dictionaries with structure:
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
                    },
                    ...
                ]
            }
        
        Example:
            >>> leagues = client.get_leagues(country='England')
            >>> premier_league = [l for l in leagues if l['league']['name'] == 'Premier League'][0]
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Leagues/operation/get-leagues
        """
        logger.info(
            f"Fetching leagues (country={country}, season={season}, type={league_type})"
        )
        
        params = {}
        if country:
            params['country'] = country
        if season:
            params['season'] = season
        if league_type:
            params['type'] = league_type
        
        response = self.get('leagues', params=params if params else None)
        leagues = response.get('response', [])
        
        logger.info(f"Fetched {len(leagues)} leagues")
        return leagues
    
    def get_teams_by_league(
        self, 
        league_id: int,
        season: int
    ) -> List[Dict[str, Any]]:
        """
        Get all teams in a specific league and season.
        
        Returns team data including:
        - Team ID, name, code, logo
        - Country information
        - Venue details (name, address, city, capacity)
        
        Args:
            league_id: League ID (e.g., 39 for Premier League)
            season: Season year (e.g., 2023 for 2023/24 season)
        
        Returns:
            List of team dictionaries with structure:
            {
                'team': {
                    'id': 42,
                    'name': 'Arsenal',
                    'code': 'ARS',
                    'country': 'England',
                    'founded': 1886,
                    'national': False,
                    'logo': 'https://...'
                },
                'venue': {
                    'id': 494,
                    'name': 'Emirates Stadium',
                    'address': 'Queensland Road',
                    'city': 'London',
                    'capacity': 60383,
                    'surface': 'grass',
                    'image': 'https://...'
                }
            }
        
        Example:
            >>> teams = client.get_teams_by_league(39, 2023)  # Premier League 2023
            >>> arsenal = [t for t in teams if t['team']['code'] == 'ARS'][0]
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Teams/operation/get-teams
        """
        logger.info(f"Fetching teams for league {league_id}, season {season}")
        
        params = {
            'league': league_id,
            'season': season
        }
        
        response = self.get('teams', params=params)
        teams = response.get('response', [])
        
        logger.info(f"Fetched {len(teams)} teams")
        return teams
    
    def get_team_details(self, team_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific team.
        
        Returns comprehensive team data:
        - Basic info (name, code, logo, etc.)
        - Country and national team status
        - Venue details
        - Foundation year
        
        Args:
            team_id: Team ID (e.g., 42 for Arsenal)
        
        Returns:
            Team dictionary with structure:
            {
                'team': {
                    'id': 42,
                    'name': 'Arsenal',
                    'code': 'ARS',
                    'country': 'England',
                    'founded': 1886,
                    'national': False,
                    'logo': 'https://...'
                },
                'venue': {
                    'id': 494,
                    'name': 'Emirates Stadium',
                    'address': 'Queensland Road',
                    'city': 'London',
                    'capacity': 60383,
                    'surface': 'grass',
                    'image': 'https://...'
                }
            }
        
        Example:
            >>> team = client.get_team_details(42)  # Arsenal
            >>> print(f"{team['team']['name']} founded in {team['team']['founded']}")
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Teams/operation/get-teams
        """
        logger.info(f"Fetching details for team {team_id}")
        
        params = {'id': team_id}
        response = self.get('teams', params=params)
        
        # API-Football returns a list even for single team
        teams = response.get('response', [])
        if not teams:
            logger.warning(f"Team {team_id} not found")
            raise APIError(
                f"Team with ID {team_id} not found",
                status_code=404,
            )
        
        team = teams[0]
        logger.info(f"Fetched team: {team.get('team', {}).get('name', 'Unknown')}")
        return team
