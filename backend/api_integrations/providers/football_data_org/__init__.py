"""
Football-Data.org API Provider

Primary API for major European leagues.
Rate limit: 10 requests/minute (free tier)

Documentation: https://www.football-data.org/documentation
"""

from .client import FootballDataClient

__all__ = ['FootballDataClient']