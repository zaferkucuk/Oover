"""
Data Validators

Validation rules for API data transformation.
Provides base validation framework and specific validators for different entity types.
"""

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Type
from uuid import UUID

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """
    Abstract base class for data validators.
    
    Provides common validation methods and error handling.
    Subclasses must implement validate() method for specific entity validation.
    
    Example:
        class MyValidator(BaseValidator):
            def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
                errors = []
                
                # Validate required fields
                errors.extend(self._validate_required_fields(
                    data, ['field1', 'field2']
                ))
                
                # Validate field types
                errors.extend(self._validate_field_types(
                    data, {'field1': str, 'field2': int}
                ))
                
                return len(errors) == 0, errors
    """
    
    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data and return validation result.
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass
    
    def _validate_required_fields(
        self, 
        data: Dict[str, Any], 
        required_fields: List[str]
    ) -> List[str]:
        """
        Check if all required fields are present and non-empty.
        
        Args:
            data: Data dictionary
            required_fields: List of required field names
            
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                errors.append(f"Required field '{field}' is missing or empty")
                logger.warning(f"Missing required field: {field}")
        return errors
    
    def _validate_field_types(
        self, 
        data: Dict[str, Any], 
        field_types: Dict[str, Type]
    ) -> List[str]:
        """
        Validate data types of fields.
        
        Args:
            data: Data dictionary
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    errors.append(
                        f"Field '{field}' has invalid type. "
                        f"Expected {expected_type.__name__}, "
                        f"got {type(data[field]).__name__}"
                    )
                    logger.warning(
                        f"Type mismatch for {field}: "
                        f"expected {expected_type.__name__}, "
                        f"got {type(data[field]).__name__}"
                    )
        return errors
    
    def _validate_string_length(
        self, 
        data: Dict[str, Any], 
        field: str, 
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> List[str]:
        """
        Validate string field length.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            min_length: Minimum allowed length (optional)
            max_length: Maximum allowed length (optional)
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        if field in data and data[field] is not None:
            value = str(data[field])
            length = len(value)
            
            if min_length is not None and length < min_length:
                errors.append(
                    f"Field '{field}' is too short. "
                    f"Minimum length: {min_length}, got: {length}"
                )
            
            if max_length is not None and length > max_length:
                errors.append(
                    f"Field '{field}' is too long. "
                    f"Maximum length: {max_length}, got: {length}"
                )
        
        return errors
    
    def _validate_number_range(
        self, 
        data: Dict[str, Any], 
        field: str, 
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[str]:
        """
        Validate numeric field range.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        if field in data and data[field] is not None:
            try:
                value = float(data[field])
                
                if min_value is not None and value < min_value:
                    errors.append(
                        f"Field '{field}' is below minimum. "
                        f"Minimum: {min_value}, got: {value}"
                    )
                
                if max_value is not None and value > max_value:
                    errors.append(
                        f"Field '{field}' exceeds maximum. "
                        f"Maximum: {max_value}, got: {value}"
                    )
            except (TypeError, ValueError):
                errors.append(f"Field '{field}' is not a valid number")
        
        return errors
    
    def _validate_url(self, data: Dict[str, Any], field: str) -> List[str]:
        """
        Validate URL format.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        if field in data and data[field] is not None:
            url = str(data[field])
            # Simple URL validation
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE
            )
            
            if not url_pattern.match(url):
                errors.append(f"Field '{field}' is not a valid URL: {url}")
        
        return errors
    
    def _validate_uuid(self, data: Dict[str, Any], field: str) -> List[str]:
        """
        Validate UUID format.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        if field in data and data[field] is not None:
            try:
                UUID(str(data[field]))
            except (ValueError, AttributeError):
                errors.append(f"Field '{field}' is not a valid UUID")
        
        return errors
    
    def validate_batch(
        self, 
        data_list: List[Dict[str, Any]]
    ) -> tuple[bool, Dict[int, List[str]]]:
        """
        Validate a batch of data items.
        
        Args:
            data_list: List of data dictionaries to validate
            
        Returns:
            Tuple of (all_valid, error_dict)
            - all_valid: True if all items are valid
            - error_dict: Dictionary mapping item indices to their error lists
        """
        all_valid = True
        error_dict = {}
        
        for index, data in enumerate(data_list):
            is_valid, errors = self.validate(data)
            if not is_valid:
                all_valid = False
                error_dict[index] = errors
        
        return all_valid, error_dict


class TeamValidator(BaseValidator):
    """
    Validator for team data.
    
    Validates team data from API responses before database insertion.
    Includes required fields, data types, and business rules validation.
    
    Validation Rules:
        Required Fields:
            - name: Team name (string, 1-100 chars)
            - code: Team code (string, 2-10 chars)
            - country_id: Country UUID (valid UUID format)
        
        Optional Fields:
            - logo: Team logo URL (valid URL format)
            - website: Team website URL (valid URL format)
            - founded: Foundation year (integer, 1800-2100)
            - market_value: Market value (float, > 0)
            - is_active: Active status (boolean)
        
        Business Rules:
            - market_value must be positive if provided
            - founded year must be reasonable (1800-2100)
            - code length should be 2-10 characters
    
    Example:
        validator = TeamValidator()
        
        team_data = {
            'name': 'Manchester United',
            'code': 'MUN',
            'country_id': 'uuid-string',
            'founded': 1878,
            'logo': 'https://example.com/logo.png',
            'market_value': 500000000
        }
        
        is_valid, errors = validator.validate(team_data)
        if not is_valid:
            print(f"Validation errors: {errors}")
    """
    
    # Validation constants
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 100
    MIN_CODE_LENGTH = 2
    MAX_CODE_LENGTH = 10
    MIN_FOUNDED_YEAR = 1800
    MAX_FOUNDED_YEAR = 2100
    MIN_MARKET_VALUE = 0
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate team data.
        
        Args:
            data: Team data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # 1. Validate required fields
        errors.extend(self._validate_required_fields(
            data, ['name', 'code', 'country_id']
        ))
        
        # 2. Validate field types
        type_checks = {
            'name': str,
            'code': str,
        }
        errors.extend(self._validate_field_types(data, type_checks))
        
        # 3. Validate string lengths
        errors.extend(self._validate_string_length(
            data, 'name', 
            min_length=self.MIN_NAME_LENGTH, 
            max_length=self.MAX_NAME_LENGTH
        ))
        
        errors.extend(self._validate_string_length(
            data, 'code', 
            min_length=self.MIN_CODE_LENGTH, 
            max_length=self.MAX_CODE_LENGTH
        ))
        
        # 4. Validate UUID for country_id
        errors.extend(self._validate_uuid(data, 'country_id'))
        
        # 5. Validate optional URL fields
        if 'logo' in data and data['logo']:
            errors.extend(self._validate_url(data, 'logo'))
        
        if 'website' in data and data['website']:
            errors.extend(self._validate_url(data, 'website'))
        
        # 6. Validate founded year range
        if 'founded' in data and data['founded'] is not None:
            errors.extend(self._validate_number_range(
                data, 'founded',
                min_value=self.MIN_FOUNDED_YEAR,
                max_value=self.MAX_FOUNDED_YEAR
            ))
        
        # 7. Validate market_value (must be positive)
        if 'market_value' in data and data['market_value'] is not None:
            errors.extend(self._validate_number_range(
                data, 'market_value',
                min_value=self.MIN_MARKET_VALUE
            ))
        
        # 8. Validate is_active boolean
        if 'is_active' in data and data['is_active'] is not None:
            if not isinstance(data['is_active'], bool):
                errors.append(
                    f"Field 'is_active' must be boolean, "
                    f"got {type(data['is_active']).__name__}"
                )
        
        # Log validation result
        if errors:
            logger.warning(
                f"Team validation failed for '{data.get('name', 'Unknown')}': "
                f"{len(errors)} errors found"
            )
        else:
            logger.debug(
                f"Team validation successful for '{data.get('name', 'Unknown')}'"
            )
        
        return len(errors) == 0, errors


# Utility functions for backward compatibility
def validate_team_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Convenience function to validate team data.
    
    Args:
        data: Team data dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = TeamValidator()
    return validator.validate(data)


def validate_required_fields(
    data: Dict[str, Any], 
    required_fields: List[str]
) -> List[str]:
    """
    Convenience function to check required fields.
    
    Args:
        data: Data dictionary
        required_fields: List of required field names
        
    Returns:
        List of error messages (empty if all valid)
    """
    validator = BaseValidator.__new__(BaseValidator)
    validator.__init__()
    return validator._validate_required_fields(data, required_fields)


def validate_data_types(
    data: Dict[str, Any], 
    field_types: Dict[str, type]
) -> List[str]:
    """
    Convenience function to validate data types.
    
    Args:
        data: Data dictionary
        field_types: Dictionary mapping field names to expected types
        
    Returns:
        List of error messages (empty if all valid)
    """
    validator = BaseValidator.__new__(BaseValidator)
    validator.__init__()
    return validator._validate_field_types(data, field_types)
