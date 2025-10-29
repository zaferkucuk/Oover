"""
Core app views package.

This module exports all viewsets from the core app for easy importing.
"""

from apps.core.views.country import CountryViewSet

__all__ = [
    'CountryViewSet',
]
