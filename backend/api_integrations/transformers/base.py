"""
Base Transformer

Abstract base class for data transformers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """Abstract base class for data transformers."""
    
    def __init__(self):
        """Initialize transformer."""
        self.errors = []
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API data to database model format."""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate transformed data."""
        pass
    
    def collect_error(self, error: str) -> None:
        """Collect validation/transformation error."""
        self.errors.append(error)
        logger.warning(f"Transformation error: {error}")
    
    def get_errors(self) -> List[str]:
        """Get all collected errors."""
        return self.errors
    
    def clear_errors(self) -> None:
        """Clear error list."""
        self.errors = []