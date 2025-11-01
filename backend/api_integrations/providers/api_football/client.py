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
    - Fixtures/Matches (with comprehensive filtering)
    - Standings (league tables with rankings)
    
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
        >>> fixtures = client.get_fixtures(league_id=39, season=2024)  # PL fixtures
        >>> standings = client.get_standings(league_id=39, season=2024)  # PL table
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
    
    def get_fixtures(
        self,
        fixture_id: Optional[int] = None,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        team_id: Optional[int] = None,
        status: Optional[str] = None,
        timezone: Optional[str] = None,
        venue_id: Optional[int] = None,
        round: Optional[str] = None,
        last: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get fixtures (matches) from API-Football with comprehensive filtering.
        
        Fixtures are the core of match prediction systems. This endpoint provides
        access to past, present, and future matches with complete details:
        - Match status, dates, and times
        - Teams, venues, and referees
        - Scores (halftime, fulltime, extra time, penalties)
        - Live match events (goals, cards, substitutions)
        
        🎯 CRITICAL: This is the most frequently used endpoint in the system
        🔄 UPDATE FREQUENCY:
            - Upcoming matches: Daily (schedule changes, postponements)
            - Live matches: Real-time (minute-by-minute updates)
            - Completed matches: One-time final result
        
        📊 SCALE: ~10,000+ fixtures per season across top European leagues
        
        ⚠️ CACHING STRATEGY (IMPORTANT):
            - Upcoming matches: 1 hour (schedule can change)
            - Live matches: 5 minutes (rapid updates)
            - Completed matches: 7 days (final results are stable)
            - Historical matches: 30 days (rarely accessed)
        
        Args:
            fixture_id: Optional specific fixture ID (e.g., 215662)
                Use when you have the exact fixture identifier.
                
            league_id: Optional league filter (e.g., 39 for Premier League)
                Returns all fixtures in the specified league.
                Combine with season for complete league schedule.
                
            season: Optional season year filter (e.g., 2024 for 2024/25 season)
                Must be combined with league_id.
                Season format: 2024 represents 2024/25 season.
                
            date: Optional specific date filter (format: 'YYYY-MM-DD')
                Returns all fixtures on this exact date.
                Useful for daily updates and match day operations.
                Example: '2024-12-15' returns all matches on Dec 15, 2024
                
            date_from: Optional start date for range (format: 'YYYY-MM-DD')
                Must be combined with date_to.
                Maximum range: typically 1 year.
                Example: '2024-12-01' to '2024-12-31' for December matches
                
            date_to: Optional end date for range (format: 'YYYY-MM-DD')
                Must be combined with date_from.
                Inclusive: includes matches on this date.
                
            team_id: Optional team filter (e.g., 33 for Manchester United)
                Returns all fixtures where this team plays (home or away).
                Useful for team-specific analysis.
                
            status: Optional match status filter. Valid values:
                - 'TBD': Time To Be Defined
                - 'NS': Not Started (scheduled)
                - '1H': First Half
                - 'HT': Halftime
                - '2H': Second Half
                - 'ET': Extra Time
                - 'P': Penalties
                - 'FT': Finished
                - 'AET': After Extra Time
                - 'PEN': Finished after penalties
                - 'BT': Break Time (between extra time periods)
                - 'SUSP': Match Suspended
                - 'INT': Match Interrupted
                - 'PST': Match Postponed
                - 'CANC': Match Cancelled
                - 'ABD': Match Abandoned
                - 'AWD': Technical Loss
                - 'WO': WalkOver
                - 'LIVE': All live statuses (1H, HT, 2H, ET, BT, P)
                
            timezone: Optional timezone for fixture dates (e.g., 'Europe/London')
                Converts fixture times to specified timezone.
                Default: UTC if not specified.
                Common values: 'Europe/London', 'America/New_York', 'Asia/Tokyo'
                
            venue_id: Optional venue filter (e.g., 556 for Old Trafford)
                Returns all fixtures played at this venue.
                Useful for venue-specific analysis.
                
            round: Optional round filter (e.g., 'Regular Season - 15')
                Returns fixtures from specific round/gameweek.
                Format varies by league and competition structure.
                Examples: 'Regular Season - 15', 'Quarter-finals', 'Group A - 3'
                
            last: Optional limit for recent fixtures (e.g., 10)
                Returns the last N fixtures for a team.
                Must be combined with team_id.
                Useful for recent form analysis.
        
        Returns:
            List of fixture dictionaries with comprehensive structure:
            {
                'fixture': {
                    'id': 215662,                           # Unique fixture identifier
                    'referee': 'Michael Oliver',            # Match referee
                    'timezone': 'UTC',                      # Timezone of dates
                    'date': '2024-01-14T16:30:00+00:00',  # Match datetime (ISO format)
                    'timestamp': 1705247400,                # Unix timestamp
                    'periods': {                            # Period timestamps
                        'first': 1705247400,
                        'second': 1705251000
                    },
                    'venue': {
                        'id': 556,
                        'name': 'Old Trafford',
                        'city': 'Manchester'
                    },
                    'status': {
                        'long': 'Match Finished',           # Full status description
                        'short': 'FT',                      # Short status code
                        'elapsed': 90                       # Minutes elapsed
                    }
                },
                'league': {
                    'id': 39,
                    'name': 'Premier League',
                    'country': 'England',
                    'logo': 'https://...',
                    'flag': 'https://...',
                    'season': 2024,
                    'round': 'Regular Season - 20'
                },
                'teams': {
                    'home': {
                        'id': 33,
                        'name': 'Manchester United',
                        'logo': 'https://...',
                        'winner': True                      # True/False/None
                    },
                    'away': {
                        'id': 34,
                        'name': 'Newcastle',
                        'logo': 'https://...',
                        'winner': False
                    }
                },
                'goals': {
                    'home': 2,
                    'away': 1
                },
                'score': {                                  # Detailed scoring
                    'halftime': {
                        'home': 1,
                        'away': 0
                    },
                    'fulltime': {
                        'home': 2,
                        'away': 1
                    },
                    'extratime': {                          # Null if no extra time
                        'home': None,
                        'away': None
                    },
                    'penalty': {                            # Null if no penalties
                        'home': None,
                        'away': None
                    }
                },
                'events': [                                 # Live events (goals, cards, subs)
                    {
                        'time': {
                            'elapsed': 23,
                            'extra': None
                        },
                        'team': {
                            'id': 33,
                            'name': 'Manchester United',
                            'logo': 'https://...'
                        },
                        'player': {
                            'id': 882,
                            'name': 'Bruno Fernandes'
                        },
                        'assist': {
                            'id': 903,
                            'name': 'Marcus Rashford'
                        },
                        'type': 'Goal',                     # Goal, Card, Subst, Var
                        'detail': 'Normal Goal',            # Detailed event type
                        'comments': None
                    },
                    ...
                ]
            }
        
        Examples:
            >>> # 1. Get specific fixture by ID
            >>> fixture = client.get_fixtures(fixture_id=215662)
            >>> print(f"{fixture[0]['teams']['home']['name']} vs "
            ...       f"{fixture[0]['teams']['away']['name']}")
            
            >>> # 2. Get all fixtures for a league's current season
            >>> premier_league = client.get_fixtures(league_id=39, season=2024)
            >>> print(f"Total fixtures: {len(premier_league)}")
            >>> # ~380 fixtures for full Premier League season
            
            >>> # 3. Get today's matches across all leagues
            >>> from datetime import date
            >>> today = date.today().isoformat()
            >>> todays_matches = client.get_fixtures(date=today)
            >>> print(f"Matches today: {len(todays_matches)}")
            
            >>> # 4. Get fixtures for date range (e.g., entire month)
            >>> december_matches = client.get_fixtures(
            ...     date_from='2024-12-01',
            ...     date_to='2024-12-31'
            ... )
            >>> print(f"December fixtures: {len(december_matches)}")
            
            >>> # 5. Get all fixtures for a specific team
            >>> man_utd = client.get_fixtures(team_id=33, season=2024)
            >>> # Returns all Man United matches in 2024/25 season
            
            >>> # 6. Get team's last N matches (recent form)
            >>> last_5 = client.get_fixtures(team_id=33, last=5)
            >>> # Returns Manchester United's last 5 completed matches
            
            >>> # 7. Get all live/ongoing matches
            >>> live_matches = client.get_fixtures(status='LIVE')
            >>> for match in live_matches:
            ...     print(f"{match['teams']['home']['name']} "
            ...           f"{match['goals']['home']}-{match['goals']['away']} "
            ...           f"{match['teams']['away']['name']} "
            ...           f"({match['fixture']['status']['elapsed']}')")
            
            >>> # 8. Get all finished matches on a date
            >>> finished_today = client.get_fixtures(
            ...     date=today,
            ...     status='FT'
            ... )
            
            >>> # 9. Get scheduled (not started) matches
            >>> upcoming = client.get_fixtures(
            ...     date=today,
            ...     status='NS'
            ... )
            
            >>> # 10. Get fixtures at a specific venue
            >>> old_trafford = client.get_fixtures(venue_id=556, season=2024)
            >>> # All matches at Old Trafford in 2024/25
            
            >>> # 11. Get fixtures for specific round/gameweek
            >>> gw_15 = client.get_fixtures(
            ...     league_id=39,
            ...     season=2024,
            ...     round='Regular Season - 15'
            ... )
            >>> # All Premier League gameweek 15 matches
            
            >>> # 12. Get team fixtures with custom timezone
            >>> arsenal_uk = client.get_fixtures(
            ...     team_id=42,
            ...     season=2024,
            ...     timezone='Europe/London'
            ... )
            >>> # Arsenal fixtures with UK times
            
            >>> # 13. Get next 10 matches for a team
            >>> next_matches = client.get_fixtures(
            ...     team_id=33,
            ...     status='NS',
            ...     last=10
            ... )
            
            >>> # 14. Get postponed matches
            >>> postponed = client.get_fixtures(
            ...     league_id=39,
            ...     season=2024,
            ...     status='PST'
            ... )
            
            >>> # 15. Complex filter: Team's home fixtures for date range
            >>> man_utd_home = [
            ...     f for f in client.get_fixtures(
            ...         team_id=33,
            ...         date_from='2024-12-01',
            ...         date_to='2024-12-31'
            ...     )
            ...     if f['teams']['home']['id'] == 33
            ... ]
        
        Common Use Cases:
            1. **Daily Updates**: Fetch today's fixtures with date=today
            2. **Live Tracking**: Poll live matches with status='LIVE', cache 5min
            3. **Team Analysis**: Get team's recent matches with team_id + last
            4. **League Schedule**: Fetch full season with league_id + season
            5. **Match Day**: Get specific round fixtures with league_id + round
            6. **Result Collection**: Fetch completed matches with status='FT'
        
        Performance Optimization:
            - Single fixture (fixture_id): 1 API call
            - League season: 1 API call (~380 fixtures for major league)
            - Date range: 1 API call per request (can include multiple leagues)
            - Team season: 1 API call (~50 fixtures per team)
            - Implement smart caching based on fixture status:
                * Upcoming (NS): Cache 1 hour
                * Live (1H/HT/2H): Cache 5 minutes
                * Finished (FT): Cache 7 days
        
        Rate Limit Considerations:
            - This is a high-frequency endpoint (daily/hourly updates)
            - Pro Plan: 7,500 requests/day, 150/minute
            - Recommended: Batch requests by date/league, not per team
            - Example efficient workflow:
                1. Fetch league fixtures once per day (1 call)
                2. Filter by team locally (0 additional calls)
                3. Update live matches every 5 minutes (N calls for N live matches)
        
        Data Quality Notes:
            - Historical matches have complete data (scores, events, statistics)
            - Future matches have minimal data (date, teams, venue)
            - Live matches have partial data (current score, elapsed time, events)
            - Some leagues have limited referee information
            - Event data quality varies by league coverage
            - Postponed/cancelled matches retain original schedule date
        
        Error Handling:
            - Returns empty list if no fixtures match filters
            - Invalid date format raises ValidationError
            - Invalid timezone raises APIError
            - API request failure raises APIError
            - Invalid status code raises ValidationError
        
        API Limits & Quotas:
            - Maximum date range: typically 1 year
            - Historical data: varies by league (typically 3-10 years)
            - Future fixtures: typically 1-2 months ahead
            - Some leagues have delayed fixture announcements
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Fixtures/operation/get-fixtures
        """
        # Log request with all provided filters
        filter_parts = []
        if fixture_id is not None:
            filter_parts.append(f"id={fixture_id}")
        if league_id is not None:
            filter_parts.append(f"league={league_id}")
        if season is not None:
            filter_parts.append(f"season={season}")
        if date:
            filter_parts.append(f"date={date}")
        if date_from and date_to:
            filter_parts.append(f"date_range={date_from} to {date_to}")
        if team_id is not None:
            filter_parts.append(f"team={team_id}")
        if status:
            filter_parts.append(f"status={status}")
        if timezone:
            filter_parts.append(f"timezone={timezone}")
        if venue_id is not None:
            filter_parts.append(f"venue={venue_id}")
        if round:
            filter_parts.append(f"round={round}")
        if last is not None:
            filter_parts.append(f"last={last}")
        
        filters_str = ", ".join(filter_parts) if filter_parts else "all fixtures"
        logger.info(f"Fetching fixtures ({filters_str})")
        
        # Build query parameters
        params = {}
        if fixture_id is not None:
            params['id'] = fixture_id
        if league_id is not None:
            params['league'] = league_id
        if season is not None:
            params['season'] = season
        if date:
            params['date'] = date
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        if team_id is not None:
            params['team'] = team_id
        if status:
            params['status'] = status
        if timezone:
            params['timezone'] = timezone
        if venue_id is not None:
            params['venue'] = venue_id
        if round:
            params['round'] = round
        if last is not None:
            params['last'] = last
        
        # Make API request
        response = self.get('fixtures', params=params if params else None)
        fixtures = response.get('response', [])
        
        # Validate response
        if fixtures is None:
            logger.warning("API returned None for fixtures response")
            fixtures = []
        
        # Log results with context
        if fixture_id:
            if fixtures:
                fixture_info = fixtures[0].get('fixture', {})
                teams = fixtures[0].get('teams', {})
                home = teams.get('home', {}).get('name', 'Unknown')
                away = teams.get('away', {}).get('name', 'Unknown')
                status_short = fixture_info.get('status', {}).get('short', 'Unknown')
                logger.info(
                    f"Fetched fixture: {home} vs {away} "
                    f"(ID: {fixture_id}, Status: {status_short})"
                )
            else:
                logger.warning(f"Fixture with ID {fixture_id} not found")
        else:
            logger.info(f"Fetched {len(fixtures)} fixtures")
            
            # Log status distribution for larger result sets
            if fixtures and len(fixtures) >= 10:
                status_counts = {}
                for fixture in fixtures:
                    status_short = fixture.get('fixture', {}).get('status', {}).get('short', 'Unknown')
                    status_counts[status_short] = status_counts.get(status_short, 0) + 1
                
                status_summary = ", ".join(
                    f"{status}: {count}" for status, count in sorted(status_counts.items())
                )
                logger.debug(f"Fixture status distribution: {status_summary}")
            
            # Log sample fixtures for small result sets
            if fixtures and len(fixtures) < 10:
                sample_info = []
                for fixture in fixtures[:5]:  # Show up to 5 fixtures
                    teams = fixture.get('teams', {})
                    home = teams.get('home', {}).get('name', 'Unknown')
                    away = teams.get('away', {}).get('name', 'Unknown')
                    sample_info.append(f"{home} vs {away}")
                logger.debug(f"Sample fixtures: {'; '.join(sample_info)}")
        
        return fixtures
    
    def get_standings(
        self,
        league_id: int,
        season: int,
        team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get league standings (league tables) from API-Football.
        
        Standings are essential for match prediction and team analysis. This endpoint
        provides complete league table data including:
        - Team rankings and positions
        - Points, wins, draws, losses
        - Goals for/against and goal difference
        - Recent form (last 5 matches)
        - Home/away performance breakdown
        - Promotion/relegation status
        
        🎯 CRITICAL: Essential data for prediction algorithms
        🔄 UPDATE FREQUENCY:
            - During season: Weekly (after match rounds complete)
            - Off-season: Monthly (or when needed)
        
        📊 TYPICAL DATA: ~20 teams per major league
        
        ⚠️ CACHING STRATEGY (IMPORTANT):
            - Active season: 6 hours (updated after matches)
            - Off-season: 30 days (relatively stable)
            - After major match rounds: Refresh immediately
        
        Args:
            league_id: League ID (required)
                Examples:
                - 39: Premier League (England)
                - 140: La Liga (Spain)
                - 78: Bundesliga (Germany)
                - 135: Serie A (Italy)
                - 61: Ligue 1 (France)
                
            season: Season year (required)
                Format: YYYY representing the starting year of the season
                Examples:
                - 2024: Represents 2024/25 season
                - 2023: Represents 2023/24 season
                Note: Some leagues use calendar year (e.g., MLS uses 2024 for 2024 season)
                
            team_id: Optional specific team filter
                When provided, returns only the standing for this team
                Useful for quick lookups of a single team's position
                Example: 42 for Arsenal's position in their league
        
        Returns:
            List containing league standing data with structure:
            [
                {
                    'league': {
                        'id': 39,
                        'name': 'Premier League',
                        'country': 'England',
                        'logo': 'https://...',
                        'flag': 'https://...',
                        'season': 2024,
                        'standings': [
                            [  # Primary standings group
                                {
                                    'rank': 1,                          # Current position
                                    'team': {
                                        'id': 42,
                                        'name': 'Arsenal',
                                        'logo': 'https://...'
                                    },
                                    'points': 45,                       # Total points
                                    'goalsDiff': 25,                    # Goal difference
                                    'group': 'Premier League',          # Group/division name
                                    'form': 'WWDWW',                   # Last 5 matches (W/D/L)
                                    'status': 'same',                   # Position trend (up/down/same)
                                    'description': 'Promotion - Champions League (Group Stage)',
                                    'all': {                            # Overall stats
                                        'played': 20,
                                        'win': 14,
                                        'draw': 3,
                                        'lose': 3,
                                        'goals': {
                                            'for': 48,
                                            'against': 23
                                        }
                                    },
                                    'home': {                           # Home stats
                                        'played': 10,
                                        'win': 8,
                                        'draw': 1,
                                        'lose': 1,
                                        'goals': {
                                            'for': 26,
                                            'against': 10
                                        }
                                    },
                                    'away': {                           # Away stats
                                        'played': 10,
                                        'win': 6,
                                        'draw': 2,
                                        'lose': 2,
                                        'goals': {
                                            'for': 22,
                                            'against': 13
                                        }
                                    },
                                    'update': '2024-01-14T00:00:00+00:00'
                                },
                                ...  # Positions 2-20
                            ],
                            # Some leagues have multiple groups/divisions
                            # For example, Copa Libertadores has Group A, B, C, etc.
                            # Most major leagues have a single group
                        ]
                    }
                }
            ]
        
        Examples:
            >>> # 1. Get full Premier League standings
            >>> standings = client.get_standings(league_id=39, season=2024)
            >>> league_data = standings[0]
            >>> table = league_data['league']['standings'][0]  # Main table
            >>> 
            >>> # Display top 5 teams
            >>> for team_data in table[:5]:
            ...     print(f"{team_data['rank']}. {team_data['team']['name']}: "
            ...           f"{team_data['points']} pts "
            ...           f"(Form: {team_data['form']})")
            >>> # Output:
            >>> # 1. Arsenal: 45 pts (Form: WWDWW)
            >>> # 2. Liverpool: 44 pts (Form: WDWWW)
            >>> # 3. Manchester City: 43 pts (Form: WWLWW)
            
            >>> # 2. Get specific team's standing
            >>> arsenal_standing = client.get_standings(
            ...     league_id=39,
            ...     season=2024,
            ...     team_id=42
            ... )
            >>> arsenal = arsenal_standing[0]['league']['standings'][0][0]
            >>> print(f"Arsenal position: {arsenal['rank']}")
            >>> print(f"Points: {arsenal['points']}")
            >>> print(f"Goal difference: {arsenal['goalsDiff']}")
            
            >>> # 3. Analyze team form (recent performance)
            >>> for team_data in table:
            ...     if team_data['form']:
            ...         wins = team_data['form'].count('W')
            ...         if wins >= 4:  # 4+ wins in last 5
            ...             print(f"{team_data['team']['name']}: Hot streak! "
            ...                   f"({team_data['form']})")
            
            >>> # 4. Find teams in relegation zone
            >>> relegation_teams = [
            ...     t for t in table
            ...     if 'Relegation' in t.get('description', '')
            ... ]
            >>> for team_data in relegation_teams:
            ...     print(f"{team_data['rank']}. {team_data['team']['name']}: "
            ...           f"{team_data['points']} pts")
            
            >>> # 5. Home vs Away performance analysis
            >>> for team_data in table:
            ...     home_ppg = (team_data['home']['win'] * 3 + 
            ...                 team_data['home']['draw']) / team_data['home']['played']
            ...     away_ppg = (team_data['away']['win'] * 3 + 
            ...                 team_data['away']['draw']) / team_data['away']['played']
            ...     
            ...     if home_ppg > away_ppg + 0.5:  # Significantly better at home
            ...         print(f"{team_data['team']['name']}: Strong home form "
            ...               f"(Home: {home_ppg:.2f} ppg, Away: {away_ppg:.2f} ppg)")
            
            >>> # 6. Goal scoring analysis
            >>> top_scorers = sorted(
            ...     table,
            ...     key=lambda t: t['all']['goals']['for'],
            ...     reverse=True
            ... )[:3]
            >>> for team_data in top_scorers:
            ...     goals = team_data['all']['goals']
            ...     print(f"{team_data['team']['name']}: "
            ...           f"{goals['for']} goals scored, "
            ...           f"{goals['against']} conceded")
            
            >>> # 7. Points per game calculation
            >>> for team_data in table:
            ...     played = team_data['all']['played']
            ...     points = team_data['points']
            ...     ppg = points / played if played > 0 else 0
            ...     print(f"{team_data['team']['name']}: "
            ...           f"{ppg:.2f} points per game")
            
            >>> # 8. Championship race (top 4)
            >>> champions_league_spots = table[:4]
            >>> print("Champions League qualification race:")
            >>> for team_data in champions_league_spots:
            ...     print(f"{team_data['rank']}. {team_data['team']['name']}: "
            ...           f"{team_data['points']} pts (Recent: {team_data['form']})")
            
            >>> # 9. Multiple leagues comparison
            >>> leagues_to_check = [
            ...     (39, 'Premier League'),
            ...     (140, 'La Liga'),
            ...     (78, 'Bundesliga')
            ... ]
            >>> for league_id, league_name in leagues_to_check:
            ...     standings = client.get_standings(league_id=league_id, season=2024)
            ...     leader = standings[0]['league']['standings'][0][0]
            ...     print(f"{league_name} leader: {leader['team']['name']} "
            ...           f"({leader['points']} pts)")
            
            >>> # 10. Defensive analysis
            >>> best_defense = sorted(
            ...     table,
            ...     key=lambda t: t['all']['goals']['against']
            ... )[:5]
            >>> print("Best defensive records:")
            >>> for team_data in best_defense:
            ...     print(f"{team_data['team']['name']}: "
            ...           f"{team_data['all']['goals']['against']} goals conceded "
            ...           f"in {team_data['all']['played']} games")
        
        Common Use Cases:
            1. **Weekly Updates**: Fetch standings after match rounds complete
            2. **Team Position**: Quick lookup with team_id filter
            3. **Form Analysis**: Use 'form' field for recent performance
            4. **Prediction Features**: Use points, goal diff, form as ML features
            5. **Relegation Risk**: Identify teams near relegation zone
            6. **Title Race**: Track top teams and points gaps
        
        Data Analysis Applications:
            - **Match Prediction**: Table position affects outcome probability
            - **Over/Under Goals**: Goals scored/conceded rates
            - **Home Advantage**: Compare home vs away performance
            - **Form Momentum**: Recent results (form field)
            - **Strength of Schedule**: Analyze opponents based on standings
        
        Performance Optimization:
            - Full league table: 1 API call
            - Single team standing: 1 API call (same cost)
            - Recommended: Fetch full table, filter locally
            - Cache for 6 hours during active season
            - Update after major match rounds complete
        
        Data Structure Notes:
            - Most leagues return single standings group (main table)
            - Some competitions have multiple groups (e.g., Champions League)
            - Access main table: standings[0]['league']['standings'][0]
            - 'form' shows last 5 matches: W=Win, D=Draw, L=Loss
            - 'status' indicates position change: up/down/same
            - 'description' shows qualification/relegation status
            - Stats broken down by: all/home/away matches
        
        Standings Positions Explained:
            - Premier League (20 teams):
                * 1-4: Champions League qualification
                * 5-6: Europa League
                * 7: Conference League (or FA Cup winner)
                * 18-20: Relegation to Championship
            - Varies by league and season rules
        
        Historical Data:
            - Available for past seasons (typically 10+ years)
            - Use to analyze team progression over time
            - Compare current season to historical performance
        
        Error Handling:
            - Returns empty list if league/season not found
            - Invalid league_id raises APIError
            - Invalid season raises ValidationError
            - Some leagues may not have standings yet (early season)
        
        Rate Limit Considerations:
            - This endpoint is called less frequently than fixtures
            - Pro Plan: 7,500 requests/day, 150/minute
            - Recommended: Weekly updates during season
            - Cache for 6 hours to minimize API calls
        
        Documentation:
            https://www.api-football.com/documentation-v3#tag/Standings/operation/get-standings
        """
        # Log request parameters
        filter_parts = [f"league={league_id}", f"season={season}"]
        if team_id is not None:
            filter_parts.append(f"team={team_id}")
        
        filters_str = ", ".join(filter_parts)
        logger.info(f"Fetching standings ({filters_str})")
        
        # Build query parameters
        params = {
            'league': league_id,
            'season': season
        }
        if team_id is not None:
            params['team'] = team_id
        
        # Make API request
        response = self.get('standings', params=params)
        standings = response.get('response', [])
        
        # Validate response
        if standings is None:
            logger.warning("API returned None for standings response")
            standings = []
        
        # Log results with context
        if standings:
            league_info = standings[0].get('league', {})
            league_name = league_info.get('name', 'Unknown')
            season_year = league_info.get('season', season)
            
            # Get standings table(s)
            standings_groups = league_info.get('standings', [])
            
            if team_id:
                # Specific team requested
                if standings_groups and standings_groups[0]:
                    team_data = standings_groups[0][0]  # First (only) result
                    team_name = team_data.get('team', {}).get('name', 'Unknown')
                    rank = team_data.get('rank', 'N/A')
                    points = team_data.get('points', 0)
                    form = team_data.get('form', 'N/A')
                    
                    logger.info(
                        f"Fetched standing for {team_name} in {league_name} {season_year}: "
                        f"Position {rank}, {points} points (Form: {form})"
                    )
                else:
                    logger.warning(f"Team {team_id} not found in standings")
            else:
                # Full league table
                total_teams = sum(len(group) for group in standings_groups)
                num_groups = len(standings_groups)
                
                if num_groups == 1:
                    # Single table (most common)
                    logger.info(
                        f"Fetched {league_name} {season_year} standings: "
                        f"{total_teams} teams"
                    )
                    
                    # Log top 3 and bottom 3 for context
                    if standings_groups[0]:
                        top_3 = standings_groups[0][:3]
                        bottom_3 = standings_groups[0][-3:]
                        
                        top_info = ", ".join(
                            f"{t['rank']}. {t['team']['name']} ({t['points']} pts)"
                            for t in top_3
                        )
                        bottom_info = ", ".join(
                            f"{t['rank']}. {t['team']['name']} ({t['points']} pts)"
                            for t in bottom_3
                        )
                        
                        logger.debug(f"Top 3: {top_info}")
                        logger.debug(f"Bottom 3: {bottom_info}")
                else:
                    # Multiple groups (e.g., Champions League)
                    logger.info(
                        f"Fetched {league_name} {season_year} standings: "
                        f"{num_groups} groups, {total_teams} teams total"
                    )
                    
                    # Log group names
                    group_names = [
                        standings_groups[i][0]['group'] if standings_groups[i] else 'Unknown'
                        for i in range(num_groups)
                    ]
                    logger.debug(f"Groups: {', '.join(group_names)}")
        else:
            logger.warning(
                f"No standings found for league {league_id}, season {season}"
            )
        
        return standings
