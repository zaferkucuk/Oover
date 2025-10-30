"""
Football-Data.org API Client

Implementation of BaseAPIClient for Football-Data.org API.
Provides methods for fetching competitions and teams data.
"""

from typing import Dict, Any, List, Optional
import logging
import requests

from api_integrations.base import BaseAPIClient
from api_integrations.base.exceptions import APIError, ValidationError

logger = logging.getLogger(__name__)


class FootballDataClient(BaseAPIClient):
    """
    Client for Football-Data.org API v4.
    
    Provides methods to fetch:
    - Competitions (leagues/tournaments)
    - Teams in competitions
    - Team details
    
    Authentication:
        Uses X-Auth-Token header with API key from settings.
    
    Rate Limits:
        - Free tier: 10 requests/minute
        - Response headers include rate limit info
    
    Documentation:
        https://www.football-data.org/documentation/api
    
    Example:
        >>> from django.conf import settings
        >>> client = FootballDataClient(settings.FOOTBALL_DATA_CONFIG['api_key'])
        >>> competitions = client.get_competitions()
        >>> teams = client.get_teams_by_competition(2021)  # Premier League
        >>> team = client.get_team_details(57)  # Arsenal
    """
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize Football-Data.org client.
        
        Args:
            api_key: API authentication key from Football-Data.org
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        super().__init__(
            base_url='https://api.football-data.org/v4',
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        logger.info("Initialized FootballDataClient")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for Football-Data.org API requests.
        
        Returns:
            Dictionary with X-Auth-Token and Content-Type headers
        """
        return {
            'X-Auth-Token': self.api_key,
            'Content-Type': 'application/json',
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle and parse Football-Data.org API response.
        
        Football-Data.org returns JSON responses with this structure:
        - Success: { "count": N, "filters": {...}, "competitions": [...] }
        - Error: { "message": "Error message", "errorCode": 400 }
        
        Also extracts rate limit info from headers:
        - X-Requests-Available-Minute: Remaining requests this minute
        - X-RequestCounter-Reset: Seconds until counter resets
        
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
                f"Invalid JSON response from Football-Data.org: {str(e)}",
                status_code=response.status_code,
            )
        
        # Log rate limit info from headers
        requests_available = response.headers.get('X-Requests-Available-Minute')
        counter_reset = response.headers.get('X-RequestCounter-Reset')
        if requests_available:
            logger.debug(
                f"Rate limit: {requests_available} requests available "
                f"(resets in {counter_reset}s)"
            )
        
        # Check for error response
        if 'message' in data and 'errorCode' in data:
            error_msg = data.get('message', 'Unknown error')
            error_code = data.get('errorCode')
            logger.error(f"API error: {error_msg} (code: {error_code})")
            raise APIError(
                f"Football-Data.org API error: {error_msg}",
                status_code=error_code,
                response_data=data,
            )
        
        return data
    
    # ==================== Endpoint Methods ====================
    
    def get_competitions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all available competitions (leagues/tournaments).
        
        Returns major European and international competitions with details:
        - Competition ID, name, code, type, emblem
        - Area (country/region) information
        - Current season info
        
        Args:
            filters: Optional query parameters (e.g., {'areas': '2077,2081'})
                - areas: Comma-separated area IDs
                - plan: Filter by plan (TIER_ONE, TIER_TWO, TIER_THREE, TIER_FOUR)
        
        Returns:
            List of competition dictionaries with structure:
            {
                'id': 2021,
                'name': 'Premier League',
                'code': 'PL',
                'type': 'LEAGUE',
                'emblem': 'https://...',
                'area': {'id': 2072, 'name': 'England', ...},
                'currentSeason': {...}
            }
        
        Example:
            >>> competitions = client.get_competitions()
            >>> premier_league = [c for c in competitions if c['code'] == 'PL'][0]
        
        Documentation:
            https://www.football-data.org/documentation/api#competitions
        """
        logger.info(f"Fetching competitions (filters={filters})")
        
        response = self.get('competitions', params=filters)
        competitions = response.get('competitions', [])
        
        logger.info(f"Fetched {len(competitions)} competitions")
        return competitions
    
    def get_teams_by_competition(
        self, 
        competition_id: int,
        season: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all teams in a specific competition.
        
        Returns team data including:
        - Team ID, name, short name, TLA (three-letter abbreviation)
        - Club colors, crest URL, website
        - Venue, founded year
        - Current squad (if available)
        
        Args:
            competition_id: Competition ID (e.g., 2021 for Premier League)
            season: Optional season year (e.g., 2023 for 2023/24 season)
                    If not provided, returns current season
        
        Returns:
            List of team dictionaries with structure:
            {
                'id': 57,
                'name': 'Arsenal FC',
                'shortName': 'Arsenal',
                'tla': 'ARS',
                'crest': 'https://...',
                'address': 'Highbury House ...',
                'website': 'http://www.arsenal.com',
                'founded': 1886,
                'clubColors': 'Red / White',
                'venue': 'Emirates Stadium',
                'squad': [...]  # May not be available in free tier
            }
        
        Example:
            >>> teams = client.get_teams_by_competition(2021)  # Premier League
            >>> arsenal = [t for t in teams if t['tla'] == 'ARS'][0]
        
        Documentation:
            https://www.football-data.org/documentation/api#teams-for-competition
        """
        logger.info(
            f"Fetching teams for competition {competition_id} "
            f"(season={season or 'current'})"
        )
        
        endpoint = f"competitions/{competition_id}/teams"
        params = {'season': season} if season else None
        
        response = self.get(endpoint, params=params)
        teams = response.get('teams', [])
        
        logger.info(f"Fetched {len(teams)} teams")
        return teams
    
    def get_team_details(self, team_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific team.
        
        Returns comprehensive team data:
        - Basic info (name, crest, colors, etc.)
        - Current squad with player details (may be limited in free tier)
        - Active competitions
        - Running competitions
        
        Args:
            team_id: Team ID (e.g., 57 for Arsenal)
        
        Returns:
            Team dictionary with structure:
            {
                'id': 57,
                'name': 'Arsenal FC',
                'shortName': 'Arsenal',
                'tla': 'ARS',
                'crest': 'https://...',
                'address': 'Highbury House ...',
                'website': 'http://www.arsenal.com',
                'founded': 1886,
                'clubColors': 'Red / White',
                'venue': 'Emirates Stadium',
                'squad': [
                    {
                        'id': 3166,
                        'name': 'Martin Ødegaard',
                        'position': 'Midfielder',
                        'dateOfBirth': '1998-12-17',
                        'nationality': 'Norway'
                    },
                    ...
                ],
                'runningCompetitions': [...],
                'coach': {...}
            }
        
        Example:
            >>> team = client.get_team_details(57)  # Arsenal
            >>> print(f"{team['name']} founded in {team['founded']}")
        
        Documentation:
            https://www.football-data.org/documentation/api#team
        """
        logger.info(f"Fetching details for team {team_id}")
        
        team = self.get(f"teams/{team_id}")
        
        logger.info(f"Fetched team: {team.get('name', 'Unknown')}")
        return team
