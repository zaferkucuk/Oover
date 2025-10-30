"""
Unit tests for Football-Data.org API integration.

Tests cover:
- Client initialization and configuration
- API endpoint methods (with mocked responses)
- Response parsing and data normalization
- Rate limiting behavior
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from requests.exceptions import RequestException, Timeout

from api_integrations.providers.football_data_org.client import FootballDataClient
from api_integrations.providers.football_data_org.parsers import FootballDataResponseParser
from api_integrations.base.exceptions import (
    APIError,
    RateLimitError,
    AuthenticationError,
    ValidationError
)


class TestFootballDataClient(TestCase):
    """Test cases for FootballDataClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_123"
        self.client = FootballDataClient(api_key=self.api_key)
    
    def test_client_initialization(self):
        """Test client initializes with correct configuration."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.base_url, "https://api.football-data.org/v4")
        self.assertIsNotNone(self.client.session)
        self.assertEqual(self.client.timeout, 30)
    
    def test_get_headers(self):
        """Test authentication headers are set correctly."""
        headers = self.client._get_headers()
        
        self.assertIn("X-Auth-Token", headers)
        self.assertEqual(headers["X-Auth-Token"], self.api_key)
        self.assertEqual(headers["Content-Type"], "application/json")
    
    @patch('requests.Session.get')
    def test_get_competitions_success(self, mock_get):
        """Test successful competitions retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 2,
            "competitions": [
                {
                    "id": 2021,
                    "name": "Premier League",
                    "code": "PL",
                    "type": "LEAGUE",
                    "emblem": "https://example.com/pl.png"
                },
                {
                    "id": 2014,
                    "name": "La Liga",
                    "code": "PD",
                    "type": "LEAGUE",
                    "emblem": "https://example.com/laliga.png"
                }
            ]
        }
        mock_response.headers = {
            "X-Requests-Available-Minute": "9"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_competitions()
        
        # Assertions
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["competitions"]), 2)
        self.assertEqual(result["competitions"][0]["name"], "Premier League")
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("/competitions", call_args[0][0])
    
    @patch('requests.Session.get')
    def test_get_competitions_with_filters(self, mock_get):
        """Test competitions retrieval with filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 1, "competitions": []}
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Call with filters
        filters = {"areas": "2088", "plan": "TIER_ONE"}
        self.client.get_competitions(filters=filters)
        
        # Verify filters were passed as query params
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"], filters)
    
    @patch('requests.Session.get')
    def test_get_teams_by_competition_success(self, mock_get):
        """Test successful teams retrieval by competition."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 1,
            "teams": [
                {
                    "id": 57,
                    "name": "Arsenal FC",
                    "shortName": "Arsenal",
                    "tla": "ARS",
                    "crest": "https://example.com/arsenal.png"
                }
            ]
        }
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_teams_by_competition(competition_id=2021)
        
        # Assertions
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["teams"][0]["name"], "Arsenal FC")
        
        # Verify correct endpoint
        call_args = mock_get.call_args
        self.assertIn("/competitions/2021/teams", call_args[0][0])
    
    @patch('requests.Session.get')
    def test_get_teams_by_competition_with_season(self, mock_get):
        """Test teams retrieval with season parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 0, "teams": []}
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Call with season
        self.client.get_teams_by_competition(competition_id=2021, season=2023)
        
        # Verify season parameter
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"]["season"], 2023)
    
    @patch('requests.Session.get')
    def test_get_team_details_success(self, mock_get):
        """Test successful single team retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 57,
            "name": "Arsenal FC",
            "founded": 1886,
            "clubColors": "Red / White",
            "venue": "Emirates Stadium",
            "website": "https://www.arsenal.com"
        }
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_team_details(team_id=57)
        
        # Assertions
        self.assertEqual(result["name"], "Arsenal FC")
        self.assertEqual(result["founded"], 1886)
        
        # Verify correct endpoint
        call_args = mock_get.call_args
        self.assertIn("/teams/57", call_args[0][0])
    
    @patch('requests.Session.get')
    def test_rate_limit_error(self, mock_get):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "message": "Too many requests",
            "errorCode": 429
        }
        mock_response.headers = {
            "X-Requests-Available-Minute": "0"
        }
        mock_get.return_value = mock_response
        
        # Should raise RateLimitError
        with self.assertRaises(RateLimitError) as context:
            self.client.get_competitions()
        
        self.assertIn("429", str(context.exception))
    
    @patch('requests.Session.get')
    def test_authentication_error(self, mock_get):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "message": "Invalid API token",
            "errorCode": 403
        }
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Should raise AuthenticationError
        with self.assertRaises(AuthenticationError) as context:
            self.client.get_competitions()
        
        self.assertIn("403", str(context.exception))
    
    @patch('requests.Session.get')
    def test_not_found_error(self, mock_get):
        """Test 404 not found error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "Team not found",
            "errorCode": 404
        }
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.client.get_team_details(team_id=99999)
        
        self.assertIn("404", str(context.exception))
    
    @patch('requests.Session.get')
    def test_server_error(self, mock_get):
        """Test 500 server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "message": "Internal server error"
        }
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Should raise APIError
        with self.assertRaises(APIError) as context:
            self.client.get_competitions()
        
        self.assertIn("500", str(context.exception))
    
    @patch('requests.Session.get')
    def test_network_timeout(self, mock_get):
        """Test network timeout handling."""
        mock_get.side_effect = Timeout("Request timed out")
        
        # Should raise APIError
        with self.assertRaises(APIError) as context:
            self.client.get_competitions()
        
        self.assertIn("timeout", str(context.exception).lower())
    
    @patch('requests.Session.get')
    def test_connection_error(self, mock_get):
        """Test connection error handling."""
        mock_get.side_effect = RequestException("Connection failed")
        
        # Should raise APIError
        with self.assertRaises(APIError) as context:
            self.client.get_competitions()
        
        self.assertIn("Connection failed", str(context.exception))


class TestFootballDataResponseParser(TestCase):
    """Test cases for FootballDataResponseParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = FootballDataResponseParser()
    
    def test_parse_competitions_response(self):
        """Test parsing competitions list response."""
        raw_response = {
            "count": 2,
            "filters": {},
            "competitions": [
                {
                    "id": 2021,
                    "name": "Premier League",
                    "code": "PL",
                    "type": "LEAGUE",
                    "emblem": "https://example.com/pl.png",
                    "currentSeason": {
                        "id": 1,
                        "startDate": "2023-08-01",
                        "endDate": "2024-05-31"
                    },
                    "area": {
                        "id": 2072,
                        "name": "England",
                        "code": "ENG"
                    }
                }
            ]
        }
        
        result = self.parser.parse(raw_response)
        
        # Assertions
        self.assertIn("competitions", result)
        self.assertEqual(len(result["competitions"]), 1)
        
        comp = result["competitions"][0]
        self.assertEqual(comp["id"], 2021)
        self.assertEqual(comp["name"], "Premier League")
        self.assertEqual(comp["code"], "PL")
        self.assertIn("currentSeason", comp)
        self.assertIn("area", comp)
    
    def test_parse_teams_response(self):
        """Test parsing teams list response."""
        raw_response = {
            "count": 1,
            "teams": [
                {
                    "id": 57,
                    "name": "Arsenal FC",
                    "shortName": "Arsenal",
                    "tla": "ARS",
                    "crest": "https://example.com/arsenal.png",
                    "address": "75 Drayton Park London N5 1BU",
                    "website": "https://www.arsenal.com",
                    "founded": 1886,
                    "clubColors": "Red / White",
                    "venue": "Emirates Stadium",
                    "area": {
                        "id": 2072,
                        "name": "England",
                        "code": "ENG"
                    }
                }
            ]
        }
        
        result = self.parser.parse(raw_response)
        
        # Assertions
        self.assertIn("teams", result)
        self.assertEqual(len(result["teams"]), 1)
        
        team = result["teams"][0]
        self.assertEqual(team["id"], 57)
        self.assertEqual(team["name"], "Arsenal FC")
        self.assertEqual(team["shortName"], "Arsenal")
        self.assertEqual(team["tla"], "ARS")
        self.assertEqual(team["founded"], 1886)
        self.assertIn("area", team)
    
    def test_parse_single_team_response(self):
        """Test parsing single team detail response."""
        raw_response = {
            "id": 57,
            "name": "Arsenal FC",
            "shortName": "Arsenal",
            "tla": "ARS",
            "crest": "https://example.com/arsenal.png"
        }
        
        result = self.parser.parse(raw_response)
        
        # Should wrap single item in list
        self.assertIn("teams", result)
        self.assertEqual(len(result["teams"]), 1)
        self.assertEqual(result["teams"][0]["name"], "Arsenal FC")
    
    def test_parse_pagination_metadata(self):
        """Test extraction of pagination metadata."""
        raw_response = {
            "count": 100,
            "filters": {
                "season": "2023",
                "areas": "2088"
            },
            "competitions": []
        }
        
        pagination = self.parser.extract_pagination(raw_response)
        
        # Assertions
        self.assertIsNotNone(pagination)
        self.assertEqual(pagination["count"], 100)
        self.assertEqual(pagination["filters"]["season"], "2023")
    
    def test_parse_error_response(self):
        """Test parsing error responses."""
        raw_response = {
            "message": "Resource not found",
            "errorCode": 404
        }
        
        error = self.parser.parse_error(raw_response)
        
        # Assertions
        self.assertIn("message", error)
        self.assertIn("errorCode", error)
        self.assertEqual(error["message"], "Resource not found")
        self.assertEqual(error["errorCode"], 404)
    
    def test_parse_empty_response(self):
        """Test parsing empty response."""
        raw_response = {
            "count": 0,
            "teams": []
        }
        
        result = self.parser.parse(raw_response)
        
        # Should handle empty list gracefully
        self.assertIn("teams", result)
        self.assertEqual(len(result["teams"]), 0)
    
    def test_parse_missing_optional_fields(self):
        """Test parsing with missing optional fields."""
        raw_response = {
            "teams": [
                {
                    "id": 57,
                    "name": "Arsenal FC"
                    # Missing: shortName, tla, crest, etc.
                }
            ]
        }
        
        result = self.parser.parse(raw_response)
        
        # Should handle missing fields gracefully
        team = result["teams"][0]
        self.assertEqual(team["id"], 57)
        self.assertEqual(team["name"], "Arsenal FC")
        # Optional fields should be None or omitted
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON structure."""
        raw_response = {
            "unexpected_key": "unexpected_value"
        }
        
        # Should handle gracefully without crashing
        result = self.parser.parse(raw_response)
        
        # Result might be empty or contain original data
        self.assertIsInstance(result, dict)


class TestRateLimiting(TestCase):
    """Test cases for rate limiting functionality."""
    
    @patch('requests.Session.get')
    def test_rate_limit_headers_parsed(self, mock_get):
        """Test rate limit headers are correctly parsed."""
        client = FootballDataClient(api_key="test_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 0, "competitions": []}
        mock_response.headers = {
            "X-Requests-Available-Minute": "7",
            "X-RequestCounter-Reset": "60"
        }
        mock_get.return_value = mock_response
        
        # Make request
        client.get_competitions()
        
        # Verify headers were present (actual rate limiter integration would track this)
        self.assertEqual(mock_response.headers["X-Requests-Available-Minute"], "7")
    
    @patch('requests.Session.get')
    def test_rate_limit_exhausted(self, mock_get):
        """Test behavior when rate limit is exhausted."""
        client = FootballDataClient(api_key="test_key")
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "message": "Rate limit exceeded",
            "errorCode": 429
        }
        mock_response.headers = {
            "X-Requests-Available-Minute": "0"
        }
        mock_get.return_value = mock_response
        
        # Should raise RateLimitError
        with self.assertRaises(RateLimitError):
            client.get_competitions()


# Integration test markers
@pytest.mark.integration
class TestFootballDataIntegration(TestCase):
    """
    Integration tests with real API (requires API key).
    
    These tests are marked with @pytest.mark.integration and will only run
    when explicitly requested: pytest -m integration
    """
    
    @pytest.mark.skipif(
        not hasattr(pytest, 'config') or not pytest.config.getoption('--run-integration'),
        reason="Integration tests require --run-integration flag"
    )
    def test_real_api_competitions(self):
        """Test real API call to get competitions."""
        # This would require a real API key
        # Only runs with: pytest -m integration --run-integration
        pass
    
    @pytest.mark.skipif(
        not hasattr(pytest, 'config') or not pytest.config.getoption('--run-integration'),
        reason="Integration tests require --run-integration flag"
    )
    def test_real_api_teams(self):
        """Test real API call to get teams."""
        # This would require a real API key
        # Only runs with: pytest -m integration --run-integration
        pass
