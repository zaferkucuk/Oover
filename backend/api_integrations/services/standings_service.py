"""
Standings Service Module

This module provides business logic layer for managing league standings data.
It orchestrates the process of fetching standings from API-Football, transforming
the data, resolving team UUIDs, and saving to Supabase database.

Key Features:
    - Fetch standings from API-Football
    - Transform API data to database format
    - Team UUID resolution from database
    - Bulk insert/update operations
    - Standings retrieval by league/season/team
    - Error handling and logging

Classes:
    StandingsService: Main service class for standings operations

Dependencies:
    - APIFootballClient: For fetching data from API-Football
    - StandingTransformer: For transforming API data
    - Supabase: For database operations
    - logging: For operation logging

Usage Example:
    ```python
    service = StandingsService()
    
    # Fetch and save standings for a league
    standings = await service.fetch_and_save_standings(
        league_id="39",  # Premier League
        season=2024
    )
    
    # Get standings from database
    db_standings = await service.get_standings_by_league(
        league_id="your-league-uuid",
        season=2024
    )
    
    # Get specific team's position
    position = await service.get_team_position(
        league_id="your-league-uuid",
        team_id="your-team-uuid",
        season=2024
    )
    ```

Author: Zafer Kucuk
Created: 2025-11-01
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

from ..providers.api_football.client import APIFootballClient
from ..transformers.standing_transformer import StandingTransformer
from ...utils.supabase_client import get_supabase_client

# Configure logging
logger = logging.getLogger(__name__)


class StandingsService:
    """
    Business logic service for managing league standings data.
    
    This service handles the complete lifecycle of standings data:
    1. Fetching from API-Football
    2. Transforming to database format
    3. Resolving team UUIDs
    4. Saving to database
    5. Retrieving from database
    6. Updating existing standings
    
    Attributes:
        client (APIFootballClient): API-Football client for data fetching
        transformer (StandingTransformer): Transformer for data conversion
        supabase: Supabase client for database operations
        
    Methods:
        fetch_and_save_standings: Fetch from API and save to database
        get_standings_by_league: Get standings for a league/season
        get_team_position: Get specific team's standing
        update_standings: Update existing standings data
        bulk_upsert_standings: Bulk insert/update operations
        _resolve_team_uuids: Resolve team UUIDs from API IDs
        _get_league_uuid: Get league UUID from API ID
    """
    
    def __init__(self):
        """
        Initialize the StandingsService.
        
        Sets up API client, transformer, and database connection.
        """
        self.client = APIFootballClient()
        self.transformer = StandingTransformer()
        self.supabase = get_supabase_client()
        logger.info("StandingsService initialized")
    
    async def fetch_and_save_standings(
        self,
        league_id: str,
        season: int,
        team_id: Optional[str] = None
    ) -> Dict:
        """
        Fetch standings from API-Football and save to database.
        
        This is the main method for populating standings data. It:
        1. Fetches standings from API-Football
        2. Transforms the data to database format
        3. Resolves team UUIDs from database
        4. Saves to database using bulk upsert
        5. Returns summary of operation
        
        Args:
            league_id: API-Football league ID (e.g., "39" for Premier League)
            season: Season year (e.g., 2024)
            team_id: Optional API-Football team ID to fetch specific team
            
        Returns:
            Dictionary with operation summary:
                {
                    'success': bool,
                    'league_id': str,
                    'season': int,
                    'standings_count': int,
                    'inserted': int,
                    'updated': int,
                    'errors': List[str],
                    'api_response': Dict
                }
                
        Raises:
            ValueError: If league_id or season is invalid
            Exception: If API fetch or database operation fails
            
        Example:
            >>> service = StandingsService()
            >>> result = await service.fetch_and_save_standings(
            ...     league_id="39",
            ...     season=2024
            ... )
            >>> print(f"Saved {result['standings_count']} standings")
        """
        logger.info(f"Fetching standings for league {league_id}, season {season}")
        
        try:
            # Validate inputs
            if not league_id or not str(league_id).isdigit():
                raise ValueError(f"Invalid league_id: {league_id}")
            if not season or season < 2000 or season > 2100:
                raise ValueError(f"Invalid season: {season}")
            
            # Fetch from API-Football
            api_response = self.client.get_standings(
                league_id=league_id,
                season=season,
                team_id=team_id
            )
            
            if not api_response.get('success'):
                error_msg = api_response.get('error', 'Unknown API error')
                logger.error(f"API fetch failed: {error_msg}")
                return {
                    'success': False,
                    'league_id': league_id,
                    'season': season,
                    'standings_count': 0,
                    'inserted': 0,
                    'updated': 0,
                    'errors': [error_msg],
                    'api_response': api_response
                }
            
            # Extract standings data
            api_standings = api_response.get('data', [])
            if not api_standings:
                logger.warning(f"No standings data found for league {league_id}, season {season}")
                return {
                    'success': True,
                    'league_id': league_id,
                    'season': season,
                    'standings_count': 0,
                    'inserted': 0,
                    'updated': 0,
                    'errors': [],
                    'api_response': api_response
                }
            
            # API-Football returns standings in nested structure
            # response -> data -> [0] -> league -> standings -> [[team1, team2, ...]]
            first_league = api_standings[0] if api_standings else {}
            league_standings = first_league.get('league', {}).get('standings', [[]])
            flat_standings = league_standings[0] if league_standings else []
            
            if not flat_standings:
                logger.warning(f"No standings found in nested structure")
                return {
                    'success': True,
                    'league_id': league_id,
                    'season': season,
                    'standings_count': 0,
                    'inserted': 0,
                    'updated': 0,
                    'errors': [],
                    'api_response': api_response
                }
            
            logger.info(f"Found {len(flat_standings)} standings in API response")
            
            # Resolve league UUID from database
            league_uuid = await self._get_league_uuid(league_id)
            if not league_uuid:
                error_msg = f"League UUID not found for API ID {league_id}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'league_id': league_id,
                    'season': season,
                    'standings_count': 0,
                    'inserted': 0,
                    'updated': 0,
                    'errors': [error_msg],
                    'api_response': api_response
                }
            
            # Resolve team UUIDs
            team_id_map = await self._resolve_team_uuids(flat_standings)
            
            # Transform standings data
            transformed_standings = self.transformer.bulk_transform_standings(
                flat_standings,
                team_id_map=team_id_map,
                league_id=league_uuid,
                season=season
            )
            
            if not transformed_standings['standings']:
                logger.warning(f"No valid standings after transformation")
                return {
                    'success': False,
                    'league_id': league_id,
                    'season': season,
                    'standings_count': 0,
                    'inserted': 0,
                    'updated': 0,
                    'errors': transformed_standings['errors'],
                    'api_response': api_response
                }
            
            # Bulk upsert to database
            upsert_result = await self.bulk_upsert_standings(
                transformed_standings['standings']
            )
            
            logger.info(
                f"Successfully saved standings: "
                f"{upsert_result['inserted']} inserted, "
                f"{upsert_result['updated']} updated"
            )
            
            return {
                'success': True,
                'league_id': league_id,
                'season': season,
                'standings_count': len(transformed_standings['standings']),
                'inserted': upsert_result['inserted'],
                'updated': upsert_result['updated'],
                'errors': transformed_standings['errors'],
                'api_response': api_response
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_save_standings: {str(e)}", exc_info=True)
            return {
                'success': False,
                'league_id': league_id,
                'season': season,
                'standings_count': 0,
                'inserted': 0,
                'updated': 0,
                'errors': [str(e)],
                'api_response': None
            }
    
    async def get_standings_by_league(
        self,
        league_id: str,
        season: int,
        order_by: str = 'position'
    ) -> List[Dict]:
        """
        Get standings from database for a specific league and season.
        
        Args:
            league_id: League UUID from database
            season: Season year (e.g., 2024)
            order_by: Column to order by (default: 'position')
                     Options: 'position', 'points', 'goal_difference'
                     
        Returns:
            List of standing dictionaries ordered by specified column
            
        Example:
            >>> standings = await service.get_standings_by_league(
            ...     league_id="uuid-here",
            ...     season=2024
            ... )
            >>> for standing in standings:
            ...     print(f"{standing['position']}. {standing['team_id']}")
        """
        try:
            logger.info(f"Fetching standings for league {league_id}, season {season}")
            
            response = self.supabase.table('standings') \
                .select('*') \
                .eq('league_id', league_id) \
                .eq('season', season) \
                .order(order_by) \
                .execute()
            
            standings = response.data if response.data else []
            logger.info(f"Found {len(standings)} standings")
            
            return standings
            
        except Exception as e:
            logger.error(f"Error fetching standings: {str(e)}", exc_info=True)
            return []
    
    async def get_team_position(
        self,
        league_id: str,
        team_id: str,
        season: int
    ) -> Optional[Dict]:
        """
        Get specific team's standing in a league for a season.
        
        Args:
            league_id: League UUID from database
            team_id: Team UUID from database
            season: Season year (e.g., 2024)
            
        Returns:
            Standing dictionary if found, None otherwise
            
        Example:
            >>> standing = await service.get_team_position(
            ...     league_id="league-uuid",
            ...     team_id="team-uuid",
            ...     season=2024
            ... )
            >>> if standing:
            ...     print(f"Position: {standing['position']}")
        """
        try:
            logger.info(f"Fetching position for team {team_id} in league {league_id}")
            
            response = self.supabase.table('standings') \
                .select('*') \
                .eq('league_id', league_id) \
                .eq('team_id', team_id) \
                .eq('season', season) \
                .execute()
            
            if response.data and len(response.data) > 0:
                standing = response.data[0]
                logger.info(f"Team position: {standing['position']}")
                return standing
            else:
                logger.warning(f"No standing found for team {team_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching team position: {str(e)}", exc_info=True)
            return None
    
    async def update_standings(
        self,
        league_id: str,
        season: int
    ) -> Dict:
        """
        Update existing standings data for a league/season.
        
        This method fetches latest standings from API and updates the database.
        It's useful for refreshing standings after matches are played.
        
        Args:
            league_id: API-Football league ID
            season: Season year (e.g., 2024)
            
        Returns:
            Dictionary with update summary:
                {
                    'success': bool,
                    'league_id': str,
                    'season': int,
                    'updated': int,
                    'errors': List[str]
                }
                
        Example:
            >>> result = await service.update_standings(
            ...     league_id="39",
            ...     season=2024
            ... )
            >>> print(f"Updated {result['updated']} standings")
        """
        logger.info(f"Updating standings for league {league_id}, season {season}")
        
        # Fetch and save will handle update via upsert
        result = await self.fetch_and_save_standings(
            league_id=league_id,
            season=season
        )
        
        return {
            'success': result['success'],
            'league_id': league_id,
            'season': season,
            'updated': result['updated'],
            'errors': result['errors']
        }
    
    async def bulk_upsert_standings(
        self,
        standings: List[Dict]
    ) -> Dict:
        """
        Bulk insert or update standings in database.
        
        Uses upsert operation to insert new standings or update existing ones.
        The unique constraint is on (league_id, team_id, season).
        
        Args:
            standings: List of standing dictionaries in database format
            
        Returns:
            Dictionary with operation summary:
                {
                    'success': bool,
                    'inserted': int,
                    'updated': int,
                    'total': int,
                    'errors': List[str]
                }
                
        Example:
            >>> standings = [
            ...     {'league_id': 'uuid', 'team_id': 'uuid', 'season': 2024, ...},
            ...     {'league_id': 'uuid', 'team_id': 'uuid', 'season': 2024, ...}
            ... ]
            >>> result = await service.bulk_upsert_standings(standings)
        """
        if not standings:
            logger.warning("No standings to upsert")
            return {
                'success': True,
                'inserted': 0,
                'updated': 0,
                'total': 0,
                'errors': []
            }
        
        try:
            logger.info(f"Upserting {len(standings)} standings")
            
            # Add timestamps
            now = datetime.utcnow().isoformat()
            for standing in standings:
                if 'created_at' not in standing:
                    standing['created_at'] = now
                standing['updated_at'] = now
            
            # Upsert to database
            # Note: Supabase upsert uses conflict resolution on unique constraints
            # The standings table has unique constraint on (league_id, team_id, season)
            response = self.supabase.table('standings') \
                .upsert(standings, on_conflict='league_id,team_id,season') \
                .execute()
            
            if response.data:
                total = len(response.data)
                logger.info(f"Successfully upserted {total} standings")
                
                # Note: Supabase doesn't distinguish between insert and update in response
                # We'll assume all are updates if they existed, all are inserts if new
                # For better tracking, we could query first to check existing records
                
                return {
                    'success': True,
                    'inserted': total,  # This is approximation
                    'updated': 0,       # This is approximation
                    'total': total,
                    'errors': []
                }
            else:
                logger.error("Upsert returned no data")
                return {
                    'success': False,
                    'inserted': 0,
                    'updated': 0,
                    'total': 0,
                    'errors': ['Upsert returned no data']
                }
                
        except Exception as e:
            logger.error(f"Error in bulk_upsert_standings: {str(e)}", exc_info=True)
            return {
                'success': False,
                'inserted': 0,
                'updated': 0,
                'total': 0,
                'errors': [str(e)]
            }
    
    async def _resolve_team_uuids(
        self,
        api_standings: List[Dict]
    ) -> Dict[str, str]:
        """
        Resolve team UUIDs from API team IDs.
        
        Creates a mapping from API-Football team IDs to database team UUIDs.
        This is necessary because the database uses UUIDs while API uses integer IDs.
        
        Args:
            api_standings: List of standings from API-Football
            
        Returns:
            Dictionary mapping API team ID (str) to team UUID (str)
            Example: {'33': 'uuid-for-manchester-united', '34': 'uuid-for-newcastle'}
            
        Note:
            Teams not found in database will be logged as warnings.
            The transformer will skip standings for teams without UUIDs.
        """
        try:
            # Extract unique team IDs from API standings
            team_ids = set()
            for standing in api_standings:
                team_data = standing.get('team', {})
                team_id = team_data.get('id')
                if team_id:
                    team_ids.add(str(team_id))
            
            if not team_ids:
                logger.warning("No team IDs found in API standings")
                return {}
            
            logger.info(f"Resolving UUIDs for {len(team_ids)} teams")
            
            # Query database for team UUIDs
            # Teams table has api_football_id column for mapping
            response = self.supabase.table('teams') \
                .select('id, api_football_id') \
                .in_('api_football_id', list(team_ids)) \
                .execute()
            
            if not response.data:
                logger.warning("No teams found in database for given API IDs")
                return {}
            
            # Build mapping
            team_id_map = {}
            for team in response.data:
                api_id = str(team['api_football_id'])
                uuid = team['id']
                team_id_map[api_id] = uuid
            
            # Log any missing teams
            found_ids = set(team_id_map.keys())
            missing_ids = team_ids - found_ids
            if missing_ids:
                logger.warning(f"Teams not found in database: {missing_ids}")
            
            logger.info(f"Resolved {len(team_id_map)} team UUIDs")
            return team_id_map
            
        except Exception as e:
            logger.error(f"Error resolving team UUIDs: {str(e)}", exc_info=True)
            return {}
    
    async def _get_league_uuid(
        self,
        api_league_id: str
    ) -> Optional[str]:
        """
        Get league UUID from database using API-Football league ID.
        
        Args:
            api_league_id: API-Football league ID (e.g., "39" for Premier League)
            
        Returns:
            League UUID if found, None otherwise
            
        Note:
            Leagues table has api_football_id column for mapping.
        """
        try:
            logger.info(f"Resolving league UUID for API ID {api_league_id}")
            
            response = self.supabase.table('leagues') \
                .select('id') \
                .eq('api_football_id', api_league_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                league_uuid = response.data[0]['id']
                logger.info(f"League UUID: {league_uuid}")
                return league_uuid
            else:
                logger.warning(f"League not found for API ID {api_league_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving league UUID: {str(e)}", exc_info=True)
            return None
    
    async def get_standings_summary(
        self,
        league_id: str,
        season: int
    ) -> Dict:
        """
        Get a summary of standings for a league/season.
        
        Provides aggregated information about the standings table:
        - Total teams
        - Leader (1st place)
        - Last place
        - Promotion zone teams
        - Relegation zone teams
        
        Args:
            league_id: League UUID from database
            season: Season year (e.g., 2024)
            
        Returns:
            Dictionary with summary information
            
        Example:
            >>> summary = await service.get_standings_summary(
            ...     league_id="league-uuid",
            ...     season=2024
            ... )
            >>> print(f"Leader: {summary['leader']['position']}")
        """
        try:
            standings = await self.get_standings_by_league(
                league_id=league_id,
                season=season,
                order_by='position'
            )
            
            if not standings:
                return {
                    'total_teams': 0,
                    'leader': None,
                    'last_place': None,
                    'promotion_zone': [],
                    'relegation_zone': []
                }
            
            # Find promotion and relegation zone teams
            promotion_zone = [s for s in standings if 'promotion' in s.get('description', '').lower()]
            relegation_zone = [s for s in standings if 'relegation' in s.get('description', '').lower()]
            
            return {
                'total_teams': len(standings),
                'leader': standings[0] if standings else None,
                'last_place': standings[-1] if standings else None,
                'promotion_zone': promotion_zone,
                'relegation_zone': relegation_zone
            }
            
        except Exception as e:
            logger.error(f"Error getting standings summary: {str(e)}", exc_info=True)
            return {
                'total_teams': 0,
                'leader': None,
                'last_place': None,
                'promotion_zone': [],
                'relegation_zone': [],
                'error': str(e)
            }
