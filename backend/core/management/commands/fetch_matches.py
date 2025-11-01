"""
Management command to fetch match fixtures from API-Football.

This command provides various strategies for fetching match data:
- Today's fixtures across all leagues
- Upcoming fixtures for next N days
- Fixtures for specific league/season
- Fixtures for specific team
- Live matches
- Fixtures for specific date or date range

Usage Examples:
    # Fetch today's fixtures
    python manage.py fetch_matches --today

    # Fetch upcoming fixtures for next 7 days
    python manage.py fetch_matches --upcoming --days 7

    # Fetch fixtures for specific league
    python manage.py fetch_matches --league-id 39 --season 2025

    # Fetch fixtures for specific team
    python manage.py fetch_matches --team-id 33 --season 2025

    # Fetch live matches
    python manage.py fetch_matches --live

    # Fetch fixtures for specific date
    python manage.py fetch_matches --date 2025-11-15

    # Fetch fixtures for date range
    python manage.py fetch_matches --from 2025-11-01 --to 2025-11-07

    # Verbose output
    python manage.py fetch_matches --today --verbose
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from core.services import MatchesService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to fetch match fixtures from API-Football."""

    help = "Fetch match fixtures from API-Football"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Strategy options (mutually exclusive)
        strategy_group = parser.add_mutually_exclusive_group(required=True)
        strategy_group.add_argument(
            "--today",
            action="store_true",
            help="Fetch today's fixtures across all leagues",
        )
        strategy_group.add_argument(
            "--upcoming",
            action="store_true",
            help="Fetch upcoming fixtures (use with --days)",
        )
        strategy_group.add_argument(
            "--live",
            action="store_true",
            help="Fetch currently live matches",
        )
        strategy_group.add_argument(
            "--date",
            type=str,
            help="Fetch fixtures for specific date (YYYY-MM-DD)",
        )
        strategy_group.add_argument(
            "--league-id",
            type=int,
            help="Fetch fixtures for specific league (requires --season)",
        )
        strategy_group.add_argument(
            "--team-id",
            type=int,
            help="Fetch fixtures for specific team (optional --season)",
        )

        # Supporting options
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days for upcoming fixtures (default: 7, use with --upcoming)",
        )
        parser.add_argument(
            "--season",
            type=int,
            help="Season year (required with --league-id, optional with --team-id)",
        )
        parser.add_argument(
            "--from",
            dest="date_from",
            type=str,
            help="Start date for date range (YYYY-MM-DD)",
        )
        parser.add_argument(
            "--to",
            dest="date_to",
            type=str,
            help="End date for date range (YYYY-MM-DD)",
        )
        parser.add_argument(
            "--status",
            type=str,
            help="Filter by match status (e.g., NS, LIVE, FT)",
        )
        parser.add_argument(
            "--timezone",
            type=str,
            default="UTC",
            help="Timezone for date filtering (default: UTC)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set verbosity level
        if options["verbose"]:
            self.stdout.write(self.style.SUCCESS("🔍 Verbose mode enabled"))
            logger.setLevel(logging.DEBUG)

        # Initialize service
        service = MatchesService()

        try:
            # Determine strategy and fetch matches
            if options["today"]:
                matches = self._fetch_today(service, options)
            elif options["upcoming"]:
                matches = self._fetch_upcoming(service, options)
            elif options["live"]:
                matches = self._fetch_live(service, options)
            elif options["date"]:
                matches = self._fetch_by_date(service, options)
            elif options["league_id"]:
                matches = self._fetch_by_league(service, options)
            elif options["team_id"]:
                matches = self._fetch_by_team(service, options)
            elif options["date_from"] and options["date_to"]:
                matches = self._fetch_date_range(service, options)
            else:
                raise CommandError(
                    "Invalid strategy. Use --help to see available options."
                )

            # Display results
            self._display_results(matches, options)

        except Exception as e:
            logger.error(f"Error fetching matches: {str(e)}", exc_info=True)
            raise CommandError(f"Failed to fetch matches: {str(e)}")

    def _fetch_today(self, service: MatchesService, options: dict) -> dict:
        """Fetch today's fixtures."""
        today = timezone.now().date()
        self.stdout.write(f"📅 Fetching fixtures for today: {today}")

        result = service.fetch_fixtures_from_api(
            date=today.isoformat(),
            timezone=options["timezone"],
            status=options.get("status"),
        )

        if options["verbose"]:
            self.stdout.write(f"   API call completed")

        return result

    def _fetch_upcoming(self, service: MatchesService, options: dict) -> dict:
        """Fetch upcoming fixtures for next N days."""
        days = options["days"]
        today = timezone.now().date()
        end_date = today + timedelta(days=days)

        self.stdout.write(
            f"📅 Fetching upcoming fixtures: {today} to {end_date} ({days} days)"
        )

        result = service.fetch_fixtures_from_api(
            date_from=today.isoformat(),
            date_to=end_date.isoformat(),
            timezone=options["timezone"],
            status=options.get("status") or "NS",  # Default to not started
        )

        if options["verbose"]:
            self.stdout.write(f"   Date range: {today} → {end_date}")

        return result

    def _fetch_live(self, service: MatchesService, options: dict) -> dict:
        """Fetch currently live matches."""
        self.stdout.write("🔴 Fetching live matches...")

        result = service.fetch_fixtures_from_api(
            live="all",  # Fetch all live matches
            timezone=options["timezone"],
        )

        if options["verbose"]:
            self.stdout.write(f"   Checking all leagues for live matches")

        return result

    def _fetch_by_date(self, service: MatchesService, options: dict) -> dict:
        """Fetch fixtures for specific date."""
        date_str = options["date"]

        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise CommandError(
                f"Invalid date format: {date_str}. Use YYYY-MM-DD format."
            )

        self.stdout.write(f"📅 Fetching fixtures for date: {date_str}")

        result = service.fetch_fixtures_from_api(
            date=date_str,
            timezone=options["timezone"],
            status=options.get("status"),
        )

        return result

    def _fetch_by_league(self, service: MatchesService, options: dict) -> dict:
        """Fetch fixtures for specific league."""
        league_id = options["league_id"]
        season = options.get("season")

        if not season:
            raise CommandError("--season is required when using --league-id")

        self.stdout.write(
            f"🏆 Fetching fixtures for league {league_id}, season {season}"
        )

        result = service.fetch_fixtures_from_api(
            league_id=league_id,
            season=season,
            timezone=options["timezone"],
            status=options.get("status"),
        )

        if options["verbose"]:
            self.stdout.write(f"   League: {league_id}")
            self.stdout.write(f"   Season: {season}")

        return result

    def _fetch_by_team(self, service: MatchesService, options: dict) -> dict:
        """Fetch fixtures for specific team."""
        team_id = options["team_id"]
        season = options.get("season")

        self.stdout.write(f"⚽ Fetching fixtures for team {team_id}")

        kwargs = {
            "team_id": team_id,
            "timezone": options["timezone"],
        }

        if season:
            kwargs["season"] = season
            if options["verbose"]:
                self.stdout.write(f"   Season: {season}")

        if options.get("status"):
            kwargs["status"] = options["status"]

        result = service.fetch_fixtures_from_api(**kwargs)

        return result

    def _fetch_date_range(self, service: MatchesService, options: dict) -> dict:
        """Fetch fixtures for date range."""
        date_from = options["date_from"]
        date_to = options["date_to"]

        # Validate date formats
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError as e:
            raise CommandError(f"Invalid date format: {str(e)}. Use YYYY-MM-DD.")

        self.stdout.write(f"📅 Fetching fixtures from {date_from} to {date_to}")

        result = service.fetch_fixtures_from_api(
            date_from=date_from,
            date_to=date_to,
            timezone=options["timezone"],
            status=options.get("status"),
        )

        return result

    def _display_results(self, result: dict, options: dict):
        """Display fetch results."""
        success = result.get("success", False)
        created = result.get("created", 0)
        updated = result.get("updated", 0)
        skipped = result.get("skipped", 0)
        total = result.get("total_fetched", 0)
        errors = result.get("errors", [])

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if success:
            self.stdout.write(self.style.SUCCESS("✅ FETCH COMPLETED SUCCESSFULLY"))
        else:
            self.stdout.write(self.style.ERROR("❌ FETCH COMPLETED WITH ERRORS"))

        self.stdout.write("=" * 60)

        # Statistics
        self.stdout.write(f"\n📊 STATISTICS:")
        self.stdout.write(f"   Total Fetched:  {total}")
        self.stdout.write(self.style.SUCCESS(f"   ✅ Created:    {created}"))
        self.stdout.write(self.style.WARNING(f"   🔄 Updated:    {updated}"))
        self.stdout.write(f"   ⏭️  Skipped:    {skipped}")

        # Breakdown by status (if available)
        status_breakdown = result.get("by_status", {})
        if status_breakdown and options["verbose"]:
            self.stdout.write(f"\n📈 BY STATUS:")
            for status, count in sorted(status_breakdown.items()):
                self.stdout.write(f"   {status}: {count}")

        # Errors
        if errors:
            self.stdout.write(self.style.ERROR(f"\n⚠️  ERRORS ({len(errors)}):"))
            for i, error in enumerate(errors[:10], 1):  # Show first 10 errors
                self.stdout.write(f"   {i}. {error}")
            if len(errors) > 10:
                self.stdout.write(f"   ... and {len(errors) - 10} more errors")

        # API usage (if available)
        api_info = result.get("api_info", {})
        if api_info and options["verbose"]:
            self.stdout.write(f"\n🌐 API USAGE:")
            self.stdout.write(f"   Requests Made: {api_info.get('requests_made', 0)}")
            self.stdout.write(
                f"   Rate Limit: {api_info.get('rate_limit_remaining', 'N/A')}"
            )

        # Validation errors (if any)
        validation_errors = result.get("validation_errors", [])
        if validation_errors and options["verbose"]:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  VALIDATION ISSUES ({len(validation_errors)}):"
                )
            )
            for error in validation_errors[:5]:  # Show first 5
                self.stdout.write(f"   • {error}")
            if len(validation_errors) > 5:
                self.stdout.write(f"   ... and {len(validation_errors) - 5} more")

        self.stdout.write("=" * 60 + "\n")

        # Tips for verbose mode
        if not options["verbose"] and (errors or validation_errors):
            self.stdout.write(
                self.style.NOTICE(
                    "💡 TIP: Use --verbose flag to see detailed error information"
                )
            )
