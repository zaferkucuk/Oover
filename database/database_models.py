"""
Database Models for Oover (Sport Prediction App)

This module contains Pydantic models for all database tables and their relationships.
Use these models for data validation, serialization, and type hints in the Django backend.

Features:
- Full type safety with Pydantic v2
- Automatic validation
- Snake_case to camelCase conversion
- Relationship handling
- API response models

Version: 1.0.0
Date: 2025-10-27
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# ENUM DEFINITIONS
# ============================================================================

class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class MatchStatus(str, Enum):
    """Match status"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class PredictionOutcome(str, Enum):
    """Prediction outcome status"""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    VOID = "void"


# ============================================================================
# BASE CONFIGURATION
# ============================================================================

class BaseDBModel(BaseModel):
    """Base model with common configuration for all database models"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {}
        }
    )


# ============================================================================
# COUNTRY MODELS
# ============================================================================

class CountryBase(BaseDBModel):
    """Base Country model with common fields"""
    
    id: str = Field(..., description="Unique identifier (e.g., 'tr', 'gb', 'uefa')")
    name: str = Field(..., description="Full country name")
    code: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    flag: Optional[str] = Field(None, description="Country flag emoji or URL")
    is_international: bool = Field(False, alias="isInternational", description="True for international organizations")
    is_active: bool = Field(True, alias="isActive", description="Active status flag")


class Country(CountryBase):
    """Country model from database"""
    
    created_at: datetime = Field(..., alias="createdAt", description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt", description="Record update timestamp")


class CountryCreate(CountryBase):
    """Model for creating a new country"""
    pass


class CountryUpdate(BaseDBModel):
    """Model for updating a country (all fields optional)"""
    
    name: Optional[str] = None
    code: Optional[str] = None
    flag: Optional[str] = None
    is_international: Optional[bool] = Field(None, alias="isInternational")
    is_active: Optional[bool] = Field(None, alias="isActive")


class CountryWithRelations(Country):
    """Country with related leagues and teams"""
    
    leagues: Optional[List['League']] = None
    teams: Optional[List['Team']] = None


# ============================================================================
# SPORT MODELS
# ============================================================================

class SportBase(BaseDBModel):
    """Base Sport model"""
    
    id: str
    name: str
    is_active: bool = Field(True, alias="isActive")


class Sport(SportBase):
    """Sport model from database"""
    
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


# ============================================================================
# LEAGUE MODELS
# ============================================================================

class LeagueBase(BaseDBModel):
    """Base League model"""
    
    id: str
    name: str
    country_id: Optional[str] = Field(None, alias="countryId", description="Foreign key to countries table")
    season: Optional[str] = None
    logo: Optional[str] = None
    sport_id: Optional[str] = Field(None, alias="sportId")
    is_active: bool = Field(True, alias="isActive")


class League(LeagueBase):
    """League model from database"""
    
    country: Optional[str] = Field(None, deprecated=True, description="DEPRECATED: Use country_id instead")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class LeagueCreate(LeagueBase):
    """Model for creating a new league"""
    pass


class LeagueUpdate(BaseDBModel):
    """Model for updating a league"""
    
    name: Optional[str] = None
    country_id: Optional[str] = Field(None, alias="countryId")
    season: Optional[str] = None
    logo: Optional[str] = None
    sport_id: Optional[str] = Field(None, alias="sportId")
    is_active: Optional[bool] = Field(None, alias="isActive")


class LeagueWithRelations(League):
    """League with related country, sport, and matches"""
    
    country_obj: Optional[Country] = Field(None, alias="country")
    sport: Optional[Sport] = None
    matches: Optional[List['Match']] = None


# ============================================================================
# TEAM MODELS
# ============================================================================

class TeamBase(BaseDBModel):
    """Base Team model"""
    
    id: str
    name: str
    country_id: Optional[str] = Field(None, alias="countryId", description="Foreign key to countries table")
    logo: Optional[str] = None
    is_national: bool = Field(False, alias="isNational")
    is_active: bool = Field(True, alias="isActive")


class Team(TeamBase):
    """Team model from database"""
    
    country: Optional[str] = Field(None, deprecated=True, description="DEPRECATED: Use country_id instead")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class TeamCreate(TeamBase):
    """Model for creating a new team"""
    pass


class TeamUpdate(BaseDBModel):
    """Model for updating a team"""
    
    name: Optional[str] = None
    country_id: Optional[str] = Field(None, alias="countryId")
    logo: Optional[str] = None
    is_national: Optional[bool] = Field(None, alias="isNational")
    is_active: Optional[bool] = Field(None, alias="isActive")


class TeamWithRelations(Team):
    """Team with related country and matches"""
    
    country_obj: Optional[Country] = Field(None, alias="country")
    home_matches: Optional[List['Match']] = Field(None, alias="homeMatches")
    away_matches: Optional[List['Match']] = Field(None, alias="awayMatches")


# ============================================================================
# MATCH MODELS
# ============================================================================

class MatchBase(BaseDBModel):
    """Base Match model"""
    
    id: str
    league_id: Optional[str] = Field(None, alias="leagueId")
    home_team_id: Optional[str] = Field(None, alias="homeTeamId")
    away_team_id: Optional[str] = Field(None, alias="awayTeamId")
    match_date: str = Field(..., alias="matchDate", description="Match date in ISO format")
    match_time: Optional[str] = Field(None, alias="matchTime")
    home_score: Optional[int] = Field(None, alias="homeScore")
    away_score: Optional[int] = Field(None, alias="awayScore")
    status: MatchStatus = MatchStatus.SCHEDULED
    venue: Optional[str] = None
    is_active: bool = Field(True, alias="isActive")


class Match(MatchBase):
    """Match model from database"""
    
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class MatchCreate(MatchBase):
    """Model for creating a new match"""
    pass


class MatchUpdate(BaseDBModel):
    """Model for updating a match"""
    
    league_id: Optional[str] = Field(None, alias="leagueId")
    home_team_id: Optional[str] = Field(None, alias="homeTeamId")
    away_team_id: Optional[str] = Field(None, alias="awayTeamId")
    match_date: Optional[str] = Field(None, alias="matchDate")
    match_time: Optional[str] = Field(None, alias="matchTime")
    home_score: Optional[int] = Field(None, alias="homeScore")
    away_score: Optional[int] = Field(None, alias="awayScore")
    status: Optional[MatchStatus] = None
    venue: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="isActive")


class MatchWithRelations(Match):
    """Match with related league, teams, and predictions"""
    
    league: Optional[LeagueWithRelations] = None
    home_team: Optional[TeamWithRelations] = Field(None, alias="homeTeam")
    away_team: Optional[TeamWithRelations] = Field(None, alias="awayTeam")
    predictions: Optional[List['Prediction']] = None


# ============================================================================
# USER MODELS
# ============================================================================

class UserBase(BaseDBModel):
    """Base User model"""
    
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = Field(None, alias="fullName")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    role: UserRole = UserRole.USER
    is_active: bool = Field(True, alias="isActive")


class User(UserBase):
    """User model from database"""
    
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class UserUpdate(BaseDBModel):
    """Model for updating a user"""
    
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = Field(None, alias="fullName")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    role: Optional[UserRole] = None
    is_active: Optional[bool] = Field(None, alias="isActive")


# ============================================================================
# PREDICTION MODELS
# ============================================================================

class PredictionBase(BaseDBModel):
    """Base Prediction model"""
    
    id: str
    user_id: Optional[str] = Field(None, alias="userId")
    match_id: Optional[str] = Field(None, alias="matchId")
    predicted_home_score: Optional[int] = Field(None, alias="predictedHomeScore")
    predicted_away_score: Optional[int] = Field(None, alias="predictedAwayScore")
    confidence: Optional[int] = Field(None, ge=0, le=100, description="Confidence level (0-100)")
    outcome: PredictionOutcome = PredictionOutcome.PENDING
    points_earned: Optional[int] = Field(None, alias="pointsEarned")


class Prediction(PredictionBase):
    """Prediction model from database"""
    
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class PredictionCreate(PredictionBase):
    """Model for creating a new prediction"""
    pass


class PredictionUpdate(BaseDBModel):
    """Model for updating a prediction"""
    
    predicted_home_score: Optional[int] = Field(None, alias="predictedHomeScore")
    predicted_away_score: Optional[int] = Field(None, alias="predictedAwayScore")
    confidence: Optional[int] = Field(None, ge=0, le=100, alias="confidence")
    outcome: Optional[PredictionOutcome] = None
    points_earned: Optional[int] = Field(None, alias="pointsEarned")


class PredictionWithRelations(Prediction):
    """Prediction with related user and match"""
    
    user: Optional[User] = None
    match: Optional[MatchWithRelations] = None


# ============================================================================
# FILTER MODELS
# ============================================================================

class CountryFilter(BaseDBModel):
    """Filter options for country queries"""
    
    is_active: Optional[bool] = Field(None, alias="isActive")
    is_international: Optional[bool] = Field(None, alias="isInternational")
    code: Optional[str] = None
    name: Optional[str] = None


class LeagueFilter(BaseDBModel):
    """Filter options for league queries"""
    
    is_active: Optional[bool] = Field(None, alias="isActive")
    country_id: Optional[str] = Field(None, alias="countryId")
    sport_id: Optional[str] = Field(None, alias="sportId")
    season: Optional[str] = None


class TeamFilter(BaseDBModel):
    """Filter options for team queries"""
    
    is_active: Optional[bool] = Field(None, alias="isActive")
    country_id: Optional[str] = Field(None, alias="countryId")
    is_national: Optional[bool] = Field(None, alias="isNational")


class MatchFilter(BaseDBModel):
    """Filter options for match queries"""
    
    status: Optional[MatchStatus] = None
    league_id: Optional[str] = Field(None, alias="leagueId")
    home_team_id: Optional[str] = Field(None, alias="homeTeamId")
    away_team_id: Optional[str] = Field(None, alias="awayTeamId")
    date_from: Optional[str] = Field(None, alias="dateFrom")
    date_to: Optional[str] = Field(None, alias="dateTo")


class PredictionFilter(BaseDBModel):
    """Filter options for prediction queries"""
    
    user_id: Optional[str] = Field(None, alias="userId")
    match_id: Optional[str] = Field(None, alias="matchId")
    outcome: Optional[PredictionOutcome] = None


# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class ApiResponse(BaseDBModel):
    """Generic API response wrapper"""
    
    data: Optional[dict] = None
    error: Optional[str] = None
    count: Optional[int] = None


class PaginatedResponse(BaseDBModel):
    """Paginated API response"""
    
    data: List[dict]
    error: Optional[str] = None
    count: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    total_pages: int = Field(..., alias="totalPages")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Creating a country

>>> from database_models import CountryCreate
>>> 
>>> new_country = CountryCreate(
...     id="nl",
...     name="Netherlands",
...     code="NL",
...     flag="🇳🇱",
...     is_active=True
... )
>>> 
>>> # Insert into database
>>> supabase.table('countries').insert(new_country.model_dump()).execute()


Example 2: Validating and updating a country

>>> from database_models import CountryUpdate
>>> 
>>> update_data = CountryUpdate(
...     flag="🇹🇷",
...     is_active=True
... )
>>> 
>>> # Only non-None fields will be updated
>>> supabase.table('countries').update(update_data.model_dump(exclude_none=True)).eq('id', 'tr').execute()


Example 3: Fetching and parsing country data

>>> from database_models import Country
>>> 
>>> response = supabase.table('countries').select('*').eq('id', 'tr').execute()
>>> country = Country(**response.data[0])
>>> 
>>> print(f"Country: {country.name} {country.flag}")


Example 4: Working with relationships

>>> from database_models import CountryWithRelations
>>> 
>>> response = supabase.table('countries').select('*, leagues(*), teams(*)').eq('id', 'tr').execute()
>>> country_with_relations = CountryWithRelations(**response.data[0])
>>> 
>>> print(f"Leagues: {len(country_with_relations.leagues or [])}")
>>> print(f"Teams: {len(country_with_relations.teams or [])}")


Example 5: Filtering matches by country

>>> from database_models import MatchWithRelations, MatchFilter
>>> 
>>> match_filter = MatchFilter(
...     status=MatchStatus.SCHEDULED,
...     date_from="2025-10-27"
... )
>>> 
>>> response = supabase.table('matches').select('''
...     *,
...     league:leagues(
...         *,
...         country:countries(*)
...     ),
...     home_team:teams(*),
...     away_team:teams(*)
... ''').eq('league.country.code', 'TR').execute()
>>> 
>>> matches = [MatchWithRelations(**match) for match in response.data]


Example 6: Creating a prediction

>>> from database_models import PredictionCreate
>>> 
>>> new_prediction = PredictionCreate(
...     id="pred_123",
...     user_id="user_456",
...     match_id="match_789",
...     predicted_home_score=2,
...     predicted_away_score=1,
...     confidence=75
... )
>>> 
>>> supabase.table('predictions').insert(new_prediction.model_dump()).execute()


Example 7: Using filters

>>> from database_models import LeagueFilter
>>> 
>>> league_filter = LeagueFilter(
...     is_active=True,
...     country_id="tr",
...     season="2024-2025"
... )
>>> 
>>> # Build query dynamically based on filter
>>> query = supabase.table('leagues').select('*')
>>> filter_dict = league_filter.model_dump(exclude_none=True)
>>> for key, value in filter_dict.items():
...     query = query.eq(key, value)
>>> response = query.execute()


Example 8: Handling API responses

>>> from database_models import ApiResponse, PaginatedResponse
>>> 
>>> # Simple response
>>> response = ApiResponse(
...     data={"id": "tr", "name": "Turkey"},
...     error=None,
...     count=1
... )
>>> 
>>> # Paginated response
>>> paginated = PaginatedResponse(
...     data=[{"id": "tr"}, {"id": "gb"}],
...     count=2,
...     page=1,
...     page_size=10,
...     total_pages=1
... )
"""


# Update forward references for recursive models
CountryWithRelations.model_rebuild()
LeagueWithRelations.model_rebuild()
TeamWithRelations.model_rebuild()
MatchWithRelations.model_rebuild()
PredictionWithRelations.model_rebuild()


# Export all models
__all__ = [
    # Enums
    'UserRole',
    'MatchStatus',
    'PredictionOutcome',
    
    # Country models
    'Country',
    'CountryCreate',
    'CountryUpdate',
    'CountryWithRelations',
    
    # Sport models
    'Sport',
    
    # League models
    'League',
    'LeagueCreate',
    'LeagueUpdate',
    'LeagueWithRelations',
    
    # Team models
    'Team',
    'TeamCreate',
    'TeamUpdate',
    'TeamWithRelations',
    
    # Match models
    'Match',
    'MatchCreate',
    'MatchUpdate',
    'MatchWithRelations',
    
    # User models
    'User',
    'UserCreate',
    'UserUpdate',
    
    # Prediction models
    'Prediction',
    'PredictionCreate',
    'PredictionUpdate',
    'PredictionWithRelations',
    
    # Filter models
    'CountryFilter',
    'LeagueFilter',
    'TeamFilter',
    'MatchFilter',
    'PredictionFilter',
    
    # Response models
    'ApiResponse',
    'PaginatedResponse',
]
