"""
API Integration Models

Django models for tracking API sync operations.
"""

from django.db import models
from django.utils import timezone
import uuid


class APISync(models.Model):
    """Track API sync operations."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    class Provider(models.TextChoices):
        FOOTBALL_DATA_ORG = 'football_data_org', 'Football-Data.org'
        API_FOOTBALL = 'api_football', 'API-Football'
    
    class ResourceType(models.TextChoices):
        TEAMS = 'teams', 'Teams'
        TEAM_STATS = 'team_stats', 'Team Stats'
        MATCHES = 'matches', 'Matches'
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Sync Info
    provider = models.CharField(
        max_length=50, 
        choices=Provider.choices,
        help_text='API provider used for this sync'
    )
    resource_type = models.CharField(
        max_length=50,
        choices=ResourceType.choices,
        help_text='Type of resource being synced'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text='Current status of sync operation'
    )
    
    # Timestamps
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text='When sync operation started'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When sync operation completed'
    )
    
    # Statistics
    records_processed = models.IntegerField(
        default=0,
        help_text='Number of records processed'
    )
    records_created = models.IntegerField(
        default=0,
        help_text='Number of new records created'
    )
    records_updated = models.IntegerField(
        default=0,
        help_text='Number of existing records updated'
    )
    records_failed = models.IntegerField(
        default=0,
        help_text='Number of records that failed to process'
    )
    
    # Error Tracking
    errors = models.JSONField(
        default=list,
        blank=True,
        help_text='List of errors encountered during sync'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Primary error message if sync failed'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata about the sync operation'
    )
    
    class Meta:
        db_table = 'api_sync'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['provider', 'resource_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-started_at']),
        ]
        verbose_name = 'API Sync'
        verbose_name_plural = 'API Syncs'
    
    def __str__(self):
        return f"{self.provider} - {self.resource_type} ({self.status})"
    
    @property
    def duration(self):
        """Calculate sync duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def mark_completed(self):
        """Mark sync as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message: str):
        """Mark sync as failed."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()