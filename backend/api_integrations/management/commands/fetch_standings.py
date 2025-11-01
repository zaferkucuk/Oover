"""
Django Management Command: fetch_standings

This command fetches league standings data from API-Football and saves it to the database.
It provides a CLI interface for manual and automated standings data collection.

Features:
    - Fetch standings for specific league and season
    - Fetch standings for all configured leagues
    - Update existing standings data
    - Dry-run mode for testing without saving
    - Verbose output for detailed progress
    - Error handling and reporting

Usage Examples:
    # Fetch Premier League 2024 standings
    python manage.py fetch_standings --league-id 39 --season 2024
    
    # Fetch with verbose output
    python manage.py fetch_standings --league-id 39 --season 2024 --verbose
    
    # Update all configured leagues
    python manage.py fetch_standings --all --update
    
    # Dry run for testing
    python manage.py fetch_standings --league-id 39 --season 2024 --dry-run
    
    # Fetch specific team's standing
    python manage.py fetch_standings --league-id 39 --season 2024 --team-id 33

Author: Zafer Kucuk
Created: 2025-11-01
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import asyncio
import logging
from typing import List, Dict, Optional

from api_integrations.services.standings_service import StandingsService

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for fetching standings data from API-Football.
    
    This command provides a CLI interface to the StandingsService, allowing
    manual and automated data collection for league standings.
    """
    
    help = 'Fetch and save league standings data from API-Football'
    
    def __init__(self):
        """Initialize the command with standings service."""
        super().__init__()
        self.service = StandingsService()
        self.stats = {
            'total_leagues': 0,
            'successful': 0,
            'failed': 0,
            'standings_saved': 0,
            'errors': []
        }
    
    def add_arguments(self, parser):
        """
        Add command line arguments.
        
        Args:
            parser: ArgumentParser instance
        """
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
        
        parser.add_argument(
            '--team-id',
            type=str,
            help='Optional: API-Football team ID to fetch specific team standing'
        )
        
        # Bulk operations
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fetch standings for all configured leagues'
        )
        
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing standings data (use with --all or specific league)'
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
        league_id = options.get('league_id')
        season = options.get('season')
        team_id = options.get('team_id')
        fetch_all = options.get('all')
        update = options.get('update')
        dry_run = options.get('dry_run')
        verbose = options.get('verbose')
        
        # Configure logging level
        if verbose:
            logger.setLevel(logging.DEBUG)
            self.stdout.write(self.style.SUCCESS('Verbose mode enabled'))
        
        # Validate arguments
        if not fetch_all and not league_id:
            raise CommandError(
                'Either --league-id or --all must be specified'
            )
        
        if league_id and not season:
            raise CommandError(
                '--season is required when using --league-id'
            )
        
        if team_id and not league_id:
            raise CommandError(
                '--team-id requires --league-id to be specified'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No data will be saved')
            )
        
        # Execute appropriate action
        try:
            if fetch_all:
                self._fetch_all_leagues(season, update, dry_run, verbose)
            else:
                self._fetch_single_league(
                    league_id, season, team_id, update, dry_run, verbose
                )
            
            # Print final statistics
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}", exc_info=True)
            raise CommandError(f"Failed to fetch standings: {str(e)}")
    
    def _fetch_single_league(
        self,
        league_id: str,
        season: int,
        team_id: Optional[str],
        update: bool,
        dry_run: bool,
        verbose: bool
    ):
        """
        Fetch standings for a single league.
        
        Args:
            league_id: API-Football league ID
            season: Season year
            team_id: Optional team ID for specific team
            update: Whether this is an update operation
            dry_run: Test mode flag
            verbose: Verbose output flag
        """
        self.stats['total_leagues'] = 1
        
        action = "Updating" if update else "Fetching"
        team_info = f" (team: {team_id})" if team_id else ""
        
        self.stdout.write(
            f"{action} standings for league {league_id}, season {season}{team_info}..."
        )
        
        try:
            # Fetch and save standings
            if not dry_run:
                result = asyncio.run(
                    self.service.fetch_and_save_standings(
                        league_id=league_id,
                        season=season,
                        team_id=team_id
                    )
                )
                
                if result['success']:
                    self.stats['successful'] += 1
                    self.stats['standings_saved'] += result['standings_count']
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Success: {result['standings_count']} standings saved "
                            f"({result['inserted']} inserted, {result['updated']} updated)"
                        )
                    )
                    
                    if verbose and result.get('errors'):
                        self.stdout.write(
                            self.style.WARNING(
                                f"Warnings: {len(result['errors'])} transformation errors"
                            )
                        )
                        for error in result['errors'][:5]:  # Show first 5 errors
                            self.stdout.write(f"  - {error}")
                else:
                    self.stats['failed'] += 1
                    error_msg = result.get('errors', ['Unknown error'])[0]
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed: {error_msg}")
                    )
                    self.stats['errors'].append(error_msg)
            else:
                # Dry run - just validate parameters
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Would fetch standings for league {league_id}, season {season}"
                    )
                )
                self.stats['successful'] += 1
            
            # Show summary if verbose
            if verbose and not dry_run:
                self._show_league_summary(league_id, season)
                
        except Exception as e:
            self.stats['failed'] += 1
            error_msg = str(e)
            self.stats['errors'].append(error_msg)
            self.stdout.write(
                self.style.ERROR(f"❌ Error: {error_msg}")
            )
            logger.error(f"Failed to fetch standings: {error_msg}", exc_info=True)
    
    def _fetch_all_leagues(
        self,
        season: Optional[int],
        update: bool,
        dry_run: bool,
        verbose: bool
    ):
        """
        Fetch standings for all configured leagues.
        
        Args:
            season: Optional season year (uses current if not specified)
            update: Whether this is an update operation
            dry_run: Test mode flag
            verbose: Verbose output flag
        """
        # Get configured leagues from settings
        configured_leagues = self._get_configured_leagues()
        
        if not configured_leagues:
            raise CommandError(
                'No leagues configured. Add STANDINGS_LEAGUES to settings.'
            )
        
        # Use provided season or current year
        if not season:
            from datetime import datetime
            season = datetime.now().year
            self.stdout.write(f"Using current season: {season}")
        
        self.stats['total_leagues'] = len(configured_leagues)
        
        action = "Updating" if update else "Fetching"
        self.stdout.write(
            f"{action} standings for {len(configured_leagues)} leagues, season {season}..."
        )
        
        # Fetch each league
        for i, league_config in enumerate(configured_leagues, 1):
            league_id = league_config['id']
            league_name = league_config.get('name', f'League {league_id}')
            
            self.stdout.write(
                f"\n[{i}/{len(configured_leagues)}] {league_name} (ID: {league_id})"
            )
            
            try:
                if not dry_run:
                    result = asyncio.run(
                        self.service.fetch_and_save_standings(
                            league_id=league_id,
                            season=season
                        )
                    )
                    
                    if result['success']:
                        self.stats['successful'] += 1
                        self.stats['standings_saved'] += result['standings_count']
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✅ {result['standings_count']} standings saved"
                            )
                        )
                    else:
                        self.stats['failed'] += 1
                        error_msg = result.get('errors', ['Unknown error'])[0]
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Failed: {error_msg}")
                        )
                        self.stats['errors'].append(f"{league_name}: {error_msg}")
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [DRY RUN] Would fetch standings for {league_name}"
                        )
                    )
                    self.stats['successful'] += 1
                
            except Exception as e:
                self.stats['failed'] += 1
                error_msg = str(e)
                self.stats['errors'].append(f"{league_name}: {error_msg}")
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Error: {error_msg}")
                )
                logger.error(
                    f"Failed to fetch standings for {league_name}: {error_msg}",
                    exc_info=True
                )
    
    def _get_configured_leagues(self) -> List[Dict]:
        """
        Get configured leagues from Django settings.
        
        Returns:
            List of league configuration dictionaries
            
        Note:
            Expected setting format:
            STANDINGS_LEAGUES = [
                {'id': '39', 'name': 'Premier League'},
                {'id': '140', 'name': 'La Liga'},
                ...
            ]
        """
        # Try to get from settings
        leagues = getattr(settings, 'STANDINGS_LEAGUES', None)
        
        if leagues:
            return leagues
        
        # Fallback to major European leagues
        return [
            {'id': '39', 'name': 'Premier League'},
            {'id': '140', 'name': 'La Liga'},
            {'id': '78', 'name': 'Bundesliga'},
            {'id': '135', 'name': 'Serie A'},
            {'id': '61', 'name': 'Ligue 1'},
        ]
    
    def _show_league_summary(self, league_id: str, season: int):
        """
        Show summary statistics for a league.
        
        Args:
            league_id: API-Football league ID
            season: Season year
        """
        try:
            # Get league UUID first
            league_uuid = asyncio.run(
                self.service._get_league_uuid(league_id)
            )
            
            if not league_uuid:
                return
            
            # Get summary
            summary = asyncio.run(
                self.service.get_standings_summary(
                    league_id=league_uuid,
                    season=season
                )
            )
            
            if summary['total_teams'] > 0:
                self.stdout.write("\n📊 League Summary:")
                self.stdout.write(f"  Total teams: {summary['total_teams']}")
                
                if summary['leader']:
                    self.stdout.write(
                        f"  🥇 Leader: Position {summary['leader']['position']} "
                        f"({summary['leader']['points']} pts)"
                    )
                
                if summary['last_place']:
                    self.stdout.write(
                        f"  🔻 Last: Position {summary['last_place']['position']} "
                        f"({summary['last_place']['points']} pts)"
                    )
                
                if summary['promotion_zone']:
                    self.stdout.write(
                        f"  ⬆️  Promotion zone: {len(summary['promotion_zone'])} teams"
                    )
                
                if summary['relegation_zone']:
                    self.stdout.write(
                        f"  ⬇️  Relegation zone: {len(summary['relegation_zone'])} teams"
                    )
                
        except Exception as e:
            logger.debug(f"Could not show summary: {str(e)}")
    
    def _print_summary(self):
        """Print final execution summary."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 EXECUTION SUMMARY")
        self.stdout.write("="*60)
        
        self.stdout.write(f"Total leagues processed: {self.stats['total_leagues']}")
        self.stdout.write(
            self.style.SUCCESS(f"Successful: {self.stats['successful']}")
        )
        
        if self.stats['failed'] > 0:
            self.stdout.write(
                self.style.ERROR(f"Failed: {self.stats['failed']}")
            )
        
        self.stdout.write(
            f"Total standings saved: {self.stats['standings_saved']}"
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
        
        # Return appropriate exit code
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
