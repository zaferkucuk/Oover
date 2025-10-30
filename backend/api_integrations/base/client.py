"""
Base API Client

Abstract base class for all API clients. Provides:
- HTTP methods (GET, POST, PUT, DELETE)
- Authentication handling
- Rate limiting integration
- Cache integration
- Error handling and retries
- Request/response logging
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Abstract base class for API clients."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            api_key: API authentication key (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None  # Will be initialized in subclasses
        logger.info(f"Initialized {self.__class__.__name__} with base_url={base_url}")
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests (including authentication)."""
        pass
    
    @abstractmethod
    def _handle_response(self, response: Any) -> Dict[str, Any]:
        """Handle and parse API response."""
        pass
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        # TODO: Implement in Phase 1.1
        raise NotImplementedError("GET method not yet implemented")
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request to the API."""
        # TODO: Implement in Phase 1.1
        raise NotImplementedError("POST method not yet implemented")
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PUT request to the API."""
        # TODO: Implement in Phase 1.1
        raise NotImplementedError("PUT method not yet implemented")
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request to the API."""
        # TODO: Implement in Phase 1.1
        raise NotImplementedError("DELETE method not yet implemented")