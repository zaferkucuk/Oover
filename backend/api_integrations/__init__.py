"""
API Integrations Module

This module provides a reusable infrastructure for integrating with external APIs.
It includes base classes, providers, services, transformers, and management commands.

Architecture:
- base/: Reusable base classes (clients, rate limiters, cache, parsers)
- providers/: API provider implementations (Football-Data.org, API-Football, etc.)
- services/: Business logic for fetching and syncing data
- transformers/: Data transformation from API responses to database models
- management/commands/: Django commands for CLI operations
- tasks/: Celery/scheduled tasks for automation
"""

default_app_config = 'api_integrations.apps.ApiIntegrationsConfig'