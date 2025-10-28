"""
URL Configuration for Oover Backend

This module defines all URL patterns for the Oover API, including:
- Admin panel
- API endpoints (countries, leagues, teams, matches, predictions)
- API documentation (Swagger/ReDoc)
- Health check endpoint

The API follows RESTful conventions with versioned endpoints.

Author: Oover Development Team
Date: October 2025
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        200 OK with status information
    """
    return Response({
        'status': 'healthy',
        'service': 'oover-backend',
        'version': '1.0.0',
    })


@api_view(['GET'])
def api_root(request):
    """
    API root endpoint that lists all available API endpoints.
    
    Returns:
        Dictionary of available endpoints
    """
    return Response({
        'message': 'Welcome to Oover API',
        'version': '1.0.0',
        'endpoints': {
            'countries': '/api/countries/',
            'leagues': '/api/leagues/',
            'teams': '/api/teams/',
            'matches': '/api/matches/',
            'predictions': '/api/predictions/',
            'docs': {
                'swagger': '/api/docs/swagger/',
                'redoc': '/api/docs/redoc/',
                'schema': '/api/docs/schema/',
            },
            'health': '/health/',
            'admin': '/admin/',
        }
    })


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # API Documentation (OpenAPI/Swagger)
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints (will be added as we create apps)
    path('api/', include('apps.core.urls')),
    
    # Add more API endpoints here as apps are created:
    # path('api/', include('apps.countries.urls')),
    # path('api/', include('apps.leagues.urls')),
    # path('api/', include('apps.teams.urls')),
    # path('api/', include('apps.matches.urls')),
    # path('api/', include('apps.predictions.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = 'Oover Administration'
admin.site.site_title = 'Oover Admin'
admin.site.index_title = 'Welcome to Oover Admin Portal'
