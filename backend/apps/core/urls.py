"""
URL Configuration for Core App

This module defines URL routes for the core application.
Uses Django REST Framework's DefaultRouter for ViewSet registration.

API Endpoints:
    /api/countries/              - List/Create countries
    /api/countries/{id}/         - Retrieve/Update/Delete country
    /api/countries/search/       - Search countries
    /api/countries/statistics/   - Get statistics
    /api/countries/export/       - Export data
    /api/countries/bulk_create/  - Bulk create countries
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
