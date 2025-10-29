"""
Django Models for Core App

This module contains core Django models that map to existing Supabase tables.
All models use managed=False since tables are managed in Supabase.

IMPORTANT: Column names use snake_case to match PostgreSQL/Supabase convention.
          Foreign keys use db_column to map Python names to database columns.

Author: Oover Development Team
Date: October 2025
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
    Primary Key: id (text)
    Foreign Keys: sport_id (Sport), country_id (Country UUID)
    
    Note: Season information is NOT stored here. It will be in a separate
          'league_seasons' table in the future to avoid data duplication.
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.TextField(
        primary_key=True,
        help_text="Unique league identifier (text UUID)"
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
            return f"{self.name} ({self.country.name})"
        return self.name
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<League: {self.id} - {self.name}>"


class Team(models.Model):
    """
    Team model - maps to 'teams' table in Supabase
    
    Represents football teams/clubs.
    Uses snake_case for new fields, camelCase for legacy fields.
    
    Database Table: teams
    Primary Key: id (text)
    Foreign Keys: league_id (League), country_id (Country UUID)
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.TextField(
        primary_key=True,
        help_text="Unique team identifier (text UUID)"
    )
    
    name = models.TextField(
        help_text="Team name (e.g., 'Manchester United', 'Real Madrid')"
    )
    
    short_name = models.TextField(
        null=True,
        blank=True,
        db_column='shortName',  # Maps to Supabase camelCase column
        help_text="Short team name (e.g., 'Man Utd', 'Real')"
    )
    
    # Foreign Keys (snake_case)
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        db_column='league_id',
        related_name='teams',
        help_text="Primary league where team competes"
    )
    
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        db_column='country_id',
        related_name='teams',
        null=True,
        blank=True,
        help_text="Team's home country"
    )
    
    # Additional Fields
    logo = models.TextField(
        null=True,
        blank=True,
        help_text="Team logo URL"
    )
    
    venue = models.TextField(
        null=True,
        blank=True,
        help_text="Home stadium name"
    )
    
    founded = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year team was founded"
    )
    
    external_id = models.TextField(
        null=True,
        blank=True,
        db_column='externalId',  # Maps to Supabase camelCase column
        help_text="External API identifier"
    )
    
    # Timestamp Fields (camelCase in Supabase)
    created_at = models.DateTimeField(
        default=timezone.now,
        db_column='createdAt',
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='updatedAt',
        help_text="Record last update timestamp"
    )
    
    class Meta:
        db_table = 'teams'
        managed = False  # Table is managed in Supabase
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['name']
        
    def __str__(self):
        """String representation of the team"""
        return self.name
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Team: {self.id} - {self.name}>"
