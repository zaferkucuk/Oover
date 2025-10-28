"""
Celery Configuration for Oover Backend

This module configures Celery for handling asynchronous tasks like:
- Fetching data from external APIs (API-Football, Football-Data.org)
- Processing match predictions
- Sending notifications
- Scheduled data synchronization

Celery is optional for now but recommended for production.

For more information, see:
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

Author: Oover Development Team
Date: October 2025
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oover_backend.settings')

app = Celery('oover_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task to test Celery configuration.
    
    Usage:
        from oover_backend.celery import debug_task
        debug_task.delay()
    """
    print(f'Request: {self.request!r}')


# Example Celery configuration (add to settings.py if needed):
"""
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule (for periodic tasks)
CELERY_BEAT_SCHEDULE = {
    'sync-matches-every-hour': {
        'task': 'apps.matches.tasks.sync_matches',
        'schedule': crontab(minute=0),  # Every hour
    },
}
"""
