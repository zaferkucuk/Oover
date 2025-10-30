"""
Services Package

This package contains business logic services for the Oover API.

Services follow a layered architecture:
- Base services provide common CRUD operations
- Specific services implement domain logic
- Services coordinate between models, transformers, and external APIs
"""

from .base import BaseAPIService

__all__ = ['BaseAPIService']
