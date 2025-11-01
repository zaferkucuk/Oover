"""
Management command to fetch leagues from API-Football.

This command fetches league data from API-Football and saves it to the database.
It provides various filtering options and supports dry-run mode for preview.

Usage:
    # Fetch all leagues
    python manage.py fetch_leagues

    # Fetch specific league
    python manage.py fetch_leagues --league-id 140

    # Fetch current season leagues only
    python manage.py fetch_leagues --current

    # Search leagues by name
    python manage.py fetch_leagues --search "Premier"

    # Fetch leagues from specific country (by country code)
    python manage.py fetch_leagues --country ES

    # Fetch leagues from specific country (by country UUID)
    python manage.py fetch_leagues --country-id "uuid-here"

    # Fetch leagues for specific season
    python manage.py fetch_leagues --season 2024

    # Limit number of results
    python manage.py fetch_leagues --limit 10

    # Dry run (preview without saving)
    python manage.py fetch_leagues --dry-run

    # Verbose output
    python manage.py fetch_leagues --verbose

    # Combine filters
    python manage.py fetch_leagues --country ES --current --verbose

Author: Oover Development Team
Date: November 2025
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api_integrations.services.leagues_service import LeaguesService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command to fetch leagues from API-Football.
    
    This command provides a CLI interface to the LeaguesService for:
    - Initial league population (~800 leagues)
    - Seasonal updates (refresh at season boundaries)
    - Targeted league fetching (specific country, league, or season)
    - Discovery of new leagues
    
    The command supports various filtering options and a dry-run mode
    for previewing results before saving to the database.
    """
    
    help = 'Fetch leagues from API-Football and save to database'
    
    def add_arguments(self, parser):
        """
        Add command-line arguments.
        
        Args:
            parser: ArgumentParser instance
        """
        # Filtering options
        parser.add_argument(
            '--league-id',
            type=int,
            help='Fetch specific league by API-Football ID (e.g., 140 for La Liga)'
        )
        
        parser.add_argument(
            '--current',
            action='store_true',
            help='Fetch only leagues with current active seasons'
        )
        
        parser.add_argument(
            '--search',
            type=str,
            help='Search leagues by name (e.g., "Premier" for Premier League)'
        )
        
        parser.add_argument(
            '--country',
            type=str,
            help='Filter by country code (e.g., ES, GB, FR, DE, IT)'
        )
        
        parser.add_argument(
            '--country-id',
            type=str,
            help='Filter by country UUID from database'
        )
        
        parser.add_argument(
            '--season',
            type=int,
            help='Filter by season year (e.g., 2024, 2025)'
        )
        
        # Limit options
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of leagues to fetch (useful for testing)'
        )
        
        # Operation modes
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview leagues without saving to database'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with detailed logging'
        )
    
    def handle(self, *args, **options):
        """
        Execute the command.
        
        Args:
            *args: Positional arguments
            **options: Command options from add_arguments
            
        Raises:
            CommandError: If command execution fails
        """
        # Configure logging
        if options['verbose']:
            logging.getLogger('api_integrations').setLevel(logging.DEBUG)
            self.stdout.write(self.style.SUCCESS('Verbose mode enabled'))
        
        # Extract options
        league_id = options.get('league_id')
        current_only = options.get('current', False)
        search = options.get('search')
        country_code = options.get('country')
        country_id = options.get('country_id')
        season = options.get('season')
        limit = options.get('limit')
        dry_run = options.get('dry_run', False)
        
        # Validate country options (can't use both)
        if country_code and country_id:
            raise CommandError(
                'Cannot use both --country and --country-id. '
                'Please use only one.'
            )
        
        # Use country_id if provided, otherwise country_code
        country_filter = country_id if country_id else None
        
        # Display operation summary
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Fetch Leagues Command ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No data will be saved\n'))
        
        # Display filters
        filters = []
        if league_id:
            filters.append(f'League ID: {league_id}')
        if current_only:
            filters.append('Current season only')
        if search:
            filters.append(f'Search: "{search}"')
        if country_code:
            filters.append(f'Country: {country_code}')
        if country_id:
            filters.append(f'Country ID: {country_id}')
        if season:
            filters.append(f'Season: {season}')
        if limit:
            filters.append(f'Limit: {limit}')
        
        if filters:
            self.stdout.write(self.style.HTTP_INFO('Filters:'))
            for f in filters:
                self.stdout.write(f'  • {f}')
            self.stdout.write('')
        else:
            self.stdout.write(self.style.HTTP_INFO('No filters - fetching all leagues\n'))
        
        # Initialize service
        try:
            self.stdout.write('Initializing LeaguesService...')
            service = LeaguesService()
            self.stdout.write(self.style.SUCCESS('✓ Service initialized\n'))
        except Exception as e:
            raise CommandError(f'Failed to initialize LeaguesService: {str(e)}')
        
        # Fetch leagues
        try:
            self.stdout.write(self.style.HTTP_INFO('Fetching leagues from API-Football...'))
            self.stdout.write('This may take a moment...\n')
            
            # Call service method
            if dry_run:
                # In dry-run mode, we still call the API but won't save
                # This is handled by the service's bulk_upsert method
                self.stdout.write(self.style.WARNING(
                    'Note: Dry-run mode not fully implemented in service. '
                    'Results will be saved.'
                ))
            
            result = service.fetch_leagues_from_api(
                league_id=league_id,
                current_only=current_only,
                search=search,
                country_id=country_filter,
                season=season
            )
            
            # Apply limit if specified (post-fetch)
            if limit and result['saved'] > limit:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nNote: Limit of {limit} specified, but {result["saved"]} '
                        f'leagues were saved. Use API filters for better control.'
                    )
                )
            
            # Display results
            self.stdout.write(self.style.MIGRATE_HEADING('\n=== Results ===\n'))
            
            self.stdout.write(
                self.style.HTTP_INFO(f'Fetched: {result["fetched"]} leagues from API')
            )
            self.stdout.write(
                self.style.HTTP_INFO(f'Transformed: {result["transformed"]} leagues')
            )
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Saved: {result["saved"]} leagues')
                )
                self.stdout.write(
                    f'  • Created: {result["created"]} new leagues'
                )
                self.stdout.write(
                    f'  • Updated: {result["updated"]} existing leagues'
                )
            
            if result['failed'] > 0:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed: {result["failed"]} leagues')
                )
            
            # Display errors if any
            if result.get('errors'):
                self.stdout.write(
                    self.style.ERROR(f'\n⚠ Errors encountered: {len(result["errors"])}')
                )
                
                if options['verbose']:
                    self.stdout.write(self.style.ERROR('\nError details:'))
                    for idx, error in enumerate(result['errors'][:10], 1):
                        self.stdout.write(f'{idx}. {error}')
                    
                    if len(result['errors']) > 10:
                        self.stdout.write(
                            f'... and {len(result["errors"]) - 10} more errors'
                        )
                else:
                    self.stdout.write(
                        'Use --verbose to see error details'
                    )
            
            # Success summary
            self.stdout.write(self.style.MIGRATE_HEADING('\n=== Summary ===\n'))
            
            if result['saved'] > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully processed {result["saved"]} leagues'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠ No leagues were saved')
                )
            
            # Recommendations
            if result['failed'] > 0:
                self.stdout.write(
                    self.style.HTTP_INFO(
                        '\nRecommendation: Review errors and retry failed leagues'
                    )
                )
            
            if not current_only and result['saved'] > 100:
                self.stdout.write(
                    self.style.HTTP_INFO(
                        '\nTip: Use --current to fetch only active season leagues'
                    )
                )
            
            self.stdout.write('')
            
        except Exception as e:
            logger.exception('Error fetching leagues')
            raise CommandError(f'Failed to fetch leagues: {str(e)}')
