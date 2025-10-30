"""
Response Parsers for Football-Data.org API

This module provides parsers for normalizing Football-Data.org API responses
into a common format that can be used across different API providers.

Author: Oover Team
Date: 2025-10-30
"""

import logging
from typing import Any, Dict, List, Optional

from api_integrations.base.response_parser import BaseResponseParser

logger = logging.getLogger('api_integrations')


class FootballDataResponseParser(BaseResponseParser):
    """
    Response parser for Football-Data.org API.
    
    Parses and normalizes Football-Data.org API responses into a common format
    that can be used across different API providers. This enables easy switching
    between providers without changing downstream code.
    
    Normalized Format:
        Competition: {
            'id': int,
            'name': str,
            'code': str,
            'type': str,  # 'LEAGUE', 'CUP'
            'emblem': str (URL),
            'currentSeason': {
                'id': int,
                'startDate': str (ISO date),
                'endDate': str (ISO date)
            },
            'area': {
                'id': int,
                'name': str,
                'code': str
            }
        }
        
        Team: {
            'id': int,
            'name': str,
            'shortName': str,
            'tla': str (3-letter code),
            'crest': str (URL),
            'address': str,
            'website': str,
            'founded': int,
            'clubColors': str,
            'venue': str
        }
    
    Example:
        >>> parser = FootballDataResponseParser()
        >>> response = requests.get('https://api.football-data.org/v4/competitions')
        >>> competitions = parser.parse(response)
        >>> for comp in competitions:
        ...     print(f"{comp['name']} ({comp['code']})")
    """
    
    def parse(self, response: Any) -> Any:
        """
        Parse the main response data.
        
        Football-Data.org API typically returns data in one of these formats:
        - Single item: Direct object
        - List of items: {'competitions': [...], 'count': N, 'filters': {...}}
        - List of items: {'teams': [...], 'count': N, 'filters': {...}}
        
        Args:
            response: Response object from requests library
            
        Returns:
            Parsed data (single item or list)
            
        Raises:
            ValueError: If response cannot be parsed
            
        Example:
            >>> response = client.get_competitions()
            >>> data = parser.parse(response)
            >>> # Returns list of normalized competition dicts
        """
        try:
            data = self.parse_json(response)
            
            # Check if this is an error response
            if self.is_error_response(data):
                error_msg = self.parse_error(data)
                logger.error(f"API error response: {error_msg}")
                raise ValueError(f"API error: {error_msg}")
            
            # Extract the main data (competitions, teams, or single item)
            if 'competitions' in data:
                logger.debug(f"Parsing {data.get('count', 0)} competitions")
                return self._parse_competitions(data['competitions'])
            elif 'teams' in data:
                logger.debug(f"Parsing {data.get('count', 0)} teams")
                return self._parse_teams(data['teams'])
            elif isinstance(data, dict) and ('id' in data or 'name' in data):
                # Single item (competition or team)
                if 'currentSeason' in data or 'area' in data:
                    logger.debug("Parsing single competition")
                    return self._parse_competition(data)
                else:
                    logger.debug("Parsing single team")
                    return self._parse_team(data)
            else:
                # Unknown format, return as-is
                logger.warning("Unknown response format, returning raw data")
                return data
                
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            raise ValueError(f"Failed to parse response: {str(e)}")
    
    def parse_error(self, data: Dict[str, Any]) -> str:
        """
        Parse error response.
        
        Football-Data.org error format:
        {
            'message': 'Error message',
            'errorCode': 400
        }
        
        Args:
            data: Response data dictionary
            
        Returns:
            Human-readable error message
            
        Example:
            >>> error_data = {'message': 'Competition not found', 'errorCode': 404}
            >>> parser.parse_error(error_data)
            'Competition not found (404)'
        """
        message = data.get('message', 'Unknown error')
        error_code = data.get('errorCode', '')
        
        if error_code:
            return f"{message} ({error_code})"
        return message
    
    def extract_pagination(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract pagination metadata.
        
        Football-Data.org uses a 'filters' object for pagination info:
        {
            'count': 20,
            'filters': {
                'season': '2023'
            }
        }
        
        Args:
            data: Response data dictionary
            
        Returns:
            Pagination metadata dict or None
            {
                'count': Total items in response,
                'filters': Active filters
            }
            
        Example:
            >>> data = {'competitions': [...], 'count': 20, 'filters': {'season': '2023'}}
            >>> parser.extract_pagination(data)
            {'count': 20, 'filters': {'season': '2023'}}
        """
        if not isinstance(data, dict):
            return None
        
        pagination = {}
        
        # Count of items in current response
        if 'count' in data:
            pagination['count'] = data['count']
        
        # Active filters
        if 'filters' in data:
            pagination['filters'] = data['filters']
        
        return pagination if pagination else None
    
    # ==================== Private Helper Methods ====================
    
    def _parse_competitions(self, competitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse a list of competitions."""
        return [self._parse_competition(comp) for comp in competitions]
    
    def _parse_competition(self, comp: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and normalize a single competition.
        
        Extracts essential fields and normalizes them to a common format.
        Missing fields are set to None instead of raising errors.
        """
        try:
            normalized = {
                'id': comp.get('id'),
                'name': comp.get('name'),
                'code': comp.get('code'),
                'type': comp.get('type'),  # 'LEAGUE', 'CUP'
                'emblem': comp.get('emblem'),
            }
            
            # Current season info (optional)
            if 'currentSeason' in comp:
                season = comp['currentSeason']
                normalized['currentSeason'] = {
                    'id': season.get('id'),
                    'startDate': season.get('startDate'),
                    'endDate': season.get('endDate'),
                }
            
            # Area/country info (optional)
            if 'area' in comp:
                area = comp['area']
                normalized['area'] = {
                    'id': area.get('id'),
                    'name': area.get('name'),
                    'code': area.get('code'),
                }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to parse competition: {str(e)}")
            logger.debug(f"Competition data: {comp}")
            raise
    
    def _parse_teams(self, teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse a list of teams."""
        return [self._parse_team(team) for team in teams]
    
    def _parse_team(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and normalize a single team.
        
        Extracts essential fields and normalizes them to a common format.
        Missing fields are set to None instead of raising errors.
        """
        try:
            normalized = {
                'id': team.get('id'),
                'name': team.get('name'),
                'shortName': team.get('shortName'),
                'tla': team.get('tla'),  # Three-Letter Abbreviation
                'crest': team.get('crest'),  # Team logo URL
                'address': team.get('address'),
                'website': team.get('website'),
                'founded': team.get('founded'),
                'clubColors': team.get('clubColors'),
                'venue': team.get('venue'),
            }
            
            # Area/country info (optional)
            if 'area' in team:
                area = team['area']
                normalized['area'] = {
                    'id': area.get('id'),
                    'name': area.get('name'),
                    'code': area.get('code'),
                }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to parse team: {str(e)}")
            logger.debug(f"Team data: {team}")
            raise
    
    def is_error_response(self, data: Dict[str, Any]) -> bool:
        """
        Check if response is an error.
        
        Football-Data.org error responses contain 'message' and 'errorCode'.
        """
        return isinstance(data, dict) and 'errorCode' in data
