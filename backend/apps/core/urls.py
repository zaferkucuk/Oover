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
Available endpoints:

Country endpoints:
- GET    /api/countries/                  - List all countries (paginated)
- POST   /api/countries/                  - Create new country
- GET    /api/countries/{id}/             - Get country details
- PUT    /api/countries/{id}/             - Update country (all fields)
- PATCH  /api/countries/{id}/             - Partial update country
- DELETE /api/countries/{id}/             - Delete country

Country custom actions:
- GET    /api/countries/active/           - List only active countries
- GET    /api/countries/stats/            - Get country statistics
- GET    /api/countries/{id}/with_relations/ - Get country with leagues and teams

League endpoints:
- GET    /api/leagues/                    - List all leagues (paginated)
- POST   /api/leagues/                    - Create new league
- GET    /api/leagues/{id}/               - Get league details
- PUT    /api/leagues/{id}/               - Update league (all fields)
- PATCH  /api/leagues/{id}/               - Partial update league
- DELETE /api/leagues/{id}/               - Delete league

League custom actions:
- GET    /api/leagues/active/             - List only active leagues
- GET    /api/leagues/by-country/{country_id}/ - Get leagues by country
- GET    /api/leagues/search/?q=premier   - Advanced search

Team endpoints:
- GET    /api/teams/                      - List all teams (paginated)
- POST   /api/teams/                      - Create new team
- GET    /api/teams/{id}/                 - Get team details
- PUT    /api/teams/{id}/                 - Update team (all fields)
- PATCH  /api/teams/{id}/                 - Partial update team
- DELETE /api/teams/{id}/                 - Delete team

Team custom actions:
- GET    /api/teams/active/               - List only active teams
- GET    /api/teams/by-country/{country_id}/ - Get teams by country
- GET    /api/teams/top-by-market-value/?limit=10 - Top teams by market value
- GET    /api/teams/search/?q=united      - Advanced search

Team External API Operations:
- POST   /api/teams/fetch/                - Fetch teams from external API (Football-Data.org or API-Football)
- POST   /api/teams/sync/                 - Sync existing teams with external API data
- GET    /api/teams/operations/           - List team API sync operations history

Query parameters for listing:
- ?is_active=true/false                   - Filter by active status
- ?country=<uuid>                         - Filter by country ID
- ?sport=<id>                             - Filter by sport ID (leagues only)
- ?market_value_min=1000000               - Filter by minimum market value (teams only)
- ?market_value_max=1000000000            - Filter by maximum market value (teams only)
- ?search=keyword                         - Search in name, code, or external_id
- ?ordering=name,-created_at              - Order by field (- for descending)
- ?page=1&page_size=20                    - Pagination (default varies by endpoint)

Query parameters for operations:
- ?status=completed                       - Filter by operation status (pending, in_progress, completed, failed)
- ?provider=football_data_org             - Filter by API provider (football_data_org, api_football)
- ?days=30                                - Show operations from last N days (default: 7, max: 90)
- ?page=1&page_size=20                    - Pagination (default: 20 per page, max: 50)

Examples:
Leagues:
- GET /api/leagues/?is_active=true&ordering=name
- GET /api/leagues/?search=premier&country=<uuid>
- GET /api/leagues/{id}/
- GET /api/leagues/active/
- GET /api/leagues/by-country/{country_uuid}/
- GET /api/leagues/search/?q=premier

Teams:
- GET /api/teams/?is_active=true&ordering=-market_value
- GET /api/teams/?search=manchester&country=<uuid>
- GET /api/teams/{id}/
- GET /api/teams/active/
- GET /api/teams/by-country/{country_uuid}/
- GET /api/teams/top-by-market-value/?limit=10&country=<uuid>
- GET /api/teams/search/?q=united
- GET /api/teams/?market_value_min=100000000&market_value_max=1000000000

Teams External API Operations:
Fetch teams:
- POST /api/teams/fetch/
  Body: {
    "provider": "football-data",
    "all_european": true
  }
- POST /api/teams/fetch/
  Body: {
    "provider": "api-football",
    "leagues": ["PL", "SA"],
    "limit": 20
  }

Sync teams:
- POST /api/teams/sync/
  Body: {
    "fields": ["market_value", "logo"],
    "force": false
  }
- POST /api/teams/sync/
  Body: {
    "force": true,
    "deactivate_missing": true
  }

Operations history:
- GET /api/teams/operations/
- GET /api/teams/operations/?status=completed
- GET /api/teams/operations/?provider=football_data_org&days=30
- GET /api/teams/operations/?status=failed&page=2&page_size=10
"""
