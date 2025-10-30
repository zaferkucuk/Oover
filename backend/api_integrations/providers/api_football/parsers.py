"""
Response parsers for API-Football API.

This module provides parsers to transform API-Football API responses
into normalized formats compatible with our application's data models.
Maps API-Football format to Football-Data.org format for consistency.
"""

import logging
from typing import Any, Dict, List, Optional

from api_integrations.base.response_parser import BaseResponseParser

logger = logging.getLogger(__name__)


class APIFootballResponseParser(BaseResponseParser):
    """
    Parser for API-Football API responses.
    
    Transforms API-Football responses into normalized format that matches
    Football-Data.org structure for consistency across providers.
    
    API-Football Response Structure:
    {
        "get": "teams",
        "parameters": {...},
        "errors": [],
        "results": 20,
        "paging": {"current": 1, "total": 1},
        "response": [...]
    }
    
    Example:
        parser = APIFootballResponseParser()
        
        # Parse teams response
        teams_data = parser.parse(response)
        # Returns: [
        #     {
        #         "id": 33,
        #         "name": "Manchester United",
        #         "shortName": "Man United",
        #         "tla": "MUN",
        #         "crest": "https://...",
        #         "address": "Sir Matt Busby Way",
        #         "website": None,
        #         "founded": 1878,
        #         "clubColors": None,
        #         "venue": {
        #             "name": "Old Trafford",
        #             "city": "Manchester",
        #             "capacity": 76212
        #         },
        #         "area": {
        #             "name": "England",
        #             "code": "GB"
        #         }
        #     }
        # ]
        
        # Parse leagues response
        leagues_data = parser.parse(response)
        # Returns: [
        #     {
        #         "id": 39,
        #         "name": "Premier League",
        #         "code": "PL",
        #         "type": "League",
        #         "emblem": "https://...",
        #         "currentSeason": {
        #             "id": 20746,
        #             "startDate": "2023-08-11",
        #             "endDate": "2024-05-19",
        #             "currentMatchday": None
        #         },
        #         "area": {
        #             "id": None,
        #             "name": "England",
        #             "code": "GB",
        #             "flag": "https://..."
        #         }
        #     }
        # ]
    """
    
    def parse(self, response: Any) -> List[Dict[str, Any]]:
        """
        Parse API-Football response into normalized format.
        
        Detects the type of response (leagues or teams) and applies
        appropriate parsing logic. Returns empty list on error.
        
        Args:
            response: API-Football response object (requests.Response or dict)
            
        Returns:
            List of normalized data dictionaries
            
        Raises:
            ValueError: If response parsing fails
        """
        try:
            data = self.parse_json(response)
            
            # Check for errors in response
            if self.is_error_response(data):
                error_msg = self.parse_error(data)
                logger.error(f"API-Football error response: {error_msg}")
                return []
            
            # Extract response data
            response_data = self.extract_list(data, "response", [])
            
            if not response_data:
                logger.warning("Empty response from API-Football")
                return []
            
            # Detect response type and parse accordingly
            first_item = response_data[0]
            
            if "league" in first_item:
                # This is a leagues response
                return self._parse_leagues_response(response_data)
            elif "team" in first_item:
                # This is a teams response
                return self._parse_teams_response(response_data)
            else:
                logger.warning(f"Unknown response type: {first_item.keys()}")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing API-Football response: {str(e)}")
            raise ValueError(f"Failed to parse API-Football response: {str(e)}")
    
    def parse_error(self, response: Any) -> str:
        """
        Parse error information from API-Football response.
        
        API-Football errors structure:
        {
            "errors": [
                "message 1",
                "message 2"
            ]
        }
        
        Args:
            response: API-Football response object or parsed dict
            
        Returns:
            Error message string
        """
        try:
            data = self.parse_json(response)
            errors = self.extract_list(data, "errors", [])
            
            if errors:
                # Join multiple error messages
                return "; ".join(str(error) for error in errors)
            
            # Fallback to generic error message
            return "Unknown API-Football error"
            
        except Exception as e:
            logger.error(f"Error parsing API-Football error response: {str(e)}")
            return f"Error parsing error response: {str(e)}"
    
    def extract_pagination(self, response: Any) -> Dict[str, Any]:
        """
        Extract pagination metadata from API-Football response.
        
        API-Football pagination structure:
        {
            "results": 20,
            "paging": {
                "current": 1,
                "total": 1
            }
        }
        
        Args:
            response: API-Football response object or parsed dict
            
        Returns:
            Dictionary with pagination info:
            {
                "count": 20,
                "current_page": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        """
        try:
            data = self.parse_json(response)
            
            results = self.extract_data(data, "results", 0)
            paging = self.extract_data(data, "paging", {})
            
            current_page = self.extract_data(paging, "current", 1)
            total_pages = self.extract_data(paging, "total", 1)
            
            return {
                "count": results,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_next": current_page < total_pages,
                "has_previous": current_page > 1,
            }
            
        except Exception as e:
            logger.error(f"Error extracting pagination: {str(e)}")
            return {
                "count": 0,
                "current_page": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            }
    
    def _parse_leagues_response(self, response_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse leagues response to normalized format (Football-Data compatible).
        
        Args:
            response_data: List of league objects from API-Football response
            
        Returns:
            List of normalized league dictionaries
        """
        normalized_leagues = []
        
        for item in response_data:
            try:
                league_data = self.extract_data(item, "league", {})
                country_data = self.extract_data(item, "country", {})
                seasons = self.extract_list(item, "seasons", [])
                
                # Find current season
                current_season = next(
                    (s for s in seasons if self.extract_data(s, "current", False)),
                    seasons[0] if seasons else {}
                )
                
                normalized_league = {
                    "id": self.extract_data(league_data, "id"),
                    "name": self.extract_data(league_data, "name"),
                    "code": self._generate_league_code(
                        self.extract_data(league_data, "name")
                    ),
                    "type": self.extract_data(league_data, "type"),
                    "emblem": self.extract_data(league_data, "logo"),
                    "currentSeason": {
                        "id": self.extract_data(current_season, "year"),
                        "startDate": self.extract_data(current_season, "start"),
                        "endDate": self.extract_data(current_season, "end"),
                        "currentMatchday": None,  # API-Football doesn't provide this
                    } if current_season else None,
                    "area": {
                        "id": None,  # API-Football doesn't provide area ID
                        "name": self.extract_data(country_data, "name"),
                        "code": self.extract_data(country_data, "code"),
                        "flag": self.extract_data(country_data, "flag"),
                    }
                }
                
                normalized_leagues.append(normalized_league)
                
            except Exception as e:
                logger.error(f"Error parsing league item: {str(e)}")
                continue
        
        return normalized_leagues
    
    def _parse_teams_response(self, response_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse teams response to normalized format (Football-Data compatible).
        
        Args:
            response_data: List of team objects from API-Football response
            
        Returns:
            List of normalized team dictionaries
        """
        normalized_teams = []
        
        for item in response_data:
            try:
                team_data = self.extract_data(item, "team", {})
                venue_data = self.extract_data(item, "venue", {})
                
                normalized_team = {
                    "id": self.extract_data(team_data, "id"),
                    "name": self.extract_data(team_data, "name"),
                    "shortName": self.extract_data(team_data, "name"),  # API-Football doesn't have shortName
                    "tla": self.extract_data(team_data, "code"),
                    "crest": self.extract_data(team_data, "logo"),
                    "address": self.extract_data(venue_data, "address"),
                    "website": None,  # API-Football doesn't provide website
                    "founded": self.extract_data(team_data, "founded"),
                    "clubColors": None,  # API-Football doesn't provide club colors
                    "venue": {
                        "name": self.extract_data(venue_data, "name"),
                        "city": self.extract_data(venue_data, "city"),
                        "capacity": self.extract_data(venue_data, "capacity"),
                    } if venue_data else None,
                    "area": {
                        "name": self.extract_data(team_data, "country"),
                        "code": None,  # API-Football doesn't provide country code in team response
                    }
                }
                
                normalized_teams.append(normalized_team)
                
            except Exception as e:
                logger.error(f"Error parsing team item: {str(e)}")
                continue
        
        return normalized_teams
    
    def _generate_league_code(self, league_name: str) -> str:
        """
        Generate a league code from league name.
        
        API-Football doesn't provide league codes, so we generate them
        from the league name (e.g., "Premier League" → "PL").
        
        Args:
            league_name: Full league name
            
        Returns:
            Generated league code (uppercase)
        """
        if not league_name:
            return "UNK"
        
        # Take first letter of each word
        words = league_name.split()
        code = "".join(word[0] for word in words if word)
        
        # Limit to 3 characters and uppercase
        return code[:3].upper()
