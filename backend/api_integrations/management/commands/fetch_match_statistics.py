"""
Django Management Command: fetch_match_statistics

This command fetches match statistics data from API-Football and saves it to the database.
It provides a CLI interface for manual and automated statistics data collection.

Features:
    - Fetch statistics for specific match ID
    - Fetch statistics for all completed matches in a league
    - Fetch statistics for matches in date range
    - Update existing statistics data
    - Batch processing with configurable limit
    - Dry-run mode for testing without saving
    - Verbose output for detailed progress
    - Error handling and reporting
    - Final summary with statistics

Usage Examples:
    # Fetch statistics for specific match
    python manage.py fetch_match_statistics --match-id 868023
    
    # Fetch for Premier League 2024 (all completed matches)
    python manage.py fetch_match_statistics --league-id 39 --season 2024
    
    # Fetch recent completed matches (last 7 days)
    python manage.py fetch_match_statistics --date-from 2024-11-01 --date-to 2024-11-07
    
    # Fetch with limit and verbose output
    python manage.py fetch_match_statistics --league-id 39 --season 2024 --limit 10 --verbose
    
    # Update existing statistics
    python manage.py fetch_match_statistics --league-id 39 --season 2024 --update
    
    # Dry run for testing
    python manage.py fetch_match_statistics --match-id 868023 --dry-run
    
    # Fetch only completed matches
    python manage.py fetch_match_statistics --league-id 39 --season 2024 --completed-only

Author: Zafer Kucuk
Created: 2025-11-02
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from api_integrations.services.statistics_service import StatisticsService
from api_integrations.services.matches_service import MatchesService

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for fetching match statistics from API-Football.
    
    This command provides a CLI interface to the StatisticsService, allowing
    manual and automated data collection for match statistics.
    """
    
    help = 'Fetch and save match statistics data from API-Football'
    
    def __init__(self):
        """Initialize the command with services."""
        super().__init__()
        self.statistics_service = StatisticsService()
        self.matches_service = MatchesService()
        self.stats = {
            'total_matches': 0,
            'successful': 0,
            'failed': 0,
            'statistics_saved': 0,
            'skipped': 0,
            'errors': []
        }
    
    def add_arguments(self, parser):
        """
        Add command line arguments.
        
        Args:
            parser: ArgumentParser instance
        """
        # Match selection
        parser.add_argument(
            '--match-id',
            type=str,
            help='API-Football match/fixture ID (e.g., 868023)'
        )
        
        # League and season selection
        parser.add_argument(
            '--league-id',
            type=str,
            help='API-Football league ID (e.g., 39 for Premier League)'
        )
        
        parser.add_argument(
            '--season',
            type=int,
            help='Season year (e.g., 2024)'
        )
        
        # Date range filtering
        parser.add_argument(
            '--date-from',
            type=str,
            help='Start date for match filter (YYYY-MM-DD format)'
        )
        
        parser.add_argument(
            '--date-to',
            type=str,
            help='End date for match filter (YYYY-MM-DD format)'
        )
        
        # Filtering options
        parser.add_argument(
            '--completed-only',
            action='store_true',
            help='Only fetch statistics for completed matches (status: FT, AET, PEN)'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of matches to process (default: no limit)'
        )
        
        # Operations
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing statistics data'
        )
        
        # Testing and output
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test run without saving to database'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with detailed progress'
        )
    
    def handle(self, *args, **options):
        """
        Main command handler.
        
        Processes command line arguments and executes appropriate actions.
        
        Args:
            *args: Positional arguments (unused)
            **options: Command line options dictionary
            
        Raises:
            CommandError: If invalid arguments or execution fails
        """
        # Extract options
        match_id = options.get('match_id')
        league_id = options.get('league_id')
        season = options.get('season')
        date_from = options.get('date_from')
        date_to = options.get('date_to')
        completed_only = options.get('completed_only')
        limit = options.get('limit')
        update = options.get('update')
        dry_run = options.get('dry_run')
        verbose = options.get('verbose')
        
        # Configure logging level
        if verbose:
            logger.setLevel(logging.DEBUG)
            self.stdout.write(self.style.SUCCESS('Verbose mode enabled'))
        
        # Validate arguments
        if not match_id and not league_id and not date_from:
            raise CommandError(
                'One of --match-id, --league-id, or --date-from must be specified'
            )
        
        if league_id and not season:
            raise CommandError(
                '--season is required when using --league-id'
            )
        
        if date_from and not date_to:
            # Default to today if date_to not specified
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No data will be saved')
            )
        
        # Execute appropriate action
        try:
            if match_id:
                self._fetch_single_match(match_id, update, dry_run, verbose)
            elif league_id:
                self._fetch_league_matches(
                    league_id, season, completed_only, limit, update, dry_run, verbose
                )
            elif date_from:
                self._fetch_date_range(
                    date_from, date_to, completed_only, limit, update, dry_run, verbose
                )
            
            # Print final statistics
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}", exc_info=True)
            raise CommandError(f"Failed to fetch statistics: {str(e)}")
    
    def _fetch_single_match(
        self,
        match_id: str,
        update: bool,
        dry_run: bool,
        verbose: bool
    ):
        """
        Fetch statistics for a single match.
        
        Args:
            match_id: API-Football match ID
            update: Whether this is an update operation
            dry_run: Test mode flag
            verbose: Verbose output flag
        """
        self.stats['total_matches'] = 1
        
        action = "Updating" if update else "Fetching"
        self.stdout.write(f"{action} statistics for match {match_id}...")
        
        try:
            if not dry_run:
                result = asyncio.run(
                    self.statistics_service.fetch_and_save_statistics(
                        match_id=match_id
                    )
                )
                
                if result['success']:
                    self.stats['successful'] += 1
                    self.stats['statistics_saved'] += result['statistics_count']
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Success: {result['statistics_count']} statistics saved"
                        )
                    )
                    
                    if verbose:
                        self._show_match_details(result)
                else:
                    self.stats['failed'] += 1
                    error_msg = result.get('error', 'Unknown error')
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed: {error_msg}")
                    )
                    self.stats['errors'].append(error_msg)
            else:
                # Dry run - just validate parameters
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Would fetch statistics for match {match_id}"
                    )
                )
                self.stats['successful'] += 1
                
        except Exception as e:
            self.stats['failed'] += 1
            error_msg = str(e)
            self.stats['errors'].append(error_msg)
            self.stdout.write(
                self.style.ERROR(f"❌ Error: {error_msg}")
            )
            logger.error(f"Failed to fetch statistics: {error_msg}", exc_info=True)
    
    def _fetch_league_matches(
        self,
        league_id: str,
        season: int,
        completed_only: bool,
        limit: Optional[int],
        update: bool,
        dry_run: bool,
        verbose: bool
    ):
        """
        Fetch statistics for all matches in a league.
        
        Args:
            league_id: API-Football league ID
            season: Season year
            completed_only: Only fetch completed matches
            limit: Maximum number of matches to process
            update: Whether this is an update operation
            dry_run: Test mode flag
            verbose: Verbose output flag
        """
        action = "Updating" if update else "Fetching"
        status_filter = " (completed only)" if completed_only else ""
        limit_info = f" (limit: {limit})" if limit else ""
        
        self.stdout.write(
            f"{action} statistics for league {league_id}, season {season}"
            f"{status_filter}{limit_info}..."
        )
        
        try:
            # Get matches for the league
            matches_result = asyncio.run(
                self.matches_service.fetch_and_save_matches(
                    league_id=league_id,
                    season=season
                )
            )
            
            if not matches_result['success']:
                raise CommandError(
                    f"Failed to fetch matches: {matches_result.get('error', 'Unknown error')}"
                )
            
            # Get match IDs from database
            matches = asyncio.run(
                self._get_matches_for_league(league_id, season, completed_only, limit)
            )
            
            if not matches:
                self.stdout.write(
                    self.style.WARNING("No matches found for the specified criteria")
                )
                return
            
            self.stats['total_matches'] = len(matches)
            self.stdout.write(f"Found {len(matches)} matches to process")
            
            # Process each match
            for i, match in enumerate(matches, 1):
                match_id = match['api_football_id']
                home_team = match.get('home_team_name', 'Unknown')
                away_team = match.get('away_team_name', 'Unknown')
                
                if verbose:
                    self.stdout.write(
                        f"\n[{i}/{len(matches)}] {home_team} vs {away_team} "
                        f"(Match ID: {match_id})"
                    )
                else:
                    # Show progress without verbose details
                    if i % 10 == 0 or i == len(matches):
                        self.stdout.write(f"Progress: {i}/{len(matches)} matches processed")
                
                try:
                    if not dry_run:
                        result = asyncio.run(
                            self.statistics_service.fetch_and_save_statistics(
                                match_id=match_id
                            )
                        )
                        
                        if result['success']:
                            self.stats['successful'] += 1
                            self.stats['statistics_saved'] += result['statistics_count']
                            
                            if verbose:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  ✅ {result['statistics_count']} statistics saved"
                                    )
                                )
                        else:
                            self.stats['failed'] += 1
                            error_msg = result.get('error', 'Unknown error')
                            
                            if verbose:
                                self.stdout.write(
                                    self.style.ERROR(f"  ❌ Failed: {error_msg}")
                                )
                            
                            self.stats['errors'].append(
                                f"Match {match_id}: {error_msg}"
                            )
                    else:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  [DRY RUN] Would fetch statistics"
                                )
                            )
                        self.stats['successful'] += 1
                    
                    # Small delay to respect rate limits
                    if not dry_run and i < len(matches):
                        await asyncio.sleep(0.5)  # 2 requests per second
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    error_msg = str(e)
                    self.stats['errors'].append(f"Match {match_id}: {error_msg}")
                    
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Error: {error_msg}")
                        )
                    
                    logger.error(
                        f"Failed to fetch statistics for match {match_id}: {error_msg}",
                        exc_info=True
                    )
            
        except Exception as e:
            logger.error(
                f"Failed to fetch league matches: {str(e)}",
                exc_info=True
            )
            raise
    
    def _fetch_date_range(
        self,
        date_from: str,
        date_to: str,
        completed_only: bool,
        limit: Optional[int],
        update: bool,
        dry_run: bool,
        verbose: bool
    ):
        """
        Fetch statistics for matches in date range.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            completed_only: Only fetch completed matches
            limit: Maximum number of matches to process
            update: Whether this is an update operation
            dry_run: Test mode flag
            verbose: Verbose output flag
        """
        action = "Updating" if update else "Fetching"
        status_filter = " (completed only)" if completed_only else ""
        limit_info = f" (limit: {limit})" if limit else ""
        
        self.stdout.write(
            f"{action} statistics for matches from {date_from} to {date_to}"
            f"{status_filter}{limit_info}..."
        )
        
        try:
            # Get matches for the date range
            matches = asyncio.run(
                self._get_matches_for_date_range(
                    date_from, date_to, completed_only, limit
                )
            )
            
            if not matches:
                self.stdout.write(
                    self.style.WARNING("No matches found for the specified date range")
                )
                return
            
            self.stats['total_matches'] = len(matches)
            self.stdout.write(f"Found {len(matches)} matches to process")
            
            # Process each match (similar to league matches)
            for i, match in enumerate(matches, 1):
                match_id = match['api_football_id']
                match_date = match.get('match_date', 'Unknown date')
                home_team = match.get('home_team_name', 'Unknown')
                away_team = match.get('away_team_name', 'Unknown')
                
                if verbose:
                    self.stdout.write(
                        f"\n[{i}/{len(matches)}] {match_date}: {home_team} vs {away_team} "
                        f"(Match ID: {match_id})"
                    )
                else:
                    if i % 10 == 0 or i == len(matches):
                        self.stdout.write(f"Progress: {i}/{len(matches)} matches processed")
                
                try:
                    if not dry_run:
                        result = asyncio.run(
                            self.statistics_service.fetch_and_save_statistics(
                                match_id=match_id
                            )
                        )
                        
                        if result['success']:
                            self.stats['successful'] += 1
                            self.stats['statistics_saved'] += result['statistics_count']
                            
                            if verbose:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  ✅ {result['statistics_count']} statistics saved"
                                    )
                                )
                        else:
                            self.stats['failed'] += 1
                            error_msg = result.get('error', 'Unknown error')
                            
                            if verbose:
                                self.stdout.write(
                                    self.style.ERROR(f"  ❌ Failed: {error_msg}")
                                )
                            
                            self.stats['errors'].append(
                                f"Match {match_id}: {error_msg}"
                            )
                    else:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  [DRY RUN] Would fetch statistics"
                                )
                            )
                        self.stats['successful'] += 1
                    
                    # Small delay to respect rate limits
                    if not dry_run and i < len(matches):
                        await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    error_msg = str(e)
                    self.stats['errors'].append(f"Match {match_id}: {error_msg}")
                    
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Error: {error_msg}")
                        )
            
        except Exception as e:
            logger.error(
                f"Failed to fetch date range matches: {str(e)}",
                exc_info=True
            )
            raise
    
    async def _get_matches_for_league(
        self,
        league_id: str,
        season: int,
        completed_only: bool,
        limit: Optional[int]
    ) -> List[Dict]:
        """
        Get matches for a league from database.
        
        Args:
            league_id: API-Football league ID
            season: Season year
            completed_only: Only return completed matches
            limit: Maximum number of matches
            
        Returns:
            List of match dictionaries
        """
        try:
            # Get league UUID
            league_uuid = await self.matches_service._get_league_uuid(league_id)
            
            if not league_uuid:
                logger.warning(f"League {league_id} not found in database")
                return []
            
            # Build query
            query = """
                SELECT 
                    m.id,
                    m.api_football_id,
                    m.match_date,
                    m.status,
                    ht.name as home_team_name,
                    at.name as away_team_name
                FROM matches m
                JOIN teams ht ON m.home_team_id = ht.id
                JOIN teams at ON m.away_team_id = at.id
                WHERE m.league_id = %s
                AND m.season = %s
            """
            params = [league_uuid, season]
            
            # Add status filter for completed matches
            if completed_only:
                query += " AND m.status IN ('FT', 'AET', 'PEN')"
            
            # Add ordering and limit
            query += " ORDER BY m.match_date DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            # Execute query
            result = await self.matches_service.db_client.execute_query(query, params)
            
            return result if result else []
            
        except Exception as e:
            logger.error(f"Failed to get matches for league: {str(e)}", exc_info=True)
            return []
    
    async def _get_matches_for_date_range(
        self,
        date_from: str,
        date_to: str,
        completed_only: bool,
        limit: Optional[int]
    ) -> List[Dict]:
        """
        Get matches for date range from database.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            completed_only: Only return completed matches
            limit: Maximum number of matches
            
        Returns:
            List of match dictionaries
        """
        try:
            # Build query
            query = """
                SELECT 
                    m.id,
                    m.api_football_id,
                    m.match_date,
                    m.status,
                    ht.name as home_team_name,
                    at.name as away_team_name
                FROM matches m
                JOIN teams ht ON m.home_team_id = ht.id
                JOIN teams at ON m.away_team_id = at.id
                WHERE m.match_date >= %s
                AND m.match_date <= %s
            """
            params = [date_from, date_to]
            
            # Add status filter
            if completed_only:
                query += " AND m.status IN ('FT', 'AET', 'PEN')"
            
            # Add ordering and limit
            query += " ORDER BY m.match_date DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            # Execute query
            result = await self.statistics_service.db_client.execute_query(query, params)
            
            return result if result else []
            
        except Exception as e:
            logger.error(
                f"Failed to get matches for date range: {str(e)}",
                exc_info=True
            )
            return []
    
    def _show_match_details(self, result: Dict):
        """
        Show detailed match statistics.
        
        Args:
            result: Result dictionary from StatisticsService
        """
        if not result.get('statistics'):
            return
        
        self.stdout.write("\n📊 Match Statistics:")
        
        for stats in result['statistics']:
            team_name = stats.get('team_name', 'Unknown Team')
            statistics = stats.get('statistics', {})
            
            self.stdout.write(f"\n  🏟️  {team_name}:")
            
            # Show key statistics
            if 'ball_possession' in statistics:
                self.stdout.write(
                    f"    Possession: {statistics['ball_possession']}%"
                )
            
            if 'shots_on_goal' in statistics:
                total_shots = statistics.get('total_shots', 0)
                self.stdout.write(
                    f"    Shots: {statistics['shots_on_goal']}/{total_shots}"
                )
            
            if 'total_passes' in statistics:
                pass_accuracy = statistics.get('passes_percentage', 0)
                self.stdout.write(
                    f"    Passes: {statistics['total_passes']} ({pass_accuracy}% accuracy)"
                )
            
            if 'expected_goals' in statistics:
                self.stdout.write(
                    f"    xG: {statistics['expected_goals']}"
                )
    
    def _print_summary(self):
        """Print final execution summary."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 EXECUTION SUMMARY")
        self.stdout.write("="*60)
        
        self.stdout.write(f"Total matches processed: {self.stats['total_matches']}")
        self.stdout.write(
            self.style.SUCCESS(f"Successful: {self.stats['successful']}")
        )
        
        if self.stats['failed'] > 0:
            self.stdout.write(
                self.style.ERROR(f"Failed: {self.stats['failed']}")
            )
        
        if self.stats['skipped'] > 0:
            self.stdout.write(
                self.style.WARNING(f"Skipped: {self.stats['skipped']}")
            )
        
        self.stdout.write(
            f"Total statistics saved: {self.stats['statistics_saved']}"
        )
        
        if self.stats['errors']:
            self.stdout.write("\n❌ Errors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                self.stdout.write(f"  - {error}")
            
            if len(self.stats['errors']) > 10:
                self.stdout.write(
                    f"  ... and {len(self.stats['errors']) - 10} more errors"
                )
        
        self.stdout.write("="*60)
        
        # Return appropriate message
        if self.stats['failed'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  Some operations failed. Check logs for details."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✅ All operations completed successfully!")
            )
