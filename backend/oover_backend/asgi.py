"""
ASGI config for Oover backend.

It exposes the ASGI callable as a module-level variable named ``application``.

ASGI (Asynchronous Server Gateway Interface) is used for deployment with
async-capable servers like Uvicorn, Daphne, or Hypercorn.

This enables support for:
- WebSockets
- Long-polling
- Server-Sent Events (SSE)
- HTTP/2

For more information on this file, see:
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/

Usage with Uvicorn:
    uvicorn oover_backend.asgi:application

Author: Oover Development Team
Date: October 2025
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oover_backend.settings')

application = get_asgi_application()
