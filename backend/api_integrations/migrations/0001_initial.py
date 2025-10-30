"""
Initial migration for api_integrations app.

Creates APISync model for tracking API sync operations.
"""

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    """Initial migration for API integrations."""
    
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='APISync',
            fields=[
                # Primary Key
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                
                # Sync Info
                ('provider', models.CharField(
                    choices=[
                        ('football_data_org', 'Football-Data.org'),
                        ('api_football', 'API-Football')
                    ],
                    help_text='API provider used for this sync',
                    max_length=50
                )),
                ('resource_type', models.CharField(
                    choices=[
                        ('teams', 'Teams'),
                        ('team_stats', 'Team Stats'),
                        ('matches', 'Matches')
                    ],
                    help_text='Type of resource being synced',
                    max_length=50
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('failed', 'Failed')
                    ],
                    default='pending',
                    help_text='Current status of sync operation',
                    max_length=20
                )),
                
                # Timestamps
                ('started_at', models.DateTimeField(
                    default=django.utils.timezone.now,
                    help_text='When sync operation started'
                )),
                ('completed_at', models.DateTimeField(
                    blank=True,
                    help_text='When sync operation completed',
                    null=True
                )),
                
                # Statistics
                ('records_processed', models.IntegerField(
                    default=0,
                    help_text='Number of records processed'
                )),
                ('records_created', models.IntegerField(
                    default=0,
                    help_text='Number of new records created'
                )),
                ('records_updated', models.IntegerField(
                    default=0,
                    help_text='Number of existing records updated'
                )),
                ('records_failed', models.IntegerField(
                    default=0,
                    help_text='Number of records that failed to process'
                )),
                
                # Error Tracking
                ('errors', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='List of errors encountered during sync'
                )),
                ('error_message', models.TextField(
                    blank=True,
                    help_text='Primary error message if sync failed'
                )),
                
                # Metadata
                ('metadata', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Additional metadata about the sync operation'
                )),
            ],
            options={
                'db_table': 'api_sync',
                'ordering': ['-started_at'],
                'verbose_name': 'API Sync',
                'verbose_name_plural': 'API Syncs',
            },
        ),
        
        # Add indexes for better query performance
        migrations.AddIndex(
            model_name='apisync',
            index=models.Index(
                fields=['provider', 'resource_type'],
                name='api_sync_pr_res_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='apisync',
            index=models.Index(
                fields=['status'],
                name='api_sync_status_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='apisync',
            index=models.Index(
                fields=['-started_at'],
                name='api_sync_started_idx'
            ),
        ),
    ]
