"""
Views module initialization

Exports all ViewSets for easy importing in urls.py
"""

from .country import CountryViewSet

__all__ = ['CountryViewSet']
