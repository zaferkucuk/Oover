"""
URL Configuration for Core App

This module defines URL patterns for the core app,
including routes for Country and League API endpoints.

Author: Oover Development Team
Date: October 2025
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core.views import CountryViewSet, LeagueViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'leagues', LeagueViewSet, basename='league')

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

Query parameters for listing:
- ?is_active=true/false                   - Filter by active status
- ?country=<uuid>                         - Filter by country ID
- ?sport=<id>                             - Filter by sport ID
- ?search=keyword                         - Search in name or external_id
- ?ordering=name,-created_at              - Order by field (- for descending)
- ?page=1&page_size=20                    - Pagination (default: page_size=20)

Examples:
- GET /api/leagues/?is_active=true&ordering=name
- GET /api/leagues/?search=premier&country=<uuid>
- GET /api/leagues/{id}/
- GET /api/leagues/active/
- GET /api/leagues/by-country/{country_uuid}/
- GET /api/leagues/search/?q=premier
"""
