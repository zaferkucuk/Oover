"""
API-Football Provider

Fallback API for comprehensive coverage.
Rate limit: 100 requests/day (free tier)

Documentation: https://www.api-football.com/documentation-v3
"""

from .client import APIFootballClient

__all__ = ['APIFootballClient']