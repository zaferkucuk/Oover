"""
Fetch Teams Management Command

This command fetches team data from external APIs (Football-Data.org or API-Football)
and stores them in the database. This is a one-time fetch operation for initial data load.

Usage Examples:
    # Fetch teams from all European leagues (default provider: football-data)
    python manage.py fetch_teams --all-european
    
    # Fetch teams from a specific league
    python manage.py fetch_teams --league PL
    
    # Fetch teams from a specific country
    python manage.py fetch_teams --country GB --provider api-football
    
    # Fetch teams from multiple leagues
    python manage.py fetch_teams --league PL --league SA --league BL1
    
    # Dry run to see what would be fetched
    python manage.py fetch_teams --all-european --dry-run
    
    # Fetch with specific provider
    python manage.py fetch_teams --all-european --provider api-football

Features:
    - One-time fetch operation for initial data load
    - Support for multiple filters (league, country, all-european)
    - Progress reporting with detailed statistics
    - Dry-run mode for testing
    - Comprehensive error handling
    - Provider selection (football-data or api-football)

Author: Oover Development Team
Created: 2025-10-30
Updated: 2025-10-30 (Bug fix for service method call)
"""

from typing import Dict, Any, Optional, List
from django.core.management.base import CommandError

from .base_teams_command import BaseTeamsCommand
from ...services.teams_service import TeamsService


class Command(BaseTeamsCommand):
    """
    Management command to fetch teams from external APIs.
    
    This command extends BaseTeamsCommand to provide one-time fetch
    functionality for loading team data into the database.
    """
    
    help = (
        'Fetch teams from external APIs (Football-Data.org or API-Football). '
        'Use for initial data load or one-time fetch operations.'
    )
    
    def add_custom_arguments(self, parser) -> None:
        """
        Add custom arguments specific to fetch_teams command.
        
        Args:
            parser: Django management command argument parser
        """
        # Filter options (mutually exclusive group)
        filter_group = parser.add_mutually_exclusive_group()
        
        filter_group.add_argument(
            '--league',
            action='append',
            dest='leagues',
            help='Fetch teams from specific league(s). Can be used multiple times. '
                 'Example: --league PL --league SA'
        )
        
        filter_group.add_argument(
            '--country',
            help='Fetch teams from specific country code. '
                 'Example: --country GB (for England)'
        )
        
        filter_group.add_argument(
            '--all-european',
            action='store_true',
            dest='all_european',
            help='Fetch teams from all top European leagues '
                 '(Premier League, La Liga, Serie A, Bundesliga, Ligue 1)'
        )
        
        # Additional options
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of teams to fetch (useful for testing)'
        )
    
    def validate_options(self, options: Dict[str, Any]) -> None:
        """
        Validate command options.
        
        Args:
            options: Dictionary of command options
            
        Raises:
            CommandError: If options are invalid
        """
        # Call parent validation first
        super().validate_options(options)
        
        # Ensure at least one filter is provided
        if not any([
            options.get('leagues'),
            options.get('country'),
            options.get('all_european')
        ]):
            raise CommandError(
                'At least one filter must be provided: '
                '--league, --country, or --all-european'
            )
        
        # Validate limit if provided
        limit = options.get('limit')
        if limit is not None and limit <= 0:
            raise CommandError('--limit must be a positive integer')
    
    def execute_teams_operation(
        self,
        service: TeamsService,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the fetch teams operation.
        
        Args:
            service: TeamsService instance
            options: Dictionary of command options
            
        Returns:
            Dictionary with operation results and statistics
        """
        # Get filter parameters
        leagues = options.get('leagues')
        country = options.get('country')
        all_european = options.get('all_european', False)
        limit = options.get('limit')
        provider = self.get_provider(options) or 'football-data'
        
        # Log operation details
        if all_european:
            self.stdout.write('Fetching teams from all European leagues...')
        elif leagues:
            self.stdout.write(f'Fetching teams from leagues: {", ".join(leagues)}')
        elif country:
            self.stdout.write(f'Fetching teams from country: {country}')
        
        if limit:
            self.stdout.write(f'Limit: {limit} teams')
        
        self.stdout.write(f'Provider: {provider}')
        self.stdout.write('')
        
        # Call service method
        try:
            # Determine which leagues to fetch
            if all_european:
                # Define top European leagues
                leagues = [
                    'PL',   # Premier League (England)
                    'PD',   # La Liga (Spain)
                    'SA',   # Serie A (Italy)
                    'BL1',  # Bundesliga (Germany)
                    'FL1',  # Ligue 1 (France)
                ]
                self.stdout.write(
                    f'📋 Processing {len(leagues)} European leagues: {", ".join(leagues)}\n'
                )
            
            # Initialize aggregated statistics
            total_stats = {
                'fetched': 0,
                'transformed': 0,
                'validated': 0,
                'saved': 0,
                'created': 0,
                'updated': 0,
                'failed': 0,
                'errors': []
            }
            
            # Execute fetch operation for each league
            if leagues:
                for idx, league_code in enumerate(leagues, 1):
                    self.stdout.write(
                        self.style.MIGRATE_LABEL(
                            f'[{idx}/{len(leagues)}] Fetching teams for {league_code}...'
                        )
                    )
                    
                    try:
                        # Call the actual service method with correct signature
                        league_stats = service.fetch_teams_from_provider(
                            provider=provider,
                            competition_id=league_code,
                            limit=limit
                        )
                        
                        # Aggregate statistics
                        for key in ['fetched', 'transformed', 'validated', 'saved', 
                                   'created', 'updated', 'failed']:
                            total_stats[key] += league_stats.get(key, 0)
                        
                        if 'errors' in league_stats and league_stats['errors']:
                            total_stats['errors'].extend(league_stats['errors'])
                        
                        # Display league-specific results
                        self.stdout.write(
                            f'   ✓ {league_stats.get("created", 0)} created, '
                            f'{league_stats.get("updated", 0)} updated, '
                            f'{league_stats.get("failed", 0)} failed\n'
                        )
                        
                    except Exception as e:
                        error_msg = f'Error fetching {league_code}: {str(e)}'
                        total_stats['errors'].append(error_msg)
                        self.stdout.write(
                            self.style.ERROR(f'   ✗ {error_msg}\n')
                        )
                        continue
            
            elif country:
                # Fetch by country
                self.stdout.write(f'Fetching teams for country: {country}...')
                
                total_stats = service.fetch_teams_from_provider(
                    provider=provider,
                    country_code=country,
                    limit=limit
                )
            
            # Return aggregated results
            return total_stats
            
        except Exception as e:
            # Log detailed error
            self.stderr.write(
                self.style.ERROR(
                    f'Error during fetch operation: {str(e)}'
                )
            )
            raise
    
    def get_operation_name(self) -> str:
        """
        Get the name of this operation for logging.
        
        Returns:
            Operation name string
        """
        return 'Fetch Teams'
    
    def get_success_message(self, stats: Dict[str, Any]) -> str:
        """
        Get custom success message with operation-specific details.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted success message
        """
        fetched = stats.get('fetched', 0)
        created = stats.get('created', 0)
        updated = stats.get('updated', 0)
        
        message_parts = [
            f'Successfully processed {fetched} teams from API',
        ]
        
        if created > 0:
            message_parts.append(f'{created} new teams created')
        
        if updated > 0:
            message_parts.append(f'{updated} teams updated')
        
        return ' | '.join(message_parts)
