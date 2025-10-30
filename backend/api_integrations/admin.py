"""
API Integration Admin

Django admin configuration for API integration models.
"""

from django.contrib import admin
from .models import APISync


@admin.register(APISync)
class APISyncAdmin(admin.ModelAdmin):
    """Admin interface for APISync model."""
    
    list_display = [
        'id',
        'provider',
        'resource_type',
        'status',
        'started_at',
        'completed_at',
        'records_processed',
        'duration_display',
    ]
    list_filter = ['provider', 'resource_type', 'status', 'started_at']
    search_fields = ['id', 'error_message']
    readonly_fields = [
        'id',
        'started_at',
        'completed_at',
        'duration_display',
    ]
    ordering = ['-started_at']
    
    fieldsets = (
        ('Sync Info', {
            'fields': ('id', 'provider', 'resource_type', 'status')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'duration_display')
        }),
        ('Statistics', {
            'fields': (
                'records_processed',
                'records_created',
                'records_updated',
                'records_failed',
            )
        }),
        ('Errors', {
            'fields': ('error_message', 'errors'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display sync duration in human-readable format."""
        duration = obj.duration
        if duration is None:
            return '-'
        
        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            return f"{duration/60:.1f}m"
        else:
            return f"{duration/3600:.1f}h"
    
    duration_display.short_description = 'Duration'