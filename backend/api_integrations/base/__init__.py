"""
Base Classes Module

Provides reusable abstract base classes for API integrations:
- BaseAPIClient: Abstract HTTP client with authentication and error handling
- RateLimiter: Token bucket rate limiting
- RateLimiterRegistry: Registry for managing multiple rate limiters
- CacheManager: Django cache integration
- BaseResponseParser: Response parsing and validation
- Custom exceptions for API errors
"""

from .client import BaseAPIClient
from .exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)
from .rate_limiter import RateLimiter, RateLimiterRegistry
from .cache_manager import CacheManager
from .response_parser import BaseResponseParser

__all__ = [
    'BaseAPIClient',
    'APIError',
    'APIConnectionError',
    'APITimeoutError',
    'RateLimitError',
    'AuthenticationError',
    'NotFoundError',
    'ValidationError',
    'RateLimiter',
    'RateLimiterRegistry',
    'CacheManager',
    'BaseResponseParser',
]
