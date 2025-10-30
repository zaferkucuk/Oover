"""
URL Configuration for Core App

This module defines URL patterns for the core app,
including routes for Country, League, and Team API endpoints.

Author: Oover Development Team
Date: October 2025
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core.views import CountryViewSet, LeagueViewSet, TeamViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'teams', TeamViewSet, basename='team')

# App name for namespacing
app_name = 'core'

# URL patterns
urlpatterns = [
    # Router URLs (includes all CRUD endpoints automatically)
    path('', include(router.urls)),
]

"""
===================================
AVAILABLE ENDPOINTS DOCUMENTATION
===================================

COUNTRY ENDPOINTS
-----------------
Standard CRUD:
- GET    /api/countries/                  - List all countries (paginated)
- POST   /api/countries/                  - Create new country
- GET    /api/countries/{id}/             - Get country details
- PUT    /api/countries/{id}/             - Update country (all fields)
- PATCH  /api/countries/{id}/             - Partial update country
- DELETE /api/countries/{id}/             - Delete country

Custom Actions:
- GET    /api/countries/active/           - List only active countries
- GET    /api/countries/stats/            - Get country statistics
- GET    /api/countries/{id}/with_relations/ - Get country with leagues and teams


LEAGUE ENDPOINTS
----------------
Standard CRUD:
- GET    /api/leagues/                    - List all leagues (paginated)
- POST   /api/leagues/                    - Create new league
- GET    /api/leagues/{id}/               - Get league details
- PUT    /api/leagues/{id}/               - Update league (all fields)
- PATCH  /api/leagues/{id}/               - Partial update league
- DELETE /api/leagues/{id}/               - Delete league

Custom Actions:
- GET    /api/leagues/active/             - List only active leagues
- GET    /api/leagues/by-country/{country_id}/ - Get leagues by country
- GET    /api/leagues/search/?q=premier   - Advanced search


TEAM ENDPOINTS
--------------
Standard CRUD:
- GET    /api/teams/                      - List all teams (paginated)
- POST   /api/teams/                      - Create new team
- GET    /api/teams/{id}/                 - Get team details
- PUT    /api/teams/{id}/                 - Update team (all fields)
- PATCH  /api/teams/{id}/                 - Partial update team
- DELETE /api/teams/{id}/                 - Delete team

Custom Actions:
- GET    /api/teams/active/               - List only active teams
- GET    /api/teams/by-country/{country_id}/ - Get teams by country
- GET    /api/teams/top-by-market-value/?limit=10 - Top teams by market value
- GET    /api/teams/search/?q=united      - Advanced search

External API Operations:
- POST   /api/teams/fetch/                - Fetch teams from external API
- POST   /api/teams/sync/                 - Sync existing teams with external API data
- GET    /api/teams/operations/           - List team API sync operations history


===================================
QUERY PARAMETERS
===================================

Standard Listing Parameters:
- ?is_active=true/false                   - Filter by active status
- ?country=<uuid>                         - Filter by country ID
- ?sport=<id>                             - Filter by sport ID (leagues only)
- ?market_value_min=1000000               - Filter by minimum market value (teams only)
- ?market_value_max=1000000000            - Filter by maximum market value (teams only)
- ?search=keyword                         - Search in name, code, or external_id
- ?ordering=name,-created_at              - Order by field (- for descending)
- ?page=1&page_size=20                    - Pagination (default varies by endpoint)

Operations Listing Parameters:
- ?status=<status>                        - Filter by operation status
                                           (pending, in_progress, completed, failed)
- ?provider=<provider>                    - Filter by API provider
                                           (football_data_org, api_football)
- ?days=<N>                               - Show operations from last N days
                                           (default: 7, min: 1, max: 90)
- ?page=1&page_size=20                    - Pagination (default: 20 per page, max: 50)


===================================
EXTERNAL API OPERATIONS DETAILS
===================================

1. FETCH TEAMS
--------------
POST /api/teams/fetch/

Fetches teams from external APIs and creates/updates them in the database.

Providers:
- football-data: Football-Data.org API (10 requests/minute, more reliable)
- api-football: API-Football (100 requests/day, broader coverage)

Request Body:
{
    "provider": "football-data",        // Required: "football-data" or "api-football"
    
    // Filter options (mutually exclusive - use only ONE):
    "leagues": ["PL", "SA"],           // Array of league codes
    "country": "GB",                    // Country code (ISO 3166-1 alpha-2)
    "all_european": true,               // Top 5 European leagues (PL, PD, SA, BL1, FL1)
    
    "limit": 20                         // Optional: Limit results for testing
}

Response (Success):
{
    "success": true,
    "message": "Successfully fetched 20 teams from football-data",
    "stats": {
        "fetched": 20,
        "created": 15,
        "updated": 5,
        "failed": 0
    },
    "provider": "football-data",
    "filters": {
        "leagues": ["PL", "SA"]
    }
}

Response (Error):
{
    "error": "Only one of 'leagues', 'country', or 'all_european' can be specified",
    "details": "Multiple filter options provided"
}

Examples:
# Fetch all teams from Premier League and Serie A
POST /api/teams/fetch/
{
    "provider": "football-data",
    "leagues": ["PL", "SA"]
}

# Fetch all teams from England
POST /api/teams/fetch/
{
    "provider": "api-football",
    "country": "GB"
}

# Fetch top European teams
POST /api/teams/fetch/
{
    "provider": "football-data",
    "all_european": true
}

# Fetch limited teams for testing
POST /api/teams/fetch/
{
    "provider": "api-football",
    "leagues": ["PL"],
    "limit": 10
}


2. SYNC TEAMS
-------------
POST /api/teams/sync/

Updates existing teams with latest data from external API.
Only syncs teams that already exist in the database.

Request Body:
{
    "fields": ["market_value", "logo"],   // Optional: Specific fields to update
                                          // Available: name, logo, founded, website,
                                          //            market_value, stadium_capacity
    "force": false,                       // Optional: Force update even if recently updated
    "deactivate_missing": false           // Optional: Deactivate teams not found in API
}

Response (Success):
{
    "success": true,
    "message": "Successfully synced 150 teams",
    "stats": {
        "updated": 145,
        "failed": 5,
        "deactivated": 0
    },
    "fields": ["market_value", "logo"],
    "options": {
        "force": false,
        "deactivate_missing": false
    }
}

Response (Error):
{
    "error": "Invalid fields specified",
    "details": "Available fields: name, logo, founded, website, market_value, stadium_capacity"
}

Examples:
# Update market values and logos
POST /api/teams/sync/
{
    "fields": ["market_value", "logo"],
    "force": false
}

# Force full sync of all fields
POST /api/teams/sync/
{
    "force": true
}

# Sync and deactivate missing teams
POST /api/teams/sync/
{
    "deactivate_missing": true
}


3. OPERATIONS HISTORY
---------------------
GET /api/teams/operations/

Lists recent API sync operations with filtering and pagination.

Query Parameters:
- status: pending | in_progress | completed | failed
- provider: football_data_org | api_football
- days: 1-90 (default: 7)
- page: Page number
- page_size: Items per page (max: 50, default: 20)

Response:
{
    "count": 42,
    "next": "http://localhost:8000/api/teams/operations/?page=2",
    "previous": null,
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "provider": "football_data_org",
            "resource_type": "teams",
            "status": "completed",
            "started_at": "2025-10-30T15:30:00Z",
            "completed_at": "2025-10-30T15:32:15Z",
            "duration_seconds": 135,
            "stats": {
                "records_processed": 20,
                "records_created": 15,
                "records_updated": 5,
                "records_failed": 0
            }
        },
        // ... more operations
    ]
}

Examples:
# Get all operations
GET /api/teams/operations/

# Get failed operations from last 30 days
GET /api/teams/operations/?status=failed&days=30

# Get operations from Football-Data.org
GET /api/teams/operations/?provider=football_data_org

# Get recent completed operations with pagination
GET /api/teams/operations/?status=completed&days=7&page=1&page_size=10


===================================
USAGE EXAMPLES
===================================

LEAGUES:
--------
# List active leagues, ordered by name
GET /api/leagues/?is_active=true&ordering=name

# Search for "premier" in league names
GET /api/leagues/?search=premier&country=<uuid>

# Get league details
GET /api/leagues/{id}/

# Get active leagues only
GET /api/leagues/active/

# Get leagues by country
GET /api/leagues/by-country/{country_uuid}/

# Advanced search
GET /api/leagues/search/?q=premier


TEAMS:
------
# List active teams, ordered by market value (descending)
GET /api/teams/?is_active=true&ordering=-market_value

# Search for "manchester" in team names
GET /api/teams/?search=manchester&country=<uuid>

# Get team details
GET /api/teams/{id}/

# Get active teams only
GET /api/teams/active/

# Get teams by country
GET /api/teams/by-country/{country_uuid}/

# Get top teams by market value
GET /api/teams/top-by-market-value/?limit=10&country=<uuid>

# Advanced search
GET /api/teams/search/?q=united

# Filter by market value range
GET /api/teams/?market_value_min=100000000&market_value_max=1000000000


===================================
API RATE LIMITS & NOTES
===================================

Football-Data.org:
- Free Tier: 10 requests per minute
- More reliable data for European leagues
- Recommended for regular syncs
- Better for current season data

API-Football:
- Free Tier: 100 requests per day
- Broader coverage (worldwide)
- Use as fallback or for non-European leagues
- Better for historical data

Operation Status:
- pending: Operation queued but not started
- in_progress: Operation currently running
- completed: Operation finished successfully
- failed: Operation encountered errors

Best Practices:
1. Use fetch for initial data population
2. Use sync for regular updates (daily/weekly)
3. Monitor operations endpoint for failures
4. Use specific filters to avoid rate limits
5. Test with 'limit' parameter first
6. Check operations history before re-running


===================================
ERROR RESPONSES
===================================

400 Bad Request:
{
    "error": "Validation error message",
    "details": "Additional error details"
}

500 Internal Server Error:
{
    "error": "Operation failed",
    "message": "Detailed error message for debugging"
}

429 Too Many Requests:
{
    "error": "Rate limit exceeded",
    "message": "Please wait before making another request"
}
"""
