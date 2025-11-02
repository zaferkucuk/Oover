"""
Statistics Service Module

This module provides business logic layer for managing match statistics data.
It orchestrates the process of fetching statistics from API-Football, transforming
the data, resolving match/team UUIDs, and saving to Supabase database.

Key Features:
    - Fetch match statistics from API-Football
    - Transform API data to database format
    - Match and Team UUID resolution from database
    - Bulk insert/update operations
    - Statistics retrieval by match/team
    - Recent performance analysis
    - Error handling and logging

Classes:
    StatisticsService: Main service class for statistics operations

Dependencies:
    - APIFootballClient: For fetching data from API-Football
    - StatisticsTransformer: For transforming API data
    - Supabase: For database operations
    - logging: For operation logging

Usage Example:
    ```python
    service = StatisticsService()
    
    # Fetch and save statistics for a match
    stats = await service.fetch_and_save_statistics(
        match_id="868023"  # API-Football match ID
    )
    
    # Get statistics from database for a match
    db_stats = await service.get_statistics_by_match(
        match_id="your-match-uuid"
    )
    
    # Get recent statistics for a team
    recent = await service.get_recent_statistics(
        team_id="your-team-uuid",
        limit=5
    )
    ```

Author: Zafer Kucuk
Created: 2025-11-02
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

from ..providers.api_football.client import APIFootballClient
from ..transformers.statistics_transformer import StatisticsTransformer
from ...utils.supabase_client import get_supabase_client

# Configure logging
logger = logging.getLogger(__name__)


class StatisticsService:
    """
    Business logic service for managing match statistics data.
    
    This service handles the complete lifecycle of statistics data:
    1. Fetching from API-Football
    2. Transforming to database format
    3. Resolving match and team UUIDs
    4. Saving to database (team_statistics table)
    5. Retrieving from database
    6. Updating existing statistics
    7. Aggregating team performance
    
    Attributes:
        client (APIFootballClient): API-Football client for data fetching
        transformer (StatisticsTransformer): Transformer for data conversion
        supabase: Supabase client for database operations
        
    Methods:
        fetch_and_save_statistics: Fetch from API and save to database
        get_statistics_by_match: Get statistics for a match
        get_statistics_by_team: Get statistics for a team
        get_recent_statistics: Get recent team performance
        update_statistics: Update existing statistics
        bulk_upsert_statistics: Bulk insert/update operations
        get_statistics_summary: Aggregated statistics overview
        _resolve_match_uuid: Resolve match UUID from API ID
        _resolve_team_uuid: Resolve team UUID from API ID
    """
    
    def __init__(self):
        """
        Initialize the StatisticsService.
        
        Sets up API client, transformer, and database connection.
        """
        self.client = APIFootballClient()
        self.transformer = StatisticsTransformer()
        self.supabase = get_supabase_client()
        logger.info("StatisticsService initialized")
    
    async def fetch_and_save_statistics(
        self,
        match_id: str,
        team_id: Optional[str] = None
    ) -> Dict:
        """
        Fetch match statistics from API-Football and save to database.
        
        This is the main method for populating statistics data. It:
        1. Fetches statistics from API-Football
        2. Transforms the data to database format
        3. Resolves match and team UUIDs from database
        4. Saves to database using bulk upsert
        5. Returns summary of operation
        
        Args:
            match_id: API-Football match/fixture ID (e.g., "868023")
            team_id: Optional API-Football team ID to fetch specific team stats
            
        Returns:
            Dictionary with operation summary:
                {
                    'success': bool,
                    'match_id': str,
                    'statistics_count': int,
                    'teams': List[str],  # Team names
                    'inserted': int,
                    'updated': int,
                    'errors': List[str],
                    'api_response': Dict
                }
                
        Raises:
            ValueError: If match_id is invalid
            Exception: If API fetch or database operation fails
            
        Example:
            >>> service = StatisticsService()
            >>> result = await service.fetch_and_save_statistics(
            ...     match_id="868023"
            ... )
            >>> print(f"Saved statistics for {len(result['teams'])} teams")
        """
        logger.info(f"Fetching statistics for match {match_id}")
        
        try:
            # Validate inputs
            if not match_id or not str(match_id).isdigit():
                raise ValueError(f"Invalid match_id: {match_id}")
            
            # Fetch from API-Football
            api_response = self.client.get_match_statistics(
                match_id=match_id,
                team_id=team_id
            )
            
            if not api_response.get('success'):
                error_msg = api_response.get('error', 'Unknown API error')
                logger.error(f"API fetch failed: {error_msg}")
                return {
                    'success': False,
                    'match_id': match_id,
                    'statistics_count': 0,
                    'teams': [],
                    'inserted': 0,
                    'updated': 0,
                    'errors': [error_msg],
                    'api_response': api_response
                }
            
            # Extract statistics data
            api_statistics = api_response.get('data', [])
            if not api_statistics:
                logger.warning(f"No statistics data found for match {match_id}")
                return {
                    'success': True,
                    'match_id': match_id,
                    'statistics_count': 0,
                    'teams': [],
                    'inserted': 0,
                    'updated': 0,
                    'errors': [],
                    'api_response': api_response
                }
            
            logger.info(f"Found statistics for {len(api_statistics)} teams")
            
            # Resolve match UUID from database
            match_uuid = await self._resolve_match_uuid(match_id)
            if not match_uuid:
                error_msg = f"Match UUID not found for API ID {match_id}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'match_id': match_id,
                    'statistics_count': 0,
                    'teams': [],
                    'inserted': 0,
                    'updated': 0,
                    'errors': [error_msg],
                    'api_response': api_response
                }
            
            # Transform statistics data for each team
            transformed_statistics = []
            team_names = []
            transform_errors = []
            
            for team_stats in api_statistics:
                # Extract team info
                team_data = team_stats.get('team', {})
                api_team_id = str(team_data.get('id', ''))
                team_name = team_data.get('name', 'Unknown')
                team_names.append(team_name)
                
                # Resolve team UUID
                team_uuid = await self._resolve_team_uuid(api_team_id)
                if not team_uuid:
                    error_msg = f"Team UUID not found for API ID {api_team_id}"
                    logger.warning(error_msg)
                    transform_errors.append(error_msg)
                    continue
                
                # Transform statistics
                try:
                    transformed = self.transformer.transform(
                        team_stats,
                        match_id=match_uuid,
                        team_id=team_uuid
                    )
                    if transformed:
                        transformed_statistics.append(transformed)
                except Exception as e:
                    error_msg = f"Error transforming stats for team {team_name}: {str(e)}"
                    logger.error(error_msg)
                    transform_errors.append(error_msg)
            
            if not transformed_statistics:
                logger.warning(f"No valid statistics after transformation")
                return {
                    'success': False,
                    'match_id': match_id,
                    'statistics_count': 0,
                    'teams': team_names,
                    'inserted': 0,
                    'updated': 0,
                    'errors': transform_errors,
                    'api_response': api_response
                }
            
            # Bulk upsert to database
            upsert_result = await self.bulk_upsert_statistics(
                transformed_statistics
            )
            
            logger.info(
                f"Successfully saved statistics for {len(team_names)} teams: "
                f"{upsert_result['inserted']} inserted, "
                f"{upsert_result['updated']} updated"
            )
            
            return {
                'success': True,
                'match_id': match_id,
                'statistics_count': len(transformed_statistics),
                'teams': team_names,
                'inserted': upsert_result['inserted'],
                'updated': upsert_result['updated'],
                'errors': transform_errors,
                'api_response': api_response
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_save_statistics: {str(e)}", exc_info=True)
            return {
                'success': False,
                'match_id': match_id,
                'statistics_count': 0,
                'teams': [],
                'inserted': 0,
                'updated': 0,
                'errors': [str(e)],
                'api_response': None
            }
    
    async def get_statistics_by_match(
        self,
        match_id: str,
        team_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get statistics from database for a specific match.
        
        Args:
            match_id: Match UUID from database
            team_id: Optional team UUID to filter specific team
            
        Returns:
            List of statistics dictionaries (1-2 teams per match)
            
        Example:
            >>> stats = await service.get_statistics_by_match(
            ...     match_id="match-uuid-here"
            ... )
            >>> for stat in stats:
            ...     print(f"Team: {stat['team_id']}")
            ...     print(f"Possession: {stat['statistics']['ball_possession']}%")
        """
        try:
            logger.info(f"Fetching statistics for match {match_id}")
            
            query = self.supabase.table('team_statistics') \
                .select('*') \
                .eq('match_id', match_id)
            
            if team_id:
                query = query.eq('team_id', team_id)
            
            response = query.execute()
            
            statistics = response.data if response.data else []
            logger.info(f"Found {len(statistics)} statistics records")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error fetching statistics by match: {str(e)}", exc_info=True)
            return []
    
    async def get_statistics_by_team(
        self,
        team_id: str,
        league_id: Optional[str] = None,
        season: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get statistics from database for a specific team.
        
        Optionally filter by league and season, and limit number of results.
        Results are ordered by match date (most recent first).
        
        Args:
            team_id: Team UUID from database
            league_id: Optional league UUID to filter
            season: Optional season year to filter
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of statistics dictionaries ordered by date (newest first)
            
        Example:
            >>> stats = await service.get_statistics_by_team(
            ...     team_id="team-uuid-here",
            ...     limit=5
            ... )
            >>> for stat in stats:
            ...     possession = stat['statistics'].get('ball_possession')
            ...     print(f"Possession: {possession}%")
        """
        try:
            logger.info(f"Fetching statistics for team {team_id}")
            
            # Build query - need to join with matches table for filtering
            query = self.supabase.table('team_statistics') \
                .select('*, matches!inner(league_id, season, match_date)') \
                .eq('team_id', team_id)
            
            if league_id:
                query = query.eq('matches.league_id', league_id)
            
            if season:
                query = query.eq('matches.season', season)
            
            response = query \
                .order('matches.match_date', desc=True) \
                .limit(limit) \
                .execute()
            
            statistics = response.data if response.data else []
            logger.info(f"Found {len(statistics)} statistics records")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error fetching statistics by team: {str(e)}", exc_info=True)
            return []
    
    async def get_recent_statistics(
        self,
        team_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent statistics for a team within specified days.
        
        Args:
            team_id: Team UUID from database
            days: Number of days to look back (default: 30)
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of statistics dictionaries from recent matches
            
        Example:
            >>> recent = await service.get_recent_statistics(
            ...     team_id="team-uuid-here",
            ...     days=14,
            ...     limit=5
            ... )
            >>> avg_possession = sum(
            ...     s['statistics'].get('ball_possession', 0) 
            ...     for s in recent
            ... ) / len(recent)
        """
        try:
            logger.info(f"Fetching recent statistics for team {team_id} (last {days} days)")
            
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table('team_statistics') \
                .select('*, matches!inner(match_date)') \
                .eq('team_id', team_id) \
                .gte('matches.match_date', cutoff_date) \
                .order('matches.match_date', desc=True) \
                .limit(limit) \
                .execute()
            
            statistics = response.data if response.data else []
            logger.info(f"Found {len(statistics)} recent statistics")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error fetching recent statistics: {str(e)}", exc_info=True)
            return []
    
    async def update_statistics(
        self,
        match_id: str,
        team_id: Optional[str] = None
    ) -> Dict:
        """
        Update existing statistics data for a match.
        
        This method fetches latest statistics from API and updates the database.
        Useful for refreshing statistics after match completion or corrections.
        
        Args:
            match_id: API-Football match ID
            team_id: Optional API-Football team ID
            
        Returns:
            Dictionary with update summary:
                {
                    'success': bool,
                    'match_id': str,
                    'updated': int,
                    'errors': List[str]
                }
                
        Example:
            >>> result = await service.update_statistics(
            ...     match_id="868023"
            ... )
            >>> print(f"Updated {result['updated']} statistics")
        """
        logger.info(f"Updating statistics for match {match_id}")
        
        # Fetch and save will handle update via upsert
        result = await self.fetch_and_save_statistics(
            match_id=match_id,
            team_id=team_id
        )
        
        return {
            'success': result['success'],
            'match_id': match_id,
            'updated': result['updated'],
            'errors': result['errors']
        }
    
    async def bulk_upsert_statistics(
        self,
        statistics: List[Dict]
    ) -> Dict:
        """
        Bulk insert or update statistics in database.
        
        Uses upsert operation to insert new statistics or update existing ones.
        The unique constraint is on (match_id, team_id).
        
        Args:
            statistics: List of statistics dictionaries in database format
            
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
            >>> statistics = [
            ...     {'match_id': 'uuid', 'team_id': 'uuid', 'statistics': {...}},
            ...     {'match_id': 'uuid', 'team_id': 'uuid', 'statistics': {...}}
            ... ]
            >>> result = await service.bulk_upsert_statistics(statistics)
        """
        if not statistics:
            logger.warning("No statistics to upsert")
            return {
                'success': True,
                'inserted': 0,
                'updated': 0,
                'total': 0,
                'errors': []
            }
        
        try:
            logger.info(f"Upserting {len(statistics)} statistics records")
            
            # Add timestamps
            now = datetime.utcnow().isoformat()
            for stat in statistics:
                if 'created_at' not in stat:
                    stat['created_at'] = now
                stat['updated_at'] = now
            
            # Upsert to database
            # The team_statistics table has unique constraint on (match_id, team_id)
            response = self.supabase.table('team_statistics') \
                .upsert(statistics, on_conflict='match_id,team_id') \
                .execute()
            
            if response.data:
                total = len(response.data)
                logger.info(f"Successfully upserted {total} statistics")
                
                return {
                    'success': True,
                    'inserted': total,  # Approximation
                    'updated': 0,       # Approximation
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
            logger.error(f"Error in bulk_upsert_statistics: {str(e)}", exc_info=True)
            return {
                'success': False,
                'inserted': 0,
                'updated': 0,
                'total': 0,
                'errors': [str(e)]
            }
    
    async def get_statistics_summary(
        self,
        team_id: str,
        league_id: Optional[str] = None,
        season: Optional[int] = None
    ) -> Dict:
        """
        Get aggregated statistics summary for a team.
        
        Provides averaged statistics across multiple matches:
        - Average possession
        - Average shots on goal
        - Average passes
        - Average fouls
        - Total matches analyzed
        
        Args:
            team_id: Team UUID from database
            league_id: Optional league UUID to filter
            season: Optional season year to filter
            
        Returns:
            Dictionary with aggregated statistics
            
        Example:
            >>> summary = await service.get_statistics_summary(
            ...     team_id="team-uuid",
            ...     season=2024
            ... )
            >>> print(f"Avg Possession: {summary['avg_possession']}%")
        """
        try:
            # Get team statistics
            stats = await self.get_statistics_by_team(
                team_id=team_id,
                league_id=league_id,
                season=season,
                limit=100  # Analyze up to 100 matches
            )
            
            if not stats:
                return {
                    'team_id': team_id,
                    'total_matches': 0,
                    'avg_possession': 0,
                    'avg_shots_on_goal': 0,
                    'avg_total_passes': 0,
                    'avg_fouls': 0,
                    'avg_expected_goals': 0
                }
            
            # Calculate averages
            total_matches = len(stats)
            
            # Helper to safely get numeric value from JSONB statistics
            def get_stat_value(stat: Dict, key: str) -> float:
                statistics = stat.get('statistics', {})
                value = statistics.get(key)
                if value is None:
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            avg_possession = sum(get_stat_value(s, 'ball_possession') for s in stats) / total_matches
            avg_shots_on_goal = sum(get_stat_value(s, 'shots_on_goal') for s in stats) / total_matches
            avg_total_passes = sum(get_stat_value(s, 'total_passes') for s in stats) / total_matches
            avg_fouls = sum(get_stat_value(s, 'fouls') for s in stats) / total_matches
            avg_expected_goals = sum(get_stat_value(s, 'expected_goals') for s in stats) / total_matches
            
            logger.info(f"Statistics summary calculated for team {team_id} ({total_matches} matches)")
            
            return {
                'team_id': team_id,
                'total_matches': total_matches,
                'avg_possession': round(avg_possession, 2),
                'avg_shots_on_goal': round(avg_shots_on_goal, 2),
                'avg_total_passes': round(avg_total_passes, 2),
                'avg_fouls': round(avg_fouls, 2),
                'avg_expected_goals': round(avg_expected_goals, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics summary: {str(e)}", exc_info=True)
            return {
                'team_id': team_id,
                'total_matches': 0,
                'avg_possession': 0,
                'avg_shots_on_goal': 0,
                'avg_total_passes': 0,
                'avg_fouls': 0,
                'avg_expected_goals': 0,
                'error': str(e)
            }
    
    async def _resolve_match_uuid(
        self,
        api_match_id: str
    ) -> Optional[str]:
        """
        Get match UUID from database using API-Football match ID.
        
        Args:
            api_match_id: API-Football match/fixture ID (e.g., "868023")
            
        Returns:
            Match UUID if found, None otherwise
            
        Note:
            Matches table has api_football_id column for mapping.
        """
        try:
            logger.info(f"Resolving match UUID for API ID {api_match_id}")
            
            response = self.supabase.table('matches') \
                .select('id') \
                .eq('api_football_id', api_match_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                match_uuid = response.data[0]['id']
                logger.info(f"Match UUID: {match_uuid}")
                return match_uuid
            else:
                logger.warning(f"Match not found for API ID {api_match_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving match UUID: {str(e)}", exc_info=True)
            return None
    
    async def _resolve_team_uuid(
        self,
        api_team_id: str
    ) -> Optional[str]:
        """
        Get team UUID from database using API-Football team ID.
        
        Args:
            api_team_id: API-Football team ID (e.g., "33" for Manchester United)
            
        Returns:
            Team UUID if found, None otherwise
            
        Note:
            Teams table has api_football_id column for mapping.
        """
        try:
            logger.info(f"Resolving team UUID for API ID {api_team_id}")
            
            response = self.supabase.table('teams') \
                .select('id') \
                .eq('api_football_id', api_team_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                team_uuid = response.data[0]['id']
                logger.info(f"Team UUID: {team_uuid}")
                return team_uuid
            else:
                logger.warning(f"Team not found for API ID {api_team_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving team UUID: {str(e)}", exc_info=True)
            return None
