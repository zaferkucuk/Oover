"""
Django Models for Core App

This module contains core Django models that map to existing Supabase tables.
All models use managed=False since tables are managed in Supabase.

Author: Oover Development Team
Date: October 2025
"""

from django.db import models
from django.utils import timezone


class Country(models.Model):
    """
    Country model - maps to 'countries' table in Supabase
    
    Represents countries where football leagues and teams exist.
    Includes both national countries and international entities (e.g., UEFA, World).
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.CharField(
        max_length=10,
        primary_key=True,
        help_text="Unique country identifier (e.g., 'england', 'spain', 'world')"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Full country name (e.g., 'England', 'Spain', 'World')"
    )
    
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Country code (e.g., 'GB', 'ES', 'WORLD')"
    )
    
    flag = models.CharField(
        max_length=50,
        help_text="Flag emoji or URL (e.g., '🏴󠁧󠁢󠁥󠁮󠁧󠁿', '🇪🇸')"
    )
    
    # Status Fields
    is_international = models.BooleanField(
        default=False,
        help_text="True for international entities (UEFA, World, etc.)"
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
        auto_now=True,
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
        return f"{self.flag} {self.name}"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<Country: {self.id} - {self.name}>"


class League(models.Model):
    """
    League model - maps to 'leagues' table in Supabase
    
    Represents football leagues/competitions across different countries.
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Unique league identifier"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="League name (e.g., 'Premier League', 'La Liga')"
    )
    
    # Foreign Key
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        db_column='country_id',
        related_name='leagues',
        help_text="Country where league operates"
    )
    
    # Additional Fields
    logo = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="League logo URL"
    )
    
    type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="League type (e.g., 'League', 'Cup')"
    )
    
    # External API Integration
    api_football_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID from API-Football service"
    )
    
    football_data_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID from Football-Data.org service"
    )
    
    # Status Fields
    is_active = models.BooleanField(
        default=True,
        help_text="False to hide league from active lists"
    )
    
    # Timestamp Fields
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
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
        return f"{self.name} ({self.country.name})"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<League: {self.id} - {self.name}>"


class Team(models.Model):
    """
    Team model - maps to 'teams' table in Supabase
    
    Represents football teams/clubs.
    
    Note: This is an unmanaged model (managed=False) because the table
    is created and managed in Supabase, not by Django migrations.
    """
    
    # Primary Fields
    id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Unique team identifier"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Team name (e.g., 'Manchester United', 'Real Madrid')"
    )
    
    # Foreign Key
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        db_column='country_id',
        related_name='teams',
        help_text="Team's home country"
    )
    
    # Additional Fields
    logo = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Team logo URL"
    )
    
    venue_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Home stadium name"
    )
    
    venue_city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Stadium city"
    )
    
    founded = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year team was founded"
    )
    
    # External API Integration
    api_football_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID from API-Football service"
    )
    
    football_data_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID from Football-Data.org service"
    )
    
    # Status Fields
    is_active = models.BooleanField(
        default=True,
        help_text="False to hide team from active lists"
    )
    
    # Timestamp Fields
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
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
