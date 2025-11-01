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
    - Countries (with flags and codes)
    - Leagues (optionally filtered by country)
    - Teams in leagues
    - Team details
    
    Authentication:
        Uses X-RapidAPI-Key and X-RapidAPI-Host headers with RapidAPI key.
    
    Rate Limits:
        - Free tier: 100 requests/day
        - Pro Plan: 7,500 requests/day, 150 requests/minute
        - Response headers include rate limit info (X-RateLimit-*)
    
    Documentation:
        https://www.api-football.com/documentation-v3
        https://rapidapi.com/api-sports/api/api-football
    
    Example:
        >>> from django.conf import settings
        >>> client = APIFootballClient(settings.API_FOOTBALL_CONFIG['api_key'])
        >>> countries = client.get_countries()  # Get all countries
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
    
    def get_countries(
        self,
        name: Optional[str] = None,
        code: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all available countries from API-Football.
        
        Returns countries with details:
        - Country name, code (ISO 3166-1 alpha-2)
        - Country flag image URL
        
        This endpoint is typically called once to populate the countries table,
        as countries rarely change. Results should be cached for extended periods
        (recommended: 1 year).
        
        Args:
            name: Optional exact country name filter (e.g., 'England', 'Spain')
            code: Optional ISO code filter (e.g., 'GB', 'ES')
            search: Optional search term for partial matching
        
        Returns:
            List of country dictionaries with structure:
            {
                'name': 'England',
                'code': 'GB',  # ISO 3166-1 alpha-2 code
                'flag': 'https://media.api-sports.io/flags/gb.svg'
            }
            
        Example:
            >>> # Get all countries
            >>> countries = client.get_countries()
            >>> print(f"Total countries: {len(countries)}")
            
            >>> # Filter by name
            >>> england = client.get_countries(name='England')
            >>> print(england[0]['code'])  # 'GB'
            
            >>> # Filter by code
            >>> spain = client.get_countries(code='ES')
            >>> print(spain[0]['name'])  # 'Spain'
            
            >>> # Search for countries
            >>> german = client.get_countries(search='german')
            >>> # Returns Germany and any countries with 'german' in name
        
        Notes:
            - This endpoint typically returns ~200 countries
            - Use caching to minimize API calls (1 year TTL recommended)
            - Countries are relatively static data
            - Some countries may not have active leagues
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Countries/operation/get-countries
        """
        logger.info(
            f"Fetching countries (name={name}, code={code}, search={search})"
        )
        
        # Build query parameters
        params = {}
        if name:
            params['name'] = name
        if code:
            params['code'] = code
        if search:
            params['search'] = search
        
        # Make API request
        response = self.get('countries', params=params if params else None)
        countries = response.get('response', [])
        
        logger.info(f"Fetched {len(countries)} countries")
        return countries
    
    def get_leagues(
        self,
        league_id: Optional[int] = None,
        country: Optional[str] = None,
        season: Optional[int] = None,
        league_type: Optional[str] = None,
        current: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all available leagues from API-Football with comprehensive filtering.
        
        Returns leagues with complete details:
        - League ID, name, type, logo
        - Country information (name, code, flag)
        - Season coverage (years, dates, current status)
        - Competition format information
        
        This endpoint provides access to ~800 leagues worldwide. Use filters to
        narrow results. For frequently accessed leagues, implement caching with
        6-month TTL (seasonal data stability).
        
        Args:
            league_id: Optional specific league ID filter (e.g., 39 for Premier League)
            country: Optional country name filter (e.g., 'England', 'Spain', 'Germany')
            season: Optional season year filter (e.g., 2023 for 2023/24 season)
            league_type: Optional type filter ('league' for regular leagues, 'cup' for cups)
            current: Optional filter for currently active leagues (True/False)
            search: Optional search term for partial name matching
        
        Returns:
            List of league dictionaries with structure:
            {
                'league': {
                    'id': 39,                    # Unique league identifier
                    'name': 'Premier League',    # League name
                    'type': 'League',            # Type: League/Cup
                    'logo': 'https://...'        # League logo URL
                },
                'country': {
                    'name': 'England',           # Country name
                    'code': 'GB',                # ISO 3166-1 alpha-2 code
                    'flag': 'https://...'        # Country flag URL
                },
                'seasons': [
                    {
                        'year': 2023,            # Season year
                        'start': '2023-08-11',   # Season start date
                        'end': '2024-05-19',     # Season end date
                        'current': True,         # Is this the current season?
                        'coverage': {            # Data coverage details
                            'fixtures': {
                                'events': True,
                                'lineups': True,
                                'statistics_fixtures': True,
                                'statistics_players': True
                            },
                            'standings': True,
                            'players': True,
                            'top_scorers': True,
                            'top_assists': True,
                            'top_cards': True,
                            'injuries': True,
                            'predictions': True,
                            'odds': False
                        }
                    },
                    ...  # Historical seasons
                ]
            }
        
        Examples:
            >>> # Get all leagues
            >>> all_leagues = client.get_leagues()
            >>> print(f"Total leagues: {len(all_leagues)}")
            
            >>> # Get specific league by ID
            >>> premier_league = client.get_leagues(league_id=39)
            >>> print(premier_league[0]['league']['name'])  # 'Premier League'
            
            >>> # Get all leagues in a country
            >>> england_leagues = client.get_leagues(country='England')
            >>> # Returns Premier League, Championship, League One, etc.
            
            >>> # Get leagues for specific season
            >>> season_2023 = client.get_leagues(season=2023)
            >>> # Returns all leagues with 2023/24 season
            
            >>> # Get only regular leagues (exclude cups)
            >>> regular_leagues = client.get_leagues(league_type='league')
            
            >>> # Get currently active leagues
            >>> active_leagues = client.get_leagues(current=True)
            
            >>> # Search for leagues
            >>> champions = client.get_leagues(search='Champions')
            >>> # Returns UEFA Champions League, AFC Champions League, etc.
            
            >>> # Combined filters: England's regular leagues, current season
            >>> england_current = client.get_leagues(
            ...     country='England',
            ...     league_type='league',
            ...     current=True
            ... )
        
        Notes:
            - This endpoint returns ~800 leagues worldwide
            - Use caching to minimize API calls (6 months TTL recommended)
            - Leagues data is seasonal - update at season start
            - Season structure varies by league (calendar year vs split seasons)
            - Some leagues may have limited data coverage (check 'coverage' field)
            - Historical seasons available for most major leagues
            - League IDs are stable and can be hardcoded for major leagues:
                * 39: Premier League (England)
                * 140: La Liga (Spain)
                * 78: Bundesliga (Germany)
                * 135: Serie A (Italy)
                * 61: Ligue 1 (France)
            
        Common Use Cases:
            1. Initial setup: Fetch all leagues, populate database
            2. Seasonal update: Fetch leagues with current season
            3. Country-specific: Get leagues for target countries
            4. League details: Fetch specific league with all seasons
        
        Performance Tips:
            - Fetching all leagues (~800) counts as 1 API call
            - Use filters to reduce response size
            - Cache results for 6 months (seasonal stability)
            - Update at season boundaries (typically July-August)
        
        Error Handling:
            - Returns empty list if no leagues match filters
            - Raises APIError if API request fails
            - Raises ValidationError if response format is invalid
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Leagues/operation/get-leagues
        """
        logger.info(
            f"Fetching leagues (id={league_id}, country={country}, season={season}, "
            f"type={league_type}, current={current}, search={search})"
        )
        
        # Build query parameters
        params = {}
        if league_id is not None:
            params['id'] = league_id
        if country:
            params['country'] = country
        if season is not None:
            params['season'] = season
        if league_type:
            params['type'] = league_type
        if current is not None:
            params['current'] = 'true' if current else 'false'
        if search:
            params['search'] = search
        
        # Make API request
        response = self.get('leagues', params=params if params else None)
        leagues = response.get('response', [])
        
        # Validate response
        if leagues is None:
            logger.warning("API returned None for leagues response")
            leagues = []
        
        # Log results with context
        if league_id:
            if leagues:
                league_name = leagues[0].get('league', {}).get('name', 'Unknown')
                logger.info(f"Fetched league: {league_name} (ID: {league_id})")
            else:
                logger.warning(f"League with ID {league_id} not found")
        else:
            logger.info(f"Fetched {len(leagues)} leagues")
            if leagues and len(leagues) < 10:
                # Log league names for small result sets
                names = [l.get('league', {}).get('name', 'Unknown') for l in leagues]
                logger.debug(f"Leagues: {', '.join(names)}")
        
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
