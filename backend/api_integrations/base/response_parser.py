"""
Base Response Parser

Abstract base class for parsing API responses.
Handles JSON parsing, error detection, pagination, and data extraction.

Example:
    class FootballDataParser(BaseResponseParser):
        def parse(self, response):
            return self.parse_json(response.text)
        
        def parse_error(self, response):
            data = self.parse_json(response.text)
            return data.get('message', 'Unknown error')
        
        def extract_pagination(self, response):
            # Football-Data.org doesn't use pagination
            return None
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import json
import logging

try:
    from requests import Response
except ImportError:
    Response = Any  # Fallback if requests not installed

logger = logging.getLogger(__name__)


class BaseResponseParser(ABC):
    """
    Abstract base class for API response parsers.
    
    Provides common utilities for:
    - JSON parsing with error handling
    - Error response detection
    - Pagination metadata extraction
    - Data extraction from nested responses
    
    Subclasses must implement:
    - parse(): Parse successful response
    - parse_error(): Parse error response
    - extract_pagination(): Extract pagination metadata
    
    Example:
        class MyAPIParser(BaseResponseParser):
            def parse(self, response):
                data = self.parse_json(response.text)
                return self.extract_list(data, 'items')
            
            def parse_error(self, response):
                data = self.parse_json(response.text)
                return data.get('error', {}).get('message', 'Unknown error')
            
            def extract_pagination(self, response):
                data = self.parse_json(response.text)
                pagination = data.get('pagination', {})
                return {
                    'next_page': pagination.get('next'),
                    'has_next': pagination.get('has_next', False),
                    'total_count': pagination.get('total')
                }
    """
    
    # =========================================================================
    # ABSTRACT METHODS (must be implemented by subclasses)
    # =========================================================================
    
    @abstractmethod
    def parse(self, response: Response) -> Union[Dict[str, Any], List[Any]]:
        """
        Parse successful API response.
        
        Args:
            response: Raw HTTP response object
            
        Returns:
            Parsed response data (dict or list)
            
        Raises:
            ValueError: If parsing fails
            
        Example:
            def parse(self, response):
                data = self.parse_json(response.text)
                return self.extract_list(data, 'teams')
        """
        pass
    
    @abstractmethod
    def parse_error(self, response: Response) -> str:
        """
        Parse error response and extract error message.
        
        Args:
            response: Raw HTTP response object
            
        Returns:
            Error message as string
            
        Example:
            def parse_error(self, response):
                data = self.parse_json(response.text)
                error = data.get('error', {})
                return error.get('message', 'Unknown error')
        """
        pass
    
    @abstractmethod
    def extract_pagination(self, response: Response) -> Optional[Dict[str, Any]]:
        """
        Extract pagination metadata from response.
        
        Args:
            response: Raw HTTP response object
            
        Returns:
            Pagination metadata dict with keys:
            - next_page: Next page number/token (optional)
            - has_next: Whether there's a next page (bool)
            - total_count: Total number of items (optional)
            - page_size: Items per page (optional)
            - current_page: Current page number (optional)
            
            Returns None if pagination not supported.
            
        Example:
            def extract_pagination(self, response):
                data = self.parse_json(response.text)
                pagination = data.get('pagination', {})
                return {
                    'next_page': pagination.get('next'),
                    'has_next': pagination.get('has_next', False),
                    'total_count': pagination.get('total'),
                    'page_size': pagination.get('limit'),
                    'current_page': pagination.get('page')
                }
        """
        pass
    
    # =========================================================================
    # UTILITY METHODS (provided for subclasses)
    # =========================================================================
    
    def parse_json(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON string with error handling.
        
        Args:
            text: JSON string to parse
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            ValueError: If JSON parsing fails
            
        Example:
            >>> response_text = '{"teams": [...]}'
            >>> data = self.parse_json(response_text)
            >>> print(data['teams'])
            [...]
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw response text (first 500 chars): {text[:500]}...")
            raise ValueError(f"Invalid JSON response: {str(e)}")
    
    def is_error_response(self, response: Response) -> bool:
        """
        Check if response is an error based on HTTP status code.
        
        Args:
            response: HTTP response object
            
        Returns:
            True if response is an error (status >= 400)
            
        Example:
            >>> if self.is_error_response(response):
            ...     error_msg = self.parse_error(response)
            ...     raise APIError(error_msg)
        """
        if not hasattr(response, 'status_code'):
            logger.warning("Response object has no status_code attribute")
            return False
        
        is_error = response.status_code >= 400
        if is_error:
            logger.warning(
                f"Error response detected: {response.status_code} "
                f"{response.reason if hasattr(response, 'reason') else ''}"
            )
        return is_error
    
    def is_success_response(self, response: Response) -> bool:
        """
        Check if response is successful (2xx status code).
        
        Args:
            response: HTTP response object
            
        Returns:
            True if response is successful (200 <= status < 300)
            
        Example:
            >>> if self.is_success_response(response):
            ...     data = self.parse(response)
        """
        if not hasattr(response, 'status_code'):
            logger.warning("Response object has no status_code attribute")
            return False
        
        return 200 <= response.status_code < 300
    
    def extract_data(
        self, 
        response_dict: Dict[str, Any], 
        key: Optional[str] = None
    ) -> Any:
        """
        Extract data from nested response dictionary.
        
        Args:
            response_dict: Parsed response dictionary
            key: Optional key to extract (e.g., 'teams', 'data', 'results')
                 If None, returns entire dict
            
        Returns:
            Extracted data (can be dict, list, or any type)
            Returns None if key not found
            
        Example:
            >>> # Response: {"data": {"teams": [...]}}
            >>> data = self.extract_data(response_dict, 'data')
            >>> # Returns: {"teams": [...]}
            >>> 
            >>> teams = self.extract_data(data, 'teams')
            >>> # Returns: [...]
        """
        if key is None:
            return response_dict
        
        if key not in response_dict:
            logger.warning(f"Key '{key}' not found in response")
            logger.debug(f"Available keys: {list(response_dict.keys())}")
            return None
        
        return response_dict[key]
    
    def extract_list(
        self,
        response_dict: Dict[str, Any],
        key: str,
        default: Optional[List] = None
    ) -> List[Any]:
        """
        Extract list from response, with fallback to default.
        
        Args:
            response_dict: Parsed response dictionary
            key: Key to extract (e.g., 'teams', 'results')
            default: Default value if key not found (default: [])
            
        Returns:
            Extracted list, or default if not found or wrong type
            
        Example:
            >>> teams = self.extract_list(response_dict, 'teams')
            >>> # Returns: [...] or []
            >>> 
            >>> teams = self.extract_list(response_dict, 'teams', default=None)
            >>> # Returns: [...] or None
        """
        if default is None:
            default = []
        
        data = self.extract_data(response_dict, key)
        if data is None:
            return default
        
        if not isinstance(data, list):
            logger.warning(f"Expected list for key '{key}', got {type(data)}")
            return default
        
        return data
    
    def extract_item(
        self,
        response_dict: Dict[str, Any],
        key: str,
        default: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Extract single item (dict) from response, with fallback to default.
        
        Args:
            response_dict: Parsed response dictionary
            key: Key to extract (e.g., 'team', 'result')
            default: Default value if key not found (default: {})
            
        Returns:
            Extracted dict, or default if not found or wrong type
            
        Example:
            >>> team = self.extract_item(response_dict, 'team')
            >>> # Returns: {...} or {}
            >>> 
            >>> team = self.extract_item(response_dict, 'team', default=None)
            >>> # Returns: {...} or None
        """
        if default is None:
            default = {}
        
        data = self.extract_data(response_dict, key)
        if data is None:
            return default
        
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for key '{key}', got {type(data)}")
            return default
        
        return data
    
    def has_next_page(self, pagination: Optional[Dict[str, Any]]) -> bool:
        """
        Check if there's a next page.
        
        Args:
            pagination: Pagination metadata dict (from extract_pagination)
            
        Returns:
            True if next page exists
            
        Example:
            >>> pagination = self.extract_pagination(response)
            >>> if self.has_next_page(pagination):
            ...     next_page = pagination['next_page']
            ...     # Fetch next page...
        """
        if pagination is None:
            return False
        return pagination.get('has_next', False)
    
    def get_next_page_token(self, pagination: Optional[Dict[str, Any]]) -> Optional[Union[str, int]]:
        """
        Get next page token/number.
        
        Args:
            pagination: Pagination metadata dict (from extract_pagination)
            
        Returns:
            Next page token/number, or None if not available
            
        Example:
            >>> pagination = self.extract_pagination(response)
            >>> next_token = self.get_next_page_token(pagination)
            >>> if next_token:
            ...     response = fetch_page(next_token)
        """
        if pagination is None:
            return None
        return pagination.get('next_page')
    
    def get_total_count(self, pagination: Optional[Dict[str, Any]]) -> Optional[int]:
        """
        Get total count of items across all pages.
        
        Args:
            pagination: Pagination metadata dict (from extract_pagination)
            
        Returns:
            Total count, or None if not available
            
        Example:
            >>> pagination = self.extract_pagination(response)
            >>> total = self.get_total_count(pagination)
            >>> logger.info(f"Found {total} total items")
        """
        if pagination is None:
            return None
        return pagination.get('total_count')
    
    def get_current_page(self, pagination: Optional[Dict[str, Any]]) -> Optional[int]:
        """
        Get current page number.
        
        Args:
            pagination: Pagination metadata dict (from extract_pagination)
            
        Returns:
            Current page number, or None if not available
            
        Example:
            >>> pagination = self.extract_pagination(response)
            >>> page = self.get_current_page(pagination)
            >>> logger.info(f"Processing page {page}")
        """
        if pagination is None:
            return None
        return pagination.get('current_page')
    
    def get_page_size(self, pagination: Optional[Dict[str, Any]]) -> Optional[int]:
        """
        Get number of items per page.
        
        Args:
            pagination: Pagination metadata dict (from extract_pagination)
            
        Returns:
            Page size, or None if not available
            
        Example:
            >>> pagination = self.extract_pagination(response)
            >>> size = self.get_page_size(pagination)
            >>> logger.info(f"Items per page: {size}")
        """
        if pagination is None:
            return None
        return pagination.get('page_size')
    
    def validate_response(self, response: Response) -> None:
        """
        Validate response and raise error if invalid.
        
        Args:
            response: HTTP response object
            
        Raises:
            ValueError: If response is invalid (error status code)
            
        Example:
            >>> self.validate_response(response)
            >>> data = self.parse(response)  # Only runs if validation passes
        """
        if not self.is_success_response(response):
            error_msg = self.parse_error(response)
            status_code = getattr(response, 'status_code', 'unknown')
            raise ValueError(f"API request failed (HTTP {status_code}): {error_msg}")


# =============================================================================
# CONCRETE IMPLEMENTATIONS
# =============================================================================


class JSONResponseParser(BaseResponseParser):
    """
    Generic JSON response parser for simple APIs.
    
    Assumes responses are straightforward JSON with optional 'data' wrapper.
    Good for APIs that return simple JSON without complex nesting.
    
    Supported response formats:
        {"teams": [...]}
        {"data": {"teams": [...]}}
        {"results": [...], "pagination": {...}}
        {"items": [...], "meta": {"page": 1, "total": 100}}
    
    Example:
        # Simple usage (data at root level)
        parser = JSONResponseParser()
        teams = parser.parse(response)
        
        # With nested data key
        parser = JSONResponseParser(data_key='data')
        teams = parser.parse(response)
        
        # Custom error key
        parser = JSONResponseParser(error_key='errors')
        error = parser.parse_error(response)
    """
    
    def __init__(
        self,
        data_key: Optional[str] = None,
        error_key: str = 'error',
        pagination_keys: Optional[List[str]] = None
    ):
        """
        Initialize parser.
        
        Args:
            data_key: Key where actual data is nested (e.g., 'data', 'results')
                     If None, assumes data is at root level
            error_key: Key where error message is located (default: 'error')
            pagination_keys: List of keys to check for pagination data
                           (default: ['pagination', 'paging', 'page_info', 'meta'])
        """
        self.data_key = data_key
        self.error_key = error_key
        self.pagination_keys = pagination_keys or ['pagination', 'paging', 'page_info', 'meta']
    
    def parse(self, response: Response) -> Union[Dict[str, Any], List[Any]]:
        """
        Parse JSON response.
        
        Returns data from specified data_key if configured,
        otherwise returns entire response.
        """
        data = self.parse_json(response.text)
        if self.data_key:
            extracted = self.extract_data(data, self.data_key)
            return extracted if extracted is not None else {}
        return data
    
    def parse_error(self, response: Response) -> str:
        """
        Parse error from JSON response.
        
        Tries multiple common error message patterns:
        - error.message
        - error.msg
        - error.detail
        - error (if string)
        - Fallback to HTTP status
        """
        try:
            data = self.parse_json(response.text)
            error = data.get(self.error_key, {})
            
            # Try common error message keys
            if isinstance(error, dict):
                for key in ['message', 'msg', 'detail', 'description', 'error_description']:
                    if key in error:
                        return str(error[key])
            elif isinstance(error, str):
                return error
            
            # Check root-level message keys
            for key in ['message', 'msg', 'detail']:
                if key in data:
                    return str(data[key])
            
            # Fallback to HTTP status
            status_text = f"HTTP {response.status_code}"
            if hasattr(response, 'reason'):
                status_text += f": {response.reason}"
            return status_text
            
        except Exception as e:
            logger.error(f"Failed to parse error response: {e}")
            status_text = f"HTTP {response.status_code}"
            if hasattr(response, 'reason'):
                status_text += f": {response.reason}"
            return status_text
    
    def extract_pagination(self, response: Response) -> Optional[Dict[str, Any]]:
        """
        Extract pagination from JSON response.
        
        Looks for pagination data in configurable keys (default: pagination, paging, page_info, meta).
        Returns standardized pagination dict or None if not found.
        """
        try:
            data = self.parse_json(response.text)
            
            # Try configured pagination keys
            for key in self.pagination_keys:
                if key in data:
                    page_data = data[key]
                    return {
                        'next_page': page_data.get('next') or page_data.get('next_page'),
                        'has_next': page_data.get('has_next', False) or page_data.get('hasNext', False),
                        'total_count': page_data.get('total') or page_data.get('total_count'),
                        'page_size': (
                            page_data.get('limit') or 
                            page_data.get('page_size') or 
                            page_data.get('per_page')
                        ),
                        'current_page': page_data.get('page') or page_data.get('current_page')
                    }
            
            # No pagination found
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract pagination: {e}")
            return None
