"""
Base API Service

Provides common CRUD operations and patterns for all API services.
Implements transaction management, error handling, and logging.

Usage:
    class TeamsService(BaseAPIService):
        model = Team
        
        def custom_method(self):
            # Custom business logic
            pass
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from django.db import models, transaction
from django.db.models import QuerySet
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import logging

# Generic type for model classes
T = TypeVar('T', bound=models.Model)

logger = logging.getLogger(__name__)


class BaseAPIService(ABC, Generic[T]):
    """
    Abstract base service class providing common CRUD operations.
    
    All service classes should inherit from this base class to ensure
    consistent patterns across the application.
    
    Attributes:
        model: Django model class that this service manages
    
    Example:
        class TeamsService(BaseAPIService[Team]):
            model = Team
            
            def fetch_from_api(self, provider: str) -> List[Team]:
                # Custom business logic
                pass
    """
    
    model: Type[T] = None  # Must be set by subclasses
    
    def __init__(self):
        """Initialize the service and validate configuration."""
        if self.model is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a 'model' attribute"
            )
        logger.info(f"Initialized {self.__class__.__name__} for {self.model.__name__}")
    
    # ==================== READ OPERATIONS ====================
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Retrieve a single object by its ID.
        
        Args:
            id: Primary key value
            
        Returns:
            Model instance if found, None otherwise
            
        Example:
            team = service.get_by_id(uuid.UUID('...'))
        """
        try:
            return self.model.objects.get(pk=id)
        except ObjectDoesNotExist:
            logger.warning(f"{self.model.__name__} with id={id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by id={id}: {str(e)}")
            raise
    
    def get_by_field(self, **filters) -> Optional[T]:
        """
        Retrieve a single object by field filters.
        
        Args:
            **filters: Field filters (e.g., external_id='provider-123')
            
        Returns:
            Model instance if found, None otherwise
            
        Example:
            team = service.get_by_field(external_id='football-data-123')
        """
        try:
            return self.model.objects.get(**filters)
        except ObjectDoesNotExist:
            logger.debug(f"{self.model.__name__} not found with filters: {filters}")
            return None
        except self.model.MultipleObjectsReturned:
            logger.error(f"Multiple {self.model.__name__} found with filters: {filters}")
            raise
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} with filters {filters}: {str(e)}")
            raise
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QuerySet[T]:
        """
        List objects with optional filtering, ordering, and pagination.
        
        Args:
            filters: Dictionary of field filters
            order_by: List of field names to order by (prefix with '-' for descending)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            QuerySet of model instances
            
        Example:
            teams = service.list(
                filters={'country__name': 'England'},
                order_by=['-created_at'],
                limit=20
            )
        """
        try:
            queryset = self.model.objects.all()
            
            # Apply filters
            if filters:
                queryset = queryset.filter(**filters)
            
            # Apply ordering
            if order_by:
                queryset = queryset.order_by(*order_by)
            
            # Apply pagination
            if offset:
                queryset = queryset[offset:]
            if limit:
                queryset = queryset[:limit]
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error listing {self.model.__name__}: {str(e)}")
            raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count objects matching the given filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching objects
            
        Example:
            active_count = service.count(filters={'is_active': True})
        """
        try:
            queryset = self.model.objects.all()
            if filters:
                queryset = queryset.filter(**filters)
            return queryset.count()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise
    
    def exists(self, **filters) -> bool:
        """
        Check if objects matching the filters exist.
        
        Args:
            **filters: Field filters
            
        Returns:
            True if at least one object exists, False otherwise
            
        Example:
            exists = service.exists(external_id='provider-123')
        """
        try:
            return self.model.objects.filter(**filters).exists()
        except Exception as e:
            logger.error(f"Error checking existence for {self.model.__name__}: {str(e)}")
            raise
    
    # ==================== WRITE OPERATIONS ====================
    
    @transaction.atomic
    def create(self, data: Dict[str, Any], validate: bool = True) -> T:
        """
        Create a new object.
        
        Args:
            data: Dictionary of field values
            validate: Whether to run model validation
            
        Returns:
            Created model instance
            
        Raises:
            ValidationError: If validation fails
            
        Example:
            team = service.create({
                'name': 'Arsenal FC',
                'code': 'ARS',
                'country_id': country.id
            })
        """
        try:
            instance = self.model(**data)
            
            if validate:
                instance.full_clean()
            
            instance.save()
            logger.info(f"Created {self.model.__name__} with id={instance.pk}")
            return instance
            
        except ValidationError as e:
            logger.warning(f"Validation error creating {self.model.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    @transaction.atomic
    def update(self, id: Any, data: Dict[str, Any], validate: bool = True) -> Optional[T]:
        """
        Update an existing object by ID.
        
        Args:
            id: Primary key value
            data: Dictionary of field values to update
            validate: Whether to run model validation
            
        Returns:
            Updated model instance if found, None otherwise
            
        Example:
            team = service.update(team_id, {'name': 'New Name'})
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            
            for field, value in data.items():
                setattr(instance, field, value)
            
            if validate:
                instance.full_clean()
            
            instance.save()
            logger.info(f"Updated {self.model.__name__} with id={id}")
            return instance
            
        except ValidationError as e:
            logger.warning(f"Validation error updating {self.model.__name__} id={id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} id={id}: {str(e)}")
            raise
    
    @transaction.atomic
    def delete(self, id: Any) -> bool:
        """
        Delete an object by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            True if deleted, False if not found
            
        Example:
            deleted = service.delete(team_id)
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            instance.delete()
            logger.info(f"Deleted {self.model.__name__} with id={id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} id={id}: {str(e)}")
            raise
    
    # ==================== BULK OPERATIONS ====================
    
    @transaction.atomic
    def bulk_create(
        self,
        data_list: List[Dict[str, Any]],
        batch_size: int = 100,
        ignore_conflicts: bool = False
    ) -> List[T]:
        """
        Create multiple objects in a single transaction.
        
        Args:
            data_list: List of dictionaries with field values
            batch_size: Number of objects to create per query
            ignore_conflicts: Whether to ignore duplicate key errors
            
        Returns:
            List of created model instances
            
        Example:
            teams = service.bulk_create([
                {'name': 'Team 1', 'code': 'T1', 'country_id': country.id},
                {'name': 'Team 2', 'code': 'T2', 'country_id': country.id}
            ])
        """
        try:
            instances = [self.model(**data) for data in data_list]
            
            created = self.model.objects.bulk_create(
                instances,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts
            )
            
            logger.info(f"Bulk created {len(created)} {self.model.__name__} instances")
            return created
            
        except Exception as e:
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            raise
    
    @transaction.atomic
    def bulk_update(
        self,
        updates: List[tuple[Any, Dict[str, Any]]],
        fields: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> int:
        """
        Update multiple objects in a single transaction.
        
        Args:
            updates: List of (id, data) tuples
            fields: List of field names to update (if None, all fields in data)
            batch_size: Number of objects to update per query
            
        Returns:
            Number of objects updated
            
        Example:
            updated = service.bulk_update([
                (team1_id, {'name': 'New Name 1'}),
                (team2_id, {'name': 'New Name 2'})
            ])
        """
        try:
            instances = []
            update_fields = set()
            
            for obj_id, data in updates:
                instance = self.get_by_id(obj_id)
                if not instance:
                    continue
                
                for field, value in data.items():
                    setattr(instance, field, value)
                    update_fields.add(field)
                
                instances.append(instance)
            
            if not instances:
                logger.warning("No instances to update")
                return 0
            
            # Use specified fields or all updated fields
            fields_to_update = fields or list(update_fields)
            
            updated_count = len(instances)
            self.model.objects.bulk_update(
                instances,
                fields_to_update,
                batch_size=batch_size
            )
            
            logger.info(f"Bulk updated {updated_count} {self.model.__name__} instances")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error bulk updating {self.model.__name__}: {str(e)}")
            raise
    
    # ==================== UTILITY METHODS ====================
    
    def get_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **filters
    ) -> tuple[T, bool]:
        """
        Get an existing object or create a new one.
        
        Args:
            defaults: Field values for creating new object
            **filters: Field filters for lookup
            
        Returns:
            Tuple of (instance, created) where created is True if new
            
        Example:
            team, created = service.get_or_create(
                external_id='provider-123',
                defaults={'name': 'Arsenal', 'code': 'ARS'}
            )
        """
        try:
            instance, created = self.model.objects.get_or_create(
                defaults=defaults,
                **filters
            )
            
            action = "Created" if created else "Retrieved existing"
            logger.info(f"{action} {self.model.__name__} with filters: {filters}")
            return instance, created
            
        except Exception as e:
            logger.error(f"Error in get_or_create for {self.model.__name__}: {str(e)}")
            raise
    
    def update_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **filters
    ) -> tuple[T, bool]:
        """
        Update an existing object or create a new one.
        
        Args:
            defaults: Field values for update/create
            **filters: Field filters for lookup
            
        Returns:
            Tuple of (instance, created) where created is True if new
            
        Example:
            team, created = service.update_or_create(
                external_id='provider-123',
                defaults={'name': 'Arsenal FC', 'code': 'ARS'}
            )
        """
        try:
            instance, created = self.model.objects.update_or_create(
                defaults=defaults,
                **filters
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} {self.model.__name__} with filters: {filters}")
            return instance, created
            
        except Exception as e:
            logger.error(f"Error in update_or_create for {self.model.__name__}: {str(e)}")
            raise
