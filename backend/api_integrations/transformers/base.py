"""
Base Transformer Module

Abstract base class for transforming API responses to database models.
Provides validation, error handling, and logging infrastructure.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
import logging


logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """
    Abstract base class for data transformers.
    
    Transforms external API responses into internal database model formats
    with comprehensive validation and error handling.
    
    Attributes:
        errors (List[str]): Collected validation/transformation errors
        logger (logging.Logger): Logger instance for the transformer
    
    Example:
        ```python
        class TeamTransformer(BaseTransformer):
            def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
                if not self.validate(data, ['id', 'name']):
                    return None
                return {
                    'external_id': data['id'],
                    'name': data['name'],
                    # ... more fields
                }
            
            def validate(self, data: Dict[str, Any]) -> bool:
                required_fields = ['id', 'name']
                return self._validate_required_fields(data, required_fields)
        ```
    """
    
    def __init__(self):
        """Initialize transformer with error collection and logging."""
        self.errors: List[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform API response data to database model format.
        
        Args:
            data: Raw API response data
            
        Returns:
            Transformed data ready for model creation, or None if validation fails
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate API response data before transformation.
        
        Args:
            data: API response data to validate
            
        Returns:
            True if data is valid, False otherwise
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        pass
    
    def transform_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of API responses.
        
        Filters out invalid items and collects errors.
        
        Args:
            data_list: List of API response data dictionaries
            
        Returns:
            List of successfully transformed data dictionaries
            
        Example:
            ```python
            transformer = TeamTransformer()
            results = transformer.transform_batch(api_responses)
            if transformer.has_errors():
                print(f"Errors: {transformer.get_errors()}")
            ```
        """
        results = []
        
        for idx, data in enumerate(data_list):
            try:
                transformed = self.transform(data)
                if transformed is not None:
                    results.append(transformed)
                else:
                    self._collect_error(f"Item {idx}: Validation failed")
            except Exception as e:
                self._collect_error(f"Item {idx}: Transformation error - {str(e)}")
                self.logger.exception(f"Error transforming item {idx}")
        
        self.logger.info(
            f"Batch transformation complete: "
            f"{len(results)}/{len(data_list)} successful, "
            f"{len(self.errors)} errors"
        )
        
        return results
    
    def _validate_required_fields(
        self, 
        data: Dict[str, Any], 
        required_fields: List[str]
    ) -> bool:
        """
        Validate that all required fields are present and not None.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            True if all required fields exist and are not None, False otherwise
            
        Example:
            ```python
            required = ['id', 'name', 'country']
            if not self._validate_required_fields(data, required):
                return None
            ```
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            self._collect_error(error_msg)
            return False
        
        return True
    
    def _validate_field_type(
        self, 
        value: Any, 
        expected_type: Type, 
        field_name: str,
        allow_none: bool = False
    ) -> bool:
        """
        Validate that a field value matches the expected type.
        
        Args:
            value: Value to validate
            expected_type: Expected Python type (e.g., str, int, dict)
            field_name: Name of the field (for error messages)
            allow_none: Whether None is an acceptable value
            
        Returns:
            True if type matches or is None (when allowed), False otherwise
            
        Example:
            ```python
            if not self._validate_field_type(data['id'], int, 'id'):
                return None
            
            # Allow optional fields
            self._validate_field_type(
                data.get('website'), 
                str, 
                'website', 
                allow_none=True
            )
            ```
        """
        if value is None:
            if allow_none:
                return True
            error_msg = f"Field '{field_name}' cannot be None"
            self._collect_error(error_msg)
            return False
        
        if not isinstance(value, expected_type):
            error_msg = (
                f"Field '{field_name}' type mismatch: "
                f"expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
            self._collect_error(error_msg)
            return False
        
        return True
    
    def _collect_error(self, error_message: str) -> None:
        """
        Collect a validation or transformation error.
        
        Args:
            error_message: Error description
        """
        self.errors.append(error_message)
        self.logger.warning(f"Transformation error: {error_message}")
    
    def get_errors(self) -> List[str]:
        """
        Get all collected errors.
        
        Returns:
            List of error messages
        """
        return self.errors
    
    def clear_errors(self) -> None:
        """
        Clear all collected errors.
        
        Useful when reusing transformer instances.
        """
        self.errors = []
        self.logger.debug("Cleared error list")
    
    def has_errors(self) -> bool:
        """
        Check if any errors have been collected.
        
        Returns:
            True if errors exist, False otherwise
            
        Example:
            ```python
            transformer.transform_batch(data)
            if transformer.has_errors():
                print("Errors occurred during transformation")
                for error in transformer.get_errors():
                    print(f"  - {error}")
            ```
        """
        return len(self.errors) > 0
