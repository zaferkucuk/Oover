from django.apps import AppConfig


class ApiIntegrationsConfig(AppConfig):
    """Django app configuration for API Integrations."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_integrations'
    verbose_name = 'API Integrations'