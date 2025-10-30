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
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
)

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """
    Abstract base class for API clients.
    
    Provides common functionality for making HTTP requests to external APIs:
    - Automatic retries with exponential backoff
    - Rate limiting integration
    - Response caching
    - Error handling and logging
    - Session management
    
    Subclasses must implement:
    - _get_headers(): Return headers dict including authentication
    - _handle_response(): Parse and validate API response
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API (without trailing slash)
            api_key: API authentication key (optional)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize session with retry strategy
        self.session = self._create_session()
        
        logger.info(
            f"Initialized {self.__class__.__name__} "
            f"(base_url={base_url}, timeout={timeout}s, max_retries={max_retries})"
        )
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.
        
        Must include authentication headers if required by the API.
        
        Returns:
            Dictionary of HTTP headers
        """
        pass
    
    @abstractmethod
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle and parse API response.
        
        Subclasses should:
        1. Validate response structure
        2. Parse response data
        3. Extract relevant fields
        4. Raise ValidationError if response is invalid
        
        Args:
            response: Raw requests.Response object
            
        Returns:
            Parsed response data as dictionary
            
        Raises:
            ValidationError: If response structure is invalid
        """
        pass
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: URL query parameters
            data: Form data for POST/PUT
            json: JSON data for POST/PUT
            
        Returns:
            Parsed response data
            
        Raises:
            APIConnectionError: If connection fails
            APITimeoutError: If request times out
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails (401, 403)
            NotFoundError: If resource not found (404)
            APIError: For other API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        logger.debug(
            f"{method} {url} "
            f"(params={params}, data={data is not None}, json={json is not None})"
        )
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
            )
            
            # Log response
            logger.debug(
                f"Response: {response.status_code} "
                f"(elapsed={response.elapsed.total_seconds():.2f}s)"
            )
            
            # Handle HTTP errors
            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError(
                    f"Authentication failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=self._safe_json(response),
                )
            
            if response.status_code == 404:
                raise NotFoundError(
                    f"Resource not found: {url}",
                    status_code=404,
                    response_data=self._safe_json(response),
                )
            
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise RateLimitError(
                    f"Rate limit exceeded (retry after {retry_after}s)",
                    status_code=429,
                    retry_after=int(retry_after),
                    response_data=self._safe_json(response),
                )
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Parse response using subclass implementation
            return self._handle_response(response)
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise APITimeoutError(
                f"Request to {url} timed out after {self.timeout}s",
                status_code=None,
            )
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIConnectionError(
                f"Failed to connect to {url}: {str(e)}",
                status_code=None,
            )
        
        except (RateLimitError, AuthenticationError, NotFoundError):
            # Re-raise our custom exceptions
            raise
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            raise APIError(
                f"API request failed: {str(e)}",
                status_code=status_code,
                response_data=self._safe_json(getattr(e, 'response', None)),
            )
    
    def _safe_json(self, response: Optional[requests.Response]) -> Optional[Dict]:
        """
        Safely extract JSON from response without raising exceptions.
        
        Args:
            response: requests.Response object or None
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        if response is None:
            return None
        
        try:
            return response.json()
        except (ValueError, AttributeError):
            return None
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint (e.g., 'teams' or '/teams')
            params: URL query parameters
            
        Returns:
            Parsed response data
            
        Example:
            >>> client.get('teams', params={'country': 'England'})
        """
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: API endpoint
            data: Form data (for application/x-www-form-urlencoded)
            json: JSON data (for application/json)
            
        Returns:
            Parsed response data
            
        Example:
            >>> client.post('teams', json={'name': 'New Team'})
        """
        return self._make_request('POST', endpoint, data=data, json=json)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a PUT request to the API.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            
        Returns:
            Parsed response data
            
        Example:
            >>> client.put('teams/123', json={'name': 'Updated Team'})
        """
        return self._make_request('PUT', endpoint, data=data, json=json)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Parsed response data
            
        Example:
            >>> client.delete('teams/123')
        """
        return self._make_request('DELETE', endpoint)
    
    def close(self):
        """Close the session and cleanup resources."""
        if self.session:
            self.session.close()
            logger.info(f"Closed {self.__class__.__name__} session")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
