"""
API Integration Views

DRF views for triggering API sync operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import APISync
from .serializers import (
    APISyncSerializer,
    FetchTeamsSerializer,
    SyncTeamsSerializer,
)
import logging

logger = logging.getLogger(__name__)


class APISyncViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing API sync history."""
    
    queryset = APISync.objects.all()
    serializer_class = APISyncSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def fetch_teams(self, request):
        """Trigger team fetch from external APIs."""
        # TODO: Implement in Phase 7.2
        serializer = FetchTeamsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            {'message': 'fetch_teams endpoint not yet implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    @action(detail=False, methods=['post'])
    def sync_teams(self, request):
        """Trigger team sync (update existing teams)."""
        # TODO: Implement in Phase 7.2
        serializer = SyncTeamsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            {'message': 'sync_teams endpoint not yet implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get sync history and current status."""
        # TODO: Implement in Phase 7.2
        recent_syncs = APISync.objects.all()[:10]
        serializer = APISyncSerializer(recent_syncs, many=True)
        return Response(serializer.data)