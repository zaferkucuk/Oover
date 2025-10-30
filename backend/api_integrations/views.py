"""
API Integration Views

DRF views for triggering API sync operations and managing team data fetching.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone

from .models import APISync
from .serializers import (
    APISyncSerializer,
    FetchTeamsSerializer,
    SyncTeamsSerializer,
)
from .services.teams_service import TeamsService

import logging

logger = logging.getLogger(__name__)

# Major European competitions (Football-Data.org codes)
EUROPEAN_COMPETITIONS = {
    'PL': 'Premier League',      # England
    'PD': 'La Liga',              # Spain
    'SA': 'Serie A',              # Italy
    'BL1': 'Bundesliga',          # Germany
    'FL1': 'Ligue 1',             # France
}


class APISyncViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing API sync operations and viewing sync history.
    
    Provides endpoints for:
    - Fetching teams from external APIs
    - Syncing existing team data
    - Viewing sync history and status
    """
    
    queryset = APISync.objects.all()
    serializer_class = APISyncSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def fetch_teams(self, request):
        """
        Trigger team fetch from external APIs.
        
        Supports three modes:
        1. Single league: {"league": "PL"}
        2. Country: {"country": "GB"}
        3. All European: {"all_european": true}
        
        Request Body:
            {
                "provider": "football-data",     # Optional, defaults to football-data
                "league": "PL",                   # Optional: League code
                "country": "GB",                  # Optional: Country code
                "all_european": false,            # Optional: Fetch all major European leagues
                "dry_run": false                  # Optional: Test without saving
            }
        
        Returns:
            {
                "success": true,
                "message": "Fetched 20 teams from Premier League",
                "statistics": {
                    "provider": "football-data",
                    "fetched": 20,
                    "transformed": 20,
                    "validated": 18,
                    "saved": 18,
                    "created": 5,
                    "updated": 13,
                    "failed": 2,
                    "errors": [...]
                }
            }
        """
        serializer = FetchTeamsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = request.data.get('provider', 'football-data')
        all_european = serializer.validated_data.get('all_european', False)
        league = serializer.validated_data.get('league')
        country = serializer.validated_data.get('country')
        dry_run = serializer.validated_data.get('dry_run', False)
        
        try:
            teams_service = TeamsService()
            
            # Mode 1: All European leagues
            if all_european:
                total_stats = {
                    'provider': provider,
                    'fetched': 0,
                    'transformed': 0,
                    'validated': 0,
                    'saved': 0,
                    'created': 0,
                    'updated': 0,
                    'failed': 0,
                    'errors': []
                }
                
                logger.info(f"Fetching teams from all European leagues")
                
                for league_code, league_name in EUROPEAN_COMPETITIONS.items():
                    try:
                        logger.info(f"Fetching {league_name} ({league_code})")
                        
                        stats = teams_service.fetch_teams_from_provider(
                            provider=provider,
                            competition_id=league_code
                        )
                        
                        # Aggregate statistics
                        total_stats['fetched'] += stats.get('fetched', 0)
                        total_stats['transformed'] += stats.get('transformed', 0)
                        total_stats['validated'] += stats.get('validated', 0)
                        total_stats['saved'] += stats.get('saved', 0)
                        total_stats['created'] += stats.get('created', 0)
                        total_stats['updated'] += stats.get('updated', 0)
                        total_stats['failed'] += stats.get('failed', 0)
                        total_stats['errors'].extend(stats.get('errors', []))
                        
                        logger.info(
                            f"{league_name}: {stats.get('saved', 0)} teams saved "
                            f"({stats.get('created', 0)} new, {stats.get('updated', 0)} updated)"
                        )
                        
                    except Exception as e:
                        error_msg = f"Error fetching {league_name}: {str(e)}"
                        total_stats['errors'].append(error_msg)
                        logger.error(error_msg)
                
                return Response({
                    'success': True,
                    'message': f"Fetched teams from {len(EUROPEAN_COMPETITIONS)} European leagues",
                    'statistics': total_stats
                })
            
            # Mode 2: Single league
            elif league:
                logger.info(f"Fetching teams from league: {league}")
                
                stats = teams_service.fetch_teams_from_provider(
                    provider=provider,
                    competition_id=league
                )
                
                league_name = EUROPEAN_COMPETITIONS.get(league, league)
                
                return Response({
                    'success': True,
                    'message': f"Fetched {stats.get('saved', 0)} teams from {league_name}",
                    'statistics': stats
                })
            
            # Mode 3: Country (not fully implemented yet)
            elif country:
                return Response(
                    {
                        'success': False,
                        'error': 'Country-based fetch not yet implemented. Use league or all_european instead.'
                    },
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
            
            else:
                return Response(
                    {
                        'success': False,
                        'error': 'Must provide league, country, or all_european'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f"Validation error: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.exception(f"Fetch operation failed: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f"Fetch operation failed: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def sync_teams(self, request):
        """
        Trigger team sync (update existing teams).
        
        Request Body:
            {
                "fields": ["market_value", "logo"],  # Optional: Specific fields to update
                "force": false                        # Optional: Force update even if recently updated
            }
        
        Returns:
            {
                "success": true,
                "message": "Synced 150 teams",
                "statistics": {...}
            }
        """
        serializer = SyncTeamsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Implement sync logic in Phase 5.4
        return Response(
            {
                'success': False,
                'error': 'sync_teams endpoint not yet implemented. Use fetch_teams for now.'
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get sync history and current status.
        
        Returns recent sync operations with statistics.
        
        Returns:
            [
                {
                    "id": "uuid",
                    "operation": "fetch_teams",
                    "provider": "football-data",
                    "status": "completed",
                    "started_at": "2025-10-30T10:00:00Z",
                    "completed_at": "2025-10-30T10:05:00Z",
                    "duration": "5 minutes",
                    "metadata": {...}
                }
            ]
        """
        recent_syncs = APISync.objects.all().order_by('-started_at')[:10]
        serializer = APISyncSerializer(recent_syncs, many=True)
        return Response(serializer.data)
