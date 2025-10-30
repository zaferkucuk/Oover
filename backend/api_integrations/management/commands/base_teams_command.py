"""
Base Teams Command

Abstract base class for all teams-related management commands.
Provides common functionality for:
- Provider validation and selection
- Error handling and logging
- Success/failure reporting
- Dry-run mode support

Usage:
    from api_integrations.management.commands.base_teams_command import BaseTeamsCommand
    
    class Command(BaseTeamsCommand):
        help = 'My teams command'
        
        def execute_teams_operation(self, *args, **options):
            # Implement your command logic here
            pass
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from api_integrations.providers import VALID_PROVIDERS

logger = logging.getLogger(__name__)


class BaseTeamsCommand(BaseCommand, ABC):
    """
    Abstract base class for teams-related management commands.
    
    This class provides common functionality for all teams commands:
    - Provider validation and selection
    - Error handling and logging
    - Statistics collection and reporting
    - Dry-run mode support
    
    Subclasses must implement:
    - execute_teams_operation(): Core command logic
    
    Example:
        class Command(BaseTeamsCommand):
            help = 'Fetch teams from API'
            
            def add_custom_arguments(self, parser):
                parser.add_argument('--league', type=str, help='League code')
            
            def execute_teams_operation(self, *args, **options):
                league = options.get('league')
                provider = self.get_provider(options)
                # ... implement command logic
                return {'created': 10, 'updated': 5, 'failed': 0}
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize base command with statistics tracking."""
        super().__init__(*args, **kwargs)
        self.start_time = None
        self.end_time = None
        self.stats = {
            'fetched': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'deactivated': 0,
            'errors': []
        }
    
    def add_arguments(self, parser):
        """
        Add common command arguments.
        
        Subclasses can override add_custom_arguments() to add their own arguments.
        
        Args:
            parser: Django ArgumentParser instance
        """
        # Provider selection
        parser.add_argument(
            '--provider',
            type=str,
            choices=VALID_PROVIDERS,
            help=f'API provider to use. Valid options: {", ".join(VALID_PROVIDERS)}'
        )
        
        # Dry-run mode
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to database'
        )
        
        # Verbosity
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        
        # Allow subclasses to add custom arguments
        self.add_custom_arguments(parser)
    
    def add_custom_arguments(self, parser):
        """
        Add custom command arguments for subclasses.
        
        Override this method in subclasses to add command-specific arguments.
        
        Args:
            parser: Django ArgumentParser instance
        
        Example:
            def add_custom_arguments(self, parser):
                parser.add_argument('--league', type=str, help='League code')
        """
        pass
    
    def handle(self, *args, **options):
        """
        Main command handler.
        
        This method orchestrates the command execution:
        1. Setup (logging, validation)
        2. Execute operation (calls execute_teams_operation)
        3. Report results (statistics, errors)
        
        Args:
            *args: Positional arguments
            **options: Command options from parser
        
        Returns:
            None
        """
        self.start_time = timezone.now()
        
        try:
            # Setup
            self.setup_logging(options)
            self.validate_options(options)
            
            # Display header
            self.print_header(options)
            
            # Execute command-specific operation
            result = self.execute_teams_operation(*args, **options)
            
            # Update statistics from result
            if result:
                self.update_stats(result)
            
            # Report success
            self.end_time = timezone.now()
            self.report_success()
            
        except Exception as e:
            # Handle errors
            self.end_time = timezone.now()
            self.handle_error(e)
    
    @abstractmethod
    def execute_teams_operation(self, *args, **options) -> Dict[str, Any]:
        """
        Execute the command-specific teams operation.
        
        This is the core method that subclasses must implement.
        
        Args:
            *args: Positional arguments
            **options: Command options
        
        Returns:
            Dictionary with operation results (created, updated, failed, etc.)
        
        Raises:
            NotImplementedError: If not implemented by subclass
        
        Example:
            def execute_teams_operation(self, *args, **options):
                provider = self.get_provider(options)
                # ... fetch and process teams
                return {
                    'fetched': 20,
                    'created': 10,
                    'updated': 5,
                    'failed': 5,
                    'errors': ['Error 1', 'Error 2']
                }
        """
        raise NotImplementedError("Subclasses must implement execute_teams_operation()")
    
    def setup_logging(self, options: Dict[str, Any]) -> None:
        """
        Setup logging based on command options.
        
        Args:
            options: Command options
        """
        if options.get('verbose'):
            logger.setLevel(logging.DEBUG)
            self.stdout.write(self.style.SUCCESS('✓ Verbose logging enabled'))
    
    def validate_options(self, options: Dict[str, Any]) -> None:
        """
        Validate command options.
        
        Args:
            options: Command options
        
        Raises:
            ValueError: If options are invalid
        """
        # Validate provider
        provider = options.get('provider')
        if provider and provider not in VALID_PROVIDERS:
            raise ValueError(
                f"Invalid provider: {provider}. "
                f"Valid options: {', '.join(VALID_PROVIDERS)}"
            )
    
    def get_provider(self, options: Dict[str, Any]) -> Optional[str]:
        """
        Get provider from options or return default (Football-Data).
        
        Args:
            options: Command options
        
        Returns:
            Provider name or None (will use default)
        
        Example:
            provider = self.get_provider(options)
            if provider:
                self.stdout.write(f"Using provider: {provider}")
        """
        provider = options.get('provider')
        if provider:
            logger.info(f"Using specified provider: {provider}")
        else:
            logger.info("Using default provider (Football-Data.org)")
        return provider
    
    def is_dry_run(self, options: Dict[str, Any]) -> bool:
        """
        Check if dry-run mode is enabled.
        
        Args:
            options: Command options
        
        Returns:
            True if dry-run mode is enabled
        """
        return options.get('dry_run', False)
    
    def print_header(self, options: Dict[str, Any]) -> None:
        """
        Print command header with basic info.
        
        Args:
            options: Command options
        """
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n{"="*60}'))
        self.stdout.write(self.style.MIGRATE_HEADING(f'{self.help}'))
        self.stdout.write(self.style.MIGRATE_HEADING(f'{"="*60}\n'))
        
        # Display mode
        if self.is_dry_run(options):
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN MODE - No changes will be saved'))
        
        # Display provider
        provider = self.get_provider(options)
        if provider:
            self.stdout.write(f'📡 Provider: {provider}')
        
        self.stdout.write('')
    
    def update_stats(self, result: Dict[str, Any]) -> None:
        """
        Update statistics from operation result.
        
        Args:
            result: Operation result dictionary
        """
        for key in ['fetched', 'created', 'updated', 'failed', 'deactivated']:
            if key in result:
                self.stats[key] += result[key]
        
        if 'errors' in result and result['errors']:
            self.stats['errors'].extend(result['errors'])
    
    def report_success(self) -> None:
        """
        Report command success with detailed statistics.
        
        Displays:
        - Execution time
        - Statistics (fetched, created, updated, failed)
        - Error messages (if any)
        """
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('✅ COMMAND COMPLETED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # Display statistics
        self.stdout.write(f'\n📊 Statistics:')
        self.stdout.write(f'   • Fetched: {self.stats["fetched"]}')
        self.stdout.write(f'   • Created: {self.stats["created"]}')
        self.stdout.write(f'   • Updated: {self.stats["updated"]}')
        if self.stats['deactivated'] > 0:
            self.stdout.write(f'   • Deactivated: {self.stats["deactivated"]}')
        if self.stats['failed'] > 0:
            self.stdout.write(
                self.style.ERROR(f'   • Failed: {self.stats["failed"]}')
            )
        
        # Display execution time
        self.stdout.write(f'\n⏱️  Execution time: {duration:.2f} seconds')
        
        # Display errors (if any)
        if self.stats['errors']:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('❌ ERRORS:'))
            for i, error in enumerate(self.stats['errors'][:10], 1):
                self.stdout.write(self.style.ERROR(f'   {i}. {error}'))
            
            if len(self.stats['errors']) > 10:
                remaining = len(self.stats['errors']) - 10
                self.stdout.write(
                    self.style.ERROR(f'   ... and {remaining} more errors')
                )
        
        self.stdout.write('')
    
    def handle_error(self, error: Exception) -> None:
        """
        Handle and report command errors.
        
        Args:
            error: The exception that occurred
        """
        duration = (self.end_time - self.start_time).total_seconds()
        
        logger.error(f"Command failed: {str(error)}", exc_info=True)
        
        self.stdout.write('')
        self.stdout.write(self.style.ERROR('='*60))
        self.stdout.write(self.style.ERROR('❌ COMMAND FAILED'))
        self.stdout.write(self.style.ERROR('='*60))
        
        # Display error
        self.stdout.write(f'\n💥 Error: {str(error)}')
        
        # Display partial statistics
        if any(self.stats.values()):
            self.stdout.write(f'\n📊 Partial Statistics (before failure):')
            self.stdout.write(f'   • Fetched: {self.stats["fetched"]}')
            self.stdout.write(f'   • Created: {self.stats["created"]}')
            self.stdout.write(f'   • Updated: {self.stats["updated"]}')
            if self.stats['failed'] > 0:
                self.stdout.write(f'   • Failed: {self.stats["failed"]}')
        
        # Display execution time
        self.stdout.write(f'\n⏱️  Execution time: {duration:.2f} seconds')
        
        self.stdout.write('')
        
        # Re-raise for Django to handle
        raise error
