"""
Custom Exceptions for API Integrations

Provides a hierarchy of exceptions for different API error scenarios.
"""


class APIError(Exception):
    """Base exception for all API-related errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class APIConnectionError(APIError):
    """Raised when unable to connect to the API."""
    pass


class APITimeoutError(APIError):
    """Raised when API request times out."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass


class NotFoundError(APIError):
    """Raised when requested resource is not found (404)."""
    pass


class ValidationError(APIError):
    """Raised when API response validation fails."""
    pass