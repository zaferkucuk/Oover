"""
Django management command to synchronize teams from external APIs.

This command performs periodic synchronization of team data by:
- Updating existing teams with latest information from API
- Creating new teams that don't exist in the database
- Optionally deactivating teams that are no longer in the API response
- Allowing selective field updates for efficiency

Usage Examples:
    # Sync all European leagues (default)
    python manage.py sync_teams

    # Sync specific league
    python manage.py sync_teams --league PL

    # Sync with deactivation of missing teams
    python manage.py sync_teams --deactivate-missing

    # Sync only specific fields
    python manage.py sync_teams --fields name,short_name,logo_url

    # Force update even if data unchanged
    python manage.py sync_teams --force

    # Sync with specific provider
    python manage.py sync_teams --provider api-football

    # Dry run to see what would be synced
    python manage.py sync_teams --dry-run

    # Combine options
    python manage.py sync_teams --league SA --deactivate-missing --force
"""

from typing import Dict, Any, Optional, List

from .base_teams_command import BaseTeamsCommand


class Command(BaseTeamsCommand):
    """
    Management command for synchronizing teams from external APIs.
    
    This command extends BaseTeamsCommand and implements periodic sync
    functionality for keeping team data up-to-date with external sources.
    
    Features:
    - Update existing teams with latest data
    - Create new teams found in API
    - Optionally deactivate teams not in API
    - Selective field updates for efficiency
    - Force update option
    - Dry-run mode for testing
    """
    
    help = 'Synchronize teams from external APIs (periodic updates)'
    operation_name = 'sync'
    
    def add_arguments(self, parser) -> None:
        """
        Add command-specific arguments.
        
        Inherits base arguments from BaseTeamsCommand and adds sync-specific options.
        
        Args:
            parser: ArgumentParser instance
        """
        # Add base arguments (provider, dry-run, etc.)
        super().add_arguments(parser)
        
        # Add sync-specific arguments
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            help='Deactivate teams not found in API response',
        )
        
        parser.add_argument(
            '--fields',
            type=str,
            help='Comma-separated list of fields to update (e.g., name,logo_url)',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data has not changed',
        )
        
        # Filter options group (same as fetch_teams)
        filter_group = parser.add_mutually_exclusive_group()
        
        filter_group.add_argument(
            '--league',
            action='append',
            help='League code to sync (can be used multiple times)',
        )
        
        filter_group.add_argument(
            '--country',
            type=str,
            help='Country code to sync teams for',
        )
        
        filter_group.add_argument(
            '--all-european',
            action='store_true',
            help='Sync top 5 European leagues (PL, PD, SA, BL1, FL1)',
        )
        
        # Optional limit for testing
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of teams to sync (for testing)',
        )
    
    def execute_teams_operation(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the sync teams operation.
        
        This method is called by the base class handle() method after
        setup and validation are complete.
        
        Args:
            options: Command options dictionary containing:
                - provider: API provider name
                - deactivate_missing: Whether to deactivate missing teams
                - fields: Optional list of fields to update
                - force: Whether to force update
                - league: Optional league codes list
                - country: Optional country code
                - all_european: Whether to sync European leagues
                - limit: Optional limit on teams
        
        Returns:
            dict: Operation statistics with keys:
                - fetched: Number of teams fetched from API
                - created: Number of new teams created
                - updated: Number of teams updated
                - failed: Number of failed operations
                - deactivated: Number of teams deactivated
                - skipped: Number of teams skipped (no changes)
        
        Raises:
            ValueError: If invalid filter options provided
            Exception: If sync operation fails
        """
        try:
            # Extract sync-specific options
            deactivate_missing = options.get('deactivate_missing', False)
            fields_str = options.get('fields')
            force_update = options.get('force', False)
            
            # Parse fields if provided
            fields_to_update = None
            if fields_str:
                fields_to_update = [f.strip() for f in fields_str.split(',')]
                self.stdout.write(
                    self.style.SUCCESS(f'Updating only fields: {", ".join(fields_to_update)}')
                )
            
            # Extract filter options
            leagues = options.get('league') or []
            country = options.get('country')
            all_european = options.get('all_european', False)
            limit = options.get('limit')
            
            # Build filters dictionary
            filters = {}
            
            if all_european:
                self.stdout.write(
                    self.style.SUCCESS('Syncing top 5 European leagues (PL, PD, SA, BL1, FL1)')
                )
                filters['leagues'] = ['PL', 'PD', 'SA', 'BL1', 'FL1']
            elif leagues:
                self.stdout.write(
                    self.style.SUCCESS(f'Syncing leagues: {", ".join(leagues)}')
                )
                filters['leagues'] = leagues
            elif country:
                self.stdout.write(
                    self.style.SUCCESS(f'Syncing teams for country: {country}')
                )
                filters['country'] = country
            else:
                # Default: all European leagues
                self.stdout.write(
                    self.style.SUCCESS('Syncing all European leagues (default)')
                )
                filters['leagues'] = ['PL', 'PD', 'SA', 'BL1', 'FL1']
            
            if limit:
                self.stdout.write(
                    self.style.WARNING(f'Limiting to {limit} teams (testing mode)')
                )
                filters['limit'] = limit
            
            # Display sync options
            if deactivate_missing:
                self.stdout.write(
                    self.style.WARNING('Deactivate missing teams: ENABLED')
                )
            if force_update:
                self.stdout.write(
                    self.style.WARNING('Force update: ENABLED')
                )
            
            # Execute sync operation
            self.stdout.write(self.style.SUCCESS('Starting sync operation...'))
            
            stats = self.teams_service.sync_teams(
                filters=filters,
                deactivate_missing=deactivate_missing,
                fields_to_update=fields_to_update,
                force_update=force_update
            )
            
            return stats
            
        except ValueError as e:
            raise ValueError(f'Invalid sync options: {str(e)}')
        except Exception as e:
            raise Exception(f'Sync operation failed: {str(e)}')
    
    def get_success_message(self, stats: Dict[str, Any], options: Dict[str, Any]) -> str:
        """
        Generate a custom success message for sync operation.
        
        Args:
            stats: Operation statistics dictionary
            options: Command options
        
        Returns:
            str: Formatted success message with operation details
        """
        # Get filter info
        leagues = options.get('league') or []
        country = options.get('country')
        all_european = options.get('all_european', False)
        deactivate_missing = options.get('deactivate_missing', False)
        fields_str = options.get('fields')
        force_update = options.get('force', False)
        
        # Build filter description
        if all_european:
            filter_desc = 'top 5 European leagues'
        elif leagues:
            filter_desc = f'leagues: {", ".join(leagues)}'
        elif country:
            filter_desc = f'country: {country}'
        else:
            filter_desc = 'all European leagues'
        
        # Build options description
        options_parts = []
        if deactivate_missing:
            options_parts.append('with deactivation')
        if fields_str:
            options_parts.append(f'fields: {fields_str}')
        if force_update:
            options_parts.append('forced update')
        
        options_desc = f" ({', '.join(options_parts)})" if options_parts else ""
        
        message = (
            f"Successfully synced teams for {filter_desc}{options_desc}\n"
            f"  • Fetched: {stats['fetched']}\n"
            f"  • Created: {stats['created']}\n"
            f"  • Updated: {stats['updated']}\n"
            f"  • Skipped: {stats.get('skipped', 0)} (no changes)\n"
            f"  • Failed: {stats['failed']}"
        )
        
        if deactivate_missing:
            message += f"\n  • Deactivated: {stats.get('deactivated', 0)}"
        
        return message
