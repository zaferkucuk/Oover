"""
Base Response Parser

Abstract base class for parsing API responses.
Handles JSON parsing, error detection, and pagination.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseResponseParser(ABC):
    """Abstract base class for API response parsers."""
    
    @abstractmethod
    def parse(self, response: Any) -> Dict[str, Any]:
        """Parse API response."""
        pass
    
    @abstractmethod
    def parse_error(self, response: Any) -> str:
        """Parse error response."""
        pass
    
    @abstractmethod
    def extract_pagination(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract pagination metadata from response."""
        pass
    
    def is_error_response(self, response: Any) -> bool:
        """Check if response is an error."""
        # TODO: Implement in Phase 1.4
        raise NotImplementedError("Error detection not yet implemented")