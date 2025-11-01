"""
Fetch Countries Management Command

This command fetches country data from API-Football and stores them in the database.
This is a one-time fetch operation for initial data load.

Usage Examples:
    # Fetch all countries from API-Football
    python manage.py fetch_countries
    
    # Fetch with limit (useful for testing)
    python manage.py fetch_countries --limit 50
    
    # Dry run to see what would be fetched without saving
    python manage.py fetch_countries --dry-run
    
    # Verbose output with detailed information
    python manage.py fetch_countries --verbose
    
    # Combine options
    python manage.py fetch_countries --limit 20 --verbose --dry-run

Features:
    - One-time fetch operation for initial data load
    - Fetches all countries with flags and ISO codes from API-Football
    - Progress reporting with detailed statistics
    - Dry-run mode for testing without database changes
    - Verbose mode for detailed operation logging
    - Comprehensive error handling with transaction rollback
    - Duplicate detection via external_id

Expected Results:
    - ~200 countries fetched from API-Football
    - Each country includes: name, code (ISO 3166-1 alpha-2), flag URL
    - Automatic duplicate handling via external_id (api-football-{CODE})
    - Transaction-safe operations with automatic rollback on errors

Author: Oover Development Team
Created: 2025-11-01
"""

from typing import Dict, Any
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...services.countries_service import CountriesService


class Command(BaseCommand):
    """
    Management command to fetch countries from API-Football.
    
    This command provides one-time fetch functionality for loading
    country data into the database. It uses the CountriesService
    to handle the complete fetch → transform → validate → save pipeline.
    """
    
    help = (
        'Fetch countries from API-Football. '
        'Use for initial data load or to refresh country data.'
    )
    
    def add_arguments(self, parser) -> None:
        """
        Add command line arguments.
        
        Args:
            parser: Django management command argument parser
        """
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of countries to fetch (useful for testing). '
                 'Example: --limit 50'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to database. '
                 'Shows what would be fetched and transformed.'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with detailed operation information'
        )
    
    def handle(self, *args, **options) -> None:
        """
        Main command handler.
        
        Args:
            *args: Positional arguments
            **options: Command options dictionary
        """
        try:
            # Validate options
            self._validate_options(options)
            
            # Extract options
            limit = options.get('limit')
            dry_run = options.get('dry_run', False)
            verbose = options.get('verbose', False)
            
            # Display operation header
            self._display_header(limit, dry_run, verbose)
            
            # Initialize service
            if verbose:
                self.stdout.write('📦 Initializing CountriesService...')
            
            service = CountriesService()
            
            # Execute fetch operation
            if verbose:
                self.stdout.write('🌍 Fetching countries from API-Football...\n')
            
            try:
                with transaction.atomic():
                    # Call service method to fetch countries from API
                    stats = service.fetch_countries_from_api(
                        limit=limit,
                        verbose=verbose
                    )
                    
                    # If dry-run, rollback the transaction
                    if dry_run:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(
                                    '\n🔄 Dry-run mode: Rolling back transaction...'
                                )
                            )
                        transaction.set_rollback(True)
                    
            except Exception as e:
                # Log error and re-raise
                self.stderr.write(
                    self.style.ERROR(
                        f'\n❌ Error during fetch operation: {str(e)}'
                    )
                )
                if verbose:
                    import traceback
                    self.stderr.write(traceback.format_exc())
                raise CommandError(f'Fetch operation failed: {str(e)}')
            
            # Display results
            self._display_results(stats, dry_run, verbose)
            
        except CommandError:
            # Re-raise CommandError as-is
            raise
        
        except Exception as e:
            # Convert unexpected errors to CommandError
            self.stderr.write(
                self.style.ERROR(f'\n❌ Unexpected error: {str(e)}')
            )
            raise CommandError(f'Command execution failed: {str(e)}')
    
    def _validate_options(self, options: Dict[str, Any]) -> None:
        """
        Validate command options.
        
        Args:
            options: Dictionary of command options
            
        Raises:
            CommandError: If options are invalid
        """
        # Validate limit if provided
        limit = options.get('limit')
        if limit is not None and limit <= 0:
            raise CommandError('--limit must be a positive integer')
    
    def _display_header(
        self,
        limit: int = None,
        dry_run: bool = False,
        verbose: bool = False
    ) -> None:
        """
        Display operation header with configuration.
        
        Args:
            limit: Optional limit on number of countries
            dry_run: Whether this is a dry-run operation
            verbose: Whether verbose output is enabled
        """
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                '\n' + '='*70
            )
        )
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                '  🌍 FETCH COUNTRIES FROM API-FOOTBALL'
            )
        )
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                '='*70
            )
        )
        
        # Display configuration
        self.stdout.write('\n📋 Configuration:')
        self.stdout.write(f'   • Source: API-Football')
        self.stdout.write(f'   • Expected: ~200 countries')
        
        if limit:
            self.stdout.write(f'   • Limit: {limit} countries')
        else:
            self.stdout.write(f'   • Limit: None (fetch all)')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '   • Mode: DRY-RUN (no database changes)'
                )
            )
        else:
            self.stdout.write('   • Mode: Live (will save to database)')
        
        if verbose:
            self.stdout.write('   • Verbosity: Detailed output enabled')
        
        self.stdout.write('')
    
    def _display_results(
        self,
        stats: Dict[str, Any],
        dry_run: bool = False,
        verbose: bool = False
    ) -> None:
        """
        Display operation results and statistics.
        
        Args:
            stats: Statistics dictionary from service
            dry_run: Whether this was a dry-run operation
            verbose: Whether verbose output is enabled
        """
        # Extract statistics
        fetched = stats.get('fetched', 0)
        transformed = stats.get('transformed', 0)
        validated = stats.get('validated', 0)
        saved = stats.get('saved', 0)
        created = stats.get('created', 0)
        updated = stats.get('updated', 0)
        failed = stats.get('failed', 0)
        errors = stats.get('errors', [])
        
        # Display separator
        self.stdout.write('\n' + '='*70)
        
        # Display summary header
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '📊 DRY-RUN RESULTS (No changes saved)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '📊 OPERATION RESULTS'
                )
            )
        
        self.stdout.write('='*70 + '\n')
        
        # Display pipeline statistics
        self.stdout.write('🔄 Pipeline Statistics:')
        self.stdout.write(f'   • Fetched from API: {fetched}')
        self.stdout.write(f'   • Transformed: {transformed}')
        self.stdout.write(f'   • Validated: {validated}')
        
        if not dry_run:
            self.stdout.write(f'   • Saved to database: {saved}')
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'   • Would be saved: {saved} (dry-run)'
                )
            )
        
        self.stdout.write('')
        
        # Display operation results
        self.stdout.write('✅ Operation Results:')
        
        if not dry_run:
            if created > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'   • New countries created: {created}'
                    )
                )
            
            if updated > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'   • Existing countries updated: {updated}'
                    )
                )
        else:
            if created > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'   • Would create: {created} (dry-run)'
                    )
                )
            
            if updated > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'   • Would update: {updated} (dry-run)'
                    )
                )
        
        if failed > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'   • Failed: {failed}'
                )
            )
        
        self.stdout.write('')
        
        # Display errors if any
        if errors:
            self.stdout.write(
                self.style.ERROR(
                    f'⚠️  Errors encountered ({len(errors)}):'
                )
            )
            for idx, error in enumerate(errors[:10], 1):  # Show first 10 errors
                self.stdout.write(f'   {idx}. {error}')
            
            if len(errors) > 10:
                self.stdout.write(
                    f'   ... and {len(errors) - 10} more errors'
                )
            
            self.stdout.write('')
        
        # Display final status
        if failed == 0 and not errors:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        '✅ Dry-run completed successfully! '
                        'Run without --dry-run to save changes.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '✅ All countries fetched and saved successfully!'
                    )
                )
        elif failed > 0 or errors:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Operation completed with {failed} failures. '
                    'Check errors above.'
                )
            )
        
        # Display verbose details if enabled
        if verbose and 'details' in stats:
            self.stdout.write('\n📝 Detailed Information:')
            for key, value in stats['details'].items():
                self.stdout.write(f'   • {key}: {value}')
        
        self.stdout.write('\n' + '='*70 + '\n')
