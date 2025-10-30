"""
API Integration URLs

URL configuration for API integration endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APISyncViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r'sync', APISyncViewSet, basename='api-sync')

app_name = 'api_integrations'

urlpatterns = [
    path('', include(router.urls)),
]