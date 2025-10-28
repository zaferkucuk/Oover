"""
WSGI config for Oover backend.

It exposes the WSGI callable as a module-level variable named ``application``.

WSGI (Web Server Gateway Interface) is used for deployment with traditional
web servers like Gunicorn, uWSGI, or Apache with mod_wsgi.

For more information on this file, see:
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/

Usage with Gunicorn:
    gunicorn oover_backend.wsgi:application

Author: Oover Development Team
Date: October 2025
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oover_backend.settings')

application = get_wsgi_application()
