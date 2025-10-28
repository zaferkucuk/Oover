#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This is the entry point for all Django management commands like:
- python manage.py runserver
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py makemigrations

Author: Oover Development Team
Date: October 2025
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # Set the default Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oover_backend.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
