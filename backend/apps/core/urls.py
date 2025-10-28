"""
URL Configuration for Core App

This module defines URL patterns for the core app,
including routes for Country API endpoints.

Author: Oover Development Team
Date: October 2025
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core.views.country import CountryViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')

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

Query parameters for listing:
- ?is_active=true/false                   - Filter by active status
- ?is_international=true/false            - Filter by international status
- ?search=keyword                         - Search in name or code
- ?ordering=name,-code                    - Order by field (- for descending)
- ?page=1&page_size=50                    - Pagination (default: page_size=50)

Examples:
- GET /api/countries/?is_active=true&ordering=name
- GET /api/countries/?search=england
- GET /api/countries/england/
- GET /api/countries/active/
- GET /api/countries/stats/
- GET /api/countries/england/with_relations/
"""
