"""
Django Models for Core App

This module contains core Django models that map to existing Supabase tables.
All models use managed=False since tables are managed in Supabase.

IMPORTANT: Column names use snake_case to match PostgreSQL/Supabase convention.
          Foreign keys use db_column to map Python names to database columns.

Author: Oover Development Team
Date: November 2025
Last Updated: 2025-11-01 (Added Match, Standing, MatchEvent models)
"""

import uuid
from django.db import models
from django.utils import timezone


class Country(models.Model):
    """
    Country model - maps to 'countries' table in Supabase
    
    Represents countries where football leagues and teams exist.
    Includes both national countries and international entities (e.g., UEFA, World).
    
    Database Table: countries
    Primary Key: id (UUID)
    
    Schema Updates (Nov 2025):
    - Added: region (geographic region)
    - Added: fifa_code (FIFA country code)
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields (UUID)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="UUID primary key (auto-generated)"
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Full country name (e.g., 'England', 'Spain', 'World')"
    )
    
    code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        unique=True,
        help_text="ISO 3166-1 alpha-2 country code (e.g., 'GB', 'ES', 'WORLD')"
    )
    
    # NEW: Geographic and FIFA information
    region = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Geographic region (e.g., 'Western Europe', 'South America', 'Asia')"
    )
    
    fifa_code = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        unique=True,
        help_text="FIFA country code - 3 letters (e.g., 'ENG', 'ESP', 'BRA')"
    )
    
    flag = models.TextField(
        null=True,
        blank=True,
        help_text="Flag emoji (e.g., '🏴󠁧󠁢󠁥󠁮󠁧󠁿', '🇪🇸')"
    )
    
    flag_url = models.TextField(
        null=True,
        blank=True,
        help_text="Flag image URL from flagcdn.com for UI rendering"
    )
    
    # Status Fields
    is_international = models.BooleanField(
        default=False,
        help_text="True for international competitions (UEFA, World Cup, etc.)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="False to hide country from active lists"
    )
    
    # Timestamp Fields
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'countries'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']
        
    def __str__(self):
        """String representation of the country"""
        emoji = self.flag if self.flag else ''
        return f"{emoji} {self.name}".strip()
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Country: {self.id} - {self.name}>"


class Sport(models.Model):
    """
    Sport model - maps to 'sports' table in Supabase
    
    Represents different sports (Football, Basketball, etc.)
    Currently focused on Football.
    
    Database Table: sports
    Primary Key: id (text)
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.TextField(
        primary_key=True,
        help_text="Unique sport identifier (text UUID)"
    )
    
    name = models.TextField(
        help_text="Sport name (e.g., 'Football', 'Basketball')"
    )
    
    slug = models.TextField(
        help_text="URL-friendly identifier (e.g., 'football', 'basketball')"
    )
    
    icon = models.TextField(
        null=True,
        blank=True,
        help_text="Sport icon emoji or class name"
    )
    
    # Display & Status Fields
    is_active = models.BooleanField(
        default=True,
        db_column='isActive',  # Maps to Supabase camelCase column
        help_text="False to hide sport from active lists"
    )
    
    display_order = models.IntegerField(
        default=0,
        db_column='displayOrder',  # Maps to Supabase camelCase column
        help_text="Sort order for display (lower numbers first)"
    )
    
    # Timestamp Fields
    created_at = models.DateTimeField(
        default=timezone.now,
        db_column='createdAt',  # Maps to Supabase camelCase column
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='updatedAt',  # Maps to Supabase camelCase column
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'sports'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Sport'
        verbose_name_plural = 'Sports'
        ordering = ['display_order', 'name']
        
    def __str__(self):
        """String representation of the sport"""
        return self.name
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Sport: {self.id} - {self.name}>"


class League(models.Model):
    """
    League model - maps to 'leagues' table in Supabase
    
    Represents football leagues/competitions across different countries.
    Uses snake_case column names to match PostgreSQL/Supabase convention.
    
    Database Table: leagues
    Primary Key: id (UUID)
    Foreign Keys: sport_id (Sport), country_id (Country UUID)
    
    Schema Updates (Nov 2025):
    - Added: tier (league tier/division level)
    - Added: confederation (UEFA, CONMEBOL, etc.)
    
    Note: Season information is NOT stored here. It will be in a separate
          'league_seasons' table in the future to avoid data duplication.
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields (UUID)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="UUID primary key (auto-generated)"
    )
    
    name = models.TextField(
        help_text="League name (e.g., 'Premier League', 'La Liga', 'Serie A')"
    )
    
    # Foreign Keys (snake_case in database)
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        db_column='sport_id',
        related_name='leagues',
        help_text="Sport type (typically Football)"
    )
    
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        db_column='country_id',
        related_name='leagues',
        null=True,
        blank=True,
        help_text="Country where league operates (NULL for multi-country leagues)"
    )
    
    # NEW: League tier and confederation
    tier = models.IntegerField(
        null=True,
        blank=True,
        help_text="League tier/division (1=top tier, 2=second division, etc.)"
    )
    
    confederation = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Football confederation (e.g., 'UEFA', 'CONMEBOL', 'CONCACAF', 'AFC', 'CAF', 'OFC')"
    )
    
    # Additional Fields (snake_case)
    logo = models.TextField(
        null=True,
        blank=True,
        help_text="League logo URL"
    )
    
    external_id = models.TextField(
        null=True,
        blank=True,
        help_text="External API identifier (e.g., 'api-football-39' for Premier League)"
    )
    
    # Status Field (snake_case)
    is_active = models.BooleanField(
        default=True,
        help_text="False to hide league from active lists"
    )
    
    # Timestamp Fields (snake_case)
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'leagues'
        managed = False  # Table is managed in Supabase
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'
        ordering = ['name']
        
    def __str__(self):
        """String representation of the league"""
        if self.country:
            tier_info = f" (Tier {self.tier})" if self.tier else ""
            return f"{self.name} ({self.country.name}){tier_info}"
        return self.name
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<League: {self.id} - {self.name}>"


class Team(models.Model):
    """
    Team model - maps to 'teams' table in Supabase
    
    Represents football teams/clubs.
    Uses snake_case column names to match PostgreSQL/Supabase convention.
    
    Database Table: teams
    Primary Key: id (text)
    Foreign Keys: country_id (Country UUID)
    
    Schema Changes (Nov 2025):
    - Added: stadium_name (home stadium)
    - Added: stadium_capacity (stadium capacity)
    - Added: primary_color (hex color code)
    - Added: secondary_color (hex color code)
    
    Schema Changes (Oct 2025):
    - Removed: league_id (no direct league relationship)
    - Removed: shortName, venue, country (text)
    - Added: code (3-letter team code)
    - Added: website (official website URL)
    - Added: market_value (team market value in EUR)
    - Added: is_active (status flag)
    - Changed: All camelCase fields to snake_case
    
    Timestamp Fields:
    - created_at: Auto-populated by Supabase (DEFAULT CURRENT_TIMESTAMP)
    - updated_at: REQUIRED (NOT NULL in Supabase, must be set by application)
    
    Note: Teams no longer have a direct league_id relationship.
          League membership is tracked through matches and seasons.
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.TextField(
        primary_key=True,
        help_text="Unique team identifier (text UUID)"
    )
    
    code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="3-letter team code (e.g., 'MUN', 'BAR', 'FNB') for compact display"
    )
    
    name = models.TextField(
        help_text="Full team name (e.g., 'Manchester United', 'FC Barcelona', 'Fenerbahçe')"
    )
    
    # Foreign Key (snake_case)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        db_column='country_id',
        related_name='teams',
        null=True,
        blank=True,
        help_text="Team's home country"
    )
    
    # Branding & Info Fields
    logo = models.TextField(
        null=True,
        blank=True,
        help_text="Team logo URL"
    )
    
    founded = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year team was founded"
    )
    
    website = models.TextField(
        null=True,
        blank=True,
        help_text="Official team website URL"
    )
    
    market_value = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Team market value in EUR (e.g., 1000000000 for €1 billion)"
    )
    
    # NEW: Stadium information
    stadium_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Home stadium name (e.g., 'Old Trafford', 'Camp Nou', 'Şükrü Saracoğlu')"
    )
    
    stadium_capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Stadium seating capacity (e.g., 75000 for Old Trafford)"
    )
    
    # NEW: Team colors (hex codes)
    primary_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Primary team color in hex format (e.g., '#DA291C' for Manchester United red)"
    )
    
    secondary_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Secondary team color in hex format (e.g., '#FBE122' for Manchester United gold)"
    )
    
    # External Reference
    external_id = models.TextField(
        null=True,
        blank=True,
        help_text="External API identifier (e.g., 'api-football-33' for Manchester United)"
    )
    
    # Status Field
    is_active = models.BooleanField(
        default=True,
        help_text="False to hide team from active lists (e.g., dissolved teams)"
    )
    
    # Timestamp Fields (snake_case)
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp (auto-populated by Supabase)"
    )
    
    updated_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record last update timestamp (REQUIRED: NOT NULL in Supabase, must always be set)"
    )
    
    class Meta:
        db_table = 'teams'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['name']
        indexes = [
            models.Index(fields=['country'], name='idx_teams_country'),
            models.Index(fields=['code'], name='idx_teams_code'),
            models.Index(fields=['is_active'], name='idx_teams_is_active'),
            models.Index(fields=['external_id'], name='idx_teams_external_id'),
        ]
        
    def __str__(self):
        """String representation of the team"""
        if self.code:
            return f"{self.name} ({self.code})"
        return self.name
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Team: {self.id} - {self.name}>"
    
    @property
    def formatted_market_value(self):
        """
        Returns formatted market value for display
        
        Examples:
            1000000 -> "€1.0M"
            1500000000 -> "€1.5B"
            None -> "N/A"
        """
        if not self.market_value:
            return "N/A"
        
        value = self.market_value
        if value >= 1_000_000_000:
            return f"€{value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"€{value / 1_000_000:.1f}M"
        else:
            return f"€{value:,}"


class Match(models.Model):
    """
    Match model - maps to 'matches' table in Supabase
    
    Represents individual football matches with full details.
    Tracks match status, scores, timing, and relationships.
    
    Database Table: matches
    Primary Key: id (UUID)
    Foreign Keys: league_id, home_team_id, away_team_id, winner_id
    
    Match Status Values:
    - 'scheduled' = Not started yet
    - 'live' = Currently in progress
    - 'finished' = Completed (FT, AET, PEN)
    - 'postponed' = Rescheduled
    - 'cancelled' = Will not be played
    - 'suspended' = Stopped mid-match
    - 'interrupted' = Temporarily stopped
    - 'abandoned' = Started but not finished
    - 'awarded' = Result given by authorities
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="UUID primary key (auto-generated)"
    )
    
    # Foreign Keys
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        db_column='league_id',
        related_name='matches',
        help_text="League/competition this match belongs to"
    )
    
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column='home_team_id',
        related_name='home_matches',
        help_text="Home team"
    )
    
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column='away_team_id',
        related_name='away_matches',
        help_text="Away team"
    )
    
    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        db_column='winner_id',
        related_name='won_matches',
        null=True,
        blank=True,
        help_text="Winning team (NULL for draws or unfinished matches)"
    )
    
    # Match Details
    season = models.CharField(
        max_length=20,
        help_text="Season identifier (e.g., '2024-2025', '2025')"
    )
    
    round = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Round/matchday name (e.g., 'Regular Season - 15', 'Semi-finals')"
    )
    
    match_date = models.DateTimeField(
        help_text="Scheduled match date and time (UTC)"
    )
    
    # Match Status
    status = models.CharField(
        max_length=20,
        default='scheduled',
        help_text="Match status (scheduled/live/finished/postponed/cancelled/etc.)"
    )
    
    status_short = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Short status code (e.g., 'NS', 'LIVE', 'FT', 'PST')"
    )
    
    # Scores
    home_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Home team final score"
    )
    
    away_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Away team final score"
    )
    
    home_halftime_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Home team halftime score"
    )
    
    away_halftime_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Away team halftime score"
    )
    
    # Live Match Timing
    elapsed_time = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutes elapsed in match (for live matches)"
    )
    
    extra_time = models.IntegerField(
        null=True,
        blank=True,
        help_text="Additional minutes added (stoppage time)"
    )
    
    # External Reference
    external_id = models.TextField(
        null=True,
        blank=True,
        help_text="External API identifier (e.g., 'api-football-1234567')"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'matches'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        ordering = ['-match_date']
        indexes = [
            models.Index(fields=['league', 'season'], name='idx_matches_league_season'),
            models.Index(fields=['match_date'], name='idx_matches_match_date'),
            models.Index(fields=['status'], name='idx_matches_status'),
            models.Index(fields=['home_team', 'away_team'], name='idx_matches_teams'),
        ]
        
    def __str__(self):
        """String representation of the match"""
        score_str = ""
        if self.home_score is not None and self.away_score is not None:
            score_str = f" ({self.home_score}-{self.away_score})"
        return f"{self.home_team.name} vs {self.away_team.name}{score_str}"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Match: {self.id} - {self.home_team.name} vs {self.away_team.name}>"
    
    @property
    def is_finished(self):
        """Check if match is completed"""
        return self.status == 'finished'
    
    @property
    def is_live(self):
        """Check if match is currently in progress"""
        return self.status == 'live'
    
    @property
    def is_scheduled(self):
        """Check if match hasn't started yet"""
        return self.status == 'scheduled'
    
    @property
    def full_score(self):
        """
        Returns formatted full score string
        
        Examples:
            "2-1" (finished match)
            "1-0 (HT)" (halftime)
            "- (scheduled)"
            "2-1 (90'+3)" (live with extra time)
        """
        if self.home_score is None or self.away_score is None:
            return "- (scheduled)"
        
        score = f"{self.home_score}-{self.away_score}"
        
        if self.is_live and self.elapsed_time:
            time_str = f"{self.elapsed_time}'"
            if self.extra_time:
                time_str = f"{self.elapsed_time}'+{self.extra_time}'"
            return f"{score} ({time_str})"
        elif self.home_halftime_score is not None and not self.is_finished:
            return f"{score} (HT)"
        
        return score


class Standing(models.Model):
    """
    Standing model - maps to 'standings' table in Supabase
    
    Represents league table standings for teams in a specific season.
    Includes position, points, match statistics, and auto-calculated PPG.
    
    Database Table: standings
    Primary Key: id (UUID)
    Foreign Keys: league_id, team_id
    
    PPG (Points Per Game):
    - Auto-calculated by database trigger
    - Formula: points / games_played
    - Updates automatically when points or games_played changes
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="UUID primary key (auto-generated)"
    )
    
    # Foreign Keys
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        db_column='league_id',
        related_name='standings',
        help_text="League this standing belongs to"
    )
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column='team_id',
        related_name='standings',
        help_text="Team in the standings"
    )
    
    # Season & Position
    season = models.CharField(
        max_length=20,
        help_text="Season identifier (e.g., '2024-2025', '2025')"
    )
    
    position = models.IntegerField(
        help_text="Current league position (1 = first place)"
    )
    
    # Match Statistics
    games_played = models.IntegerField(
        default=0,
        help_text="Total matches played"
    )
    
    wins = models.IntegerField(
        default=0,
        help_text="Total wins"
    )
    
    draws = models.IntegerField(
        default=0,
        help_text="Total draws"
    )
    
    losses = models.IntegerField(
        default=0,
        help_text="Total losses"
    )
    
    # Goals
    goals_for = models.IntegerField(
        default=0,
        help_text="Total goals scored"
    )
    
    goals_against = models.IntegerField(
        default=0,
        help_text="Total goals conceded"
    )
    
    # Points
    points = models.IntegerField(
        default=0,
        help_text="Total points (3 per win, 1 per draw)"
    )
    
    # NEW: Points Per Game (auto-calculated by trigger)
    ppg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Points per game (auto-calculated: points / games_played)"
    )
    
    # Additional Info
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Additional info (e.g., 'Champions League', 'Relegation')"
    )
    
    # External Reference
    external_id = models.TextField(
        null=True,
        blank=True,
        help_text="External API identifier"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'standings'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Standing'
        verbose_name_plural = 'Standings'
        ordering = ['league', 'season', 'position']
        indexes = [
            models.Index(fields=['league', 'season'], name='idx_standings_league_season'),
            models.Index(fields=['team'], name='idx_standings_team'),
            models.Index(fields=['position'], name='idx_standings_position'),
        ]
        # Unique constraint: one team can only have one standing per league per season
        constraints = [
            models.UniqueConstraint(
                fields=['league', 'team', 'season'],
                name='unique_league_team_season'
            )
        ]
        
    def __str__(self):
        """String representation of the standing"""
        return f"{self.position}. {self.team.name} - {self.points} pts ({self.season})"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Standing: {self.team.name} - Position {self.position} in {self.league.name} {self.season}>"
    
    @property
    def goal_difference(self):
        """Calculate goal difference"""
        return self.goals_for - self.goals_against
    
    @property
    def win_percentage(self):
        """
        Calculate win percentage
        
        Returns:
            float: Win percentage (0-100)
            None: If no games played
        """
        if self.games_played == 0:
            return None
        return round((self.wins / self.games_played) * 100, 2)
    
    @property
    def form_summary(self):
        """
        Returns a summary of team form
        
        Returns:
            dict: Summary with wins, draws, losses, goals
        """
        return {
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'goal_difference': self.goal_difference,
            'points': self.points,
            'ppg': float(self.ppg) if self.ppg else None
        }


class MatchEvent(models.Model):
    """
    MatchEvent model - maps to 'match_events' table in Supabase
    
    Represents individual events during a match (goals, cards, substitutions).
    Uses JSONB field for flexible event-specific details.
    
    Database Table: match_events
    Primary Key: id (UUID)
    Foreign Keys: match_id, team_id, player_id (optional)
    
    Event Types:
    - 'goal' = Goal scored
    - 'card' = Yellow/Red card
    - 'substitution' = Player substitution
    - 'var' = VAR decision
    - 'penalty' = Penalty event
    - 'own_goal' = Own goal
    
    Event Details (JSONB):
    Flexible structure for event-specific data:
    - Goal: {"assist_player_id": "uuid", "type": "header/penalty/freekick"}
    - Card: {"type": "yellow/red", "reason": "foul/unsporting"}
    - Substitution: {"player_in_id": "uuid", "player_out_id": "uuid"}
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="UUID primary key (auto-generated)"
    )
    
    # Foreign Keys
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        db_column='match_id',
        related_name='events',
        help_text="Match this event belongs to"
    )
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column='team_id',
        related_name='match_events',
        help_text="Team involved in the event"
    )
    
    # Player is optional (some events like team warnings don't have a player)
    player_id = models.TextField(
        null=True,
        blank=True,
        help_text="Player ID involved in event (optional - stored as text UUID)"
    )
    
    # Event Information
    event_type = models.CharField(
        max_length=20,
        help_text="Event type (goal/card/substitution/var/penalty/own_goal)"
    )
    
    event_time = models.IntegerField(
        help_text="Minute when event occurred (e.g., 23, 45, 90)"
    )
    
    extra_time = models.IntegerField(
        null=True,
        blank=True,
        help_text="Additional time if event occurred in stoppage time (e.g., 90+3)"
    )
    
    # JSONB field for flexible event details
    event_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional event-specific details in JSON format"
    )
    
    # External Reference
    external_id = models.TextField(
        null=True,
        blank=True,
        help_text="External API identifier"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'match_events'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Match Event'
        verbose_name_plural = 'Match Events'
        ordering = ['match', 'event_time', 'extra_time']
        indexes = [
            models.Index(fields=['match'], name='idx_match_events_match'),
            models.Index(fields=['team'], name='idx_match_events_team'),
            models.Index(fields=['event_type'], name='idx_match_events_event_type'),
            models.Index(fields=['event_time'], name='idx_match_events_event_time'),
        ]
        
    def __str__(self):
        """String representation of the match event"""
        time_str = f"{self.event_time}'"
        if self.extra_time:
            time_str = f"{self.event_time}'+{self.extra_time}'"
        return f"{self.event_type.title()} - {self.team.name} ({time_str})"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<MatchEvent: {self.event_type} at {self.event_time}' in Match {self.match_id}>"
    
    @property
    def display_time(self):
        """
        Returns formatted time for display
        
        Examples:
            "23'" (regular time)
            "45'+2'" (stoppage time)
        """
        if self.extra_time:
            return f"{self.event_time}'+{self.extra_time}'"
        return f"{self.event_time}'"
    
    @property
    def is_goal(self):
        """Check if event is a goal"""
        return self.event_type in ['goal', 'own_goal', 'penalty']
    
    @property
    def is_card(self):
        """Check if event is a card"""
        return self.event_type == 'card'
    
    @property
    def is_substitution(self):
        """Check if event is a substitution"""
        return self.event_type == 'substitution'
