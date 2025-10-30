"""
Import teams from Football-Data.org API to Supabase for ANY league.

This script fetches teams from the Football-Data API and imports/updates
them into the teams table using UPSERT strategy.

Usage:
    # Import single league
    python scripts/import_teams.py --league PL
    
    # Import multiple leagues
    python scripts/import_teams.py --league PL PD SA BL1
    
    # Import all supported leagues
    python scripts/import_teams.py --all

Supported Leagues:
    PL   - Premier League (England)
    PD   - La Liga (Spain)
    SA   - Serie A (Italy)
    BL1  - Bundesliga (Germany)
    FL1  - Ligue 1 (France)
    PPL  - Primeira Liga (Portugal)
    DED  - Eredivisie (Netherlands)
    SL   - Super Lig (Turkey)
"""

import os
import sys
import uuid
import argparse
import requests
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Football-Data API configuration
FOOTBALL_DATA_API_KEY = "83834c41da4c4f06a1f9505aa460beb2"
FOOTBALL_DATA_API_URL = "https://api.football-data.org/v4"

# League mappings: league_code -> (competition_id, country_code)
LEAGUE_MAPPINGS = {
    "PL": (2021, "GBR"),      # Premier League (England)
    "PD": (2014, "ESP"),      # La Liga (Spain)
    "SA": (2019, "ITA"),      # Serie A (Italy)
    "BL1": (2002, "DEU"),     # Bundesliga (Germany)
    "FL1": (2015, "FRA"),     # Ligue 1 (France)
    "PPL": (2017, "PRT"),     # Primeira Liga (Portugal)
    "DED": (2003, "NLD"),     # Eredivisie (Netherlands)
    "SL": (2036, "TUR"),      # Super Lig (Turkey)
}


def get_country_id(country_code: str) -> Optional[str]:
    """
    Get country UUID from database by ISO code.
    
    Args:
        country_code: ISO country code (e.g., 'GBR', 'ESP')
    
    Returns:
        Country UUID or None if not found
    """
    try:
        result = supabase.table("countries").select("id").eq("iso_code", country_code).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        print(f"⚠️ Country not found for code: {country_code}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching country: {e}")
        return None


def get_league_id(league_code: str) -> Optional[str]:
    """
    Get league UUID from database by code.
    
    Args:
        league_code: League code (e.g., 'PL', 'PD', 'SA')
    
    Returns:
        League UUID or None if not found
    """
    try:
        result = supabase.table("leagues").select("id").eq("code", league_code).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        print(f"⚠️ League not found for code: {league_code}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching league: {e}")
        return None


def fetch_teams(competition_id: int, league_name: str) -> Optional[List[Dict]]:
    """
    Fetch teams from Football-Data API for a specific competition.
    
    Args:
        competition_id: Football-Data API competition ID
        league_name: League name for logging
    
    Returns:
        List of team dictionaries or None if error
    """
    try:
        headers = {
            "X-Auth-Token": FOOTBALL_DATA_API_KEY,
            "Content-Type": "application/json"
        }
        
        url = f"{FOOTBALL_DATA_API_URL}/competitions/{competition_id}/teams"
        
        print(f"📡 Fetching {league_name} teams from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        teams = data.get("teams", [])
        
        print(f"✅ Fetched {len(teams)} teams")
        return teams
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None


def upsert_team(team_data: dict, country_id: str, league_id: str) -> str:
    """
    Insert or update a team in the database (UPSERT).
    
    Args:
        team_data: Team data from API
        country_id: Country UUID
        league_id: League UUID
    
    Returns:
        'inserted', 'updated', 'unchanged', or 'failed'
    """
    try:
        # Check if team already exists by name
        existing = supabase.table("teams").select("*").eq("name", team_data["name"]).execute()
        
        # Prepare team data
        team_update = {
            "name": team_data["name"],
            "short_name": team_data.get("shortName", team_data["name"]),
            "logo_url": team_data.get("crest"),
            "country_id": country_id,
            "league_id": league_id,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if existing.data and len(existing.data) > 0:
            # Team exists - check if update needed
            existing_team = existing.data[0]
            team_id = existing_team["id"]
            
            # Check if any field changed
            needs_update = False
            changes = []
            
            if existing_team.get("short_name") != team_update["short_name"]:
                needs_update = True
                changes.append(f"short_name: {existing_team.get('short_name')} → {team_update['short_name']}")
            
            if existing_team.get("logo_url") != team_update["logo_url"]:
                needs_update = True
                changes.append(f"logo_url changed")
            
            if existing_team.get("country_id") != team_update["country_id"]:
                needs_update = True
                changes.append("country_id updated")
            
            if existing_team.get("league_id") != team_update["league_id"]:
                needs_update = True
                changes.append("league_id updated")
            
            if needs_update:
                # Update existing team
                result = supabase.table("teams").update(team_update).eq("id", team_id).execute()
                
                if result.data:
                    print(f"🔄 Updated: {team_data['name']}")
                    for change in changes:
                        print(f"   - {change}")
                    return "updated"
                else:
                    print(f"❌ Failed to update: {team_data['name']}")
                    return "failed"
            else:
                print(f"⏭️  No changes: {team_data['name']}")
                return "unchanged"
        
        else:
            # Team doesn't exist - insert new
            team_insert = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                **team_update
            }
            
            result = supabase.table("teams").insert(team_insert).execute()
            
            if result.data:
                print(f"✅ Inserted: {team_data['name']}")
                return "inserted"
            else:
                print(f"❌ Failed to insert: {team_data['name']}")
                return "failed"
            
    except Exception as e:
        print(f"❌ Error upserting team {team_data.get('name', 'Unknown')}: {e}")
        return "failed"


def import_league(league_code: str) -> Dict[str, int]:
    """
    Import teams for a single league.
    
    Args:
        league_code: League code (e.g., 'PL', 'PD')
    
    Returns:
        Dictionary with counts: inserted, updated, unchanged, failed
    """
    print(f"\n{'='*60}")
    print(f"🏆 PROCESSING LEAGUE: {league_code}")
    print(f"{'='*60}")
    
    # Get league mapping
    if league_code not in LEAGUE_MAPPINGS:
        print(f"❌ Unknown league code: {league_code}")
        print(f"Supported leagues: {', '.join(LEAGUE_MAPPINGS.keys())}")
        return {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    competition_id, country_code = LEAGUE_MAPPINGS[league_code]
    
    # Step 1: Get country ID
    print(f"\n📍 Step 1: Finding country ({country_code}) in database...")
    country_id = get_country_id(country_code)
    
    if not country_id:
        print(f"❌ Could not find country {country_code}. Please add it first.")
        return {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    print(f"✅ Found country: {country_id}")
    
    # Step 2: Get league ID
    print(f"\n🏆 Step 2: Finding league ({league_code}) in database...")
    league_id = get_league_id(league_code)
    
    if not league_id:
        print(f"❌ Could not find league {league_code}. Please add it first.")
        return {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    print(f"✅ Found league: {league_id}")
    
    # Step 3: Fetch teams from API
    print(f"\n📡 Step 3: Fetching teams from Football-Data API...")
    teams = fetch_teams(competition_id, league_code)
    
    if not teams:
        print(f"❌ Failed to fetch teams for {league_code}")
        return {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    # Step 4: Upsert each team
    print(f"\n📥 Step 4: Processing {len(teams)} teams...")
    print("-" * 60)
    
    counts = {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    for team_data in teams:
        result = upsert_team(team_data, country_id, league_id)
        counts[result] = counts.get(result, 0) + 1
    
    # Summary for this league
    print("\n" + "-" * 60)
    print(f"📊 {league_code} SUMMARY:")
    print(f"✨ Inserted: {counts['inserted']}")
    print(f"🔄 Updated: {counts['updated']}")
    print(f"⏭️  Unchanged: {counts['unchanged']}")
    print(f"❌ Failed: {counts['failed']}")
    print(f"📊 Total: {len(teams)}")
    
    return counts


def main():
    """Main function to orchestrate the import process."""
    parser = argparse.ArgumentParser(
        description="Import teams from Football-Data API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import single league
  python scripts/import_teams.py --league PL
  
  # Import multiple leagues
  python scripts/import_teams.py --league PL PD SA
  
  # Import all supported leagues
  python scripts/import_teams.py --all

Supported Leagues:
  PL   - Premier League (England)
  PD   - La Liga (Spain)
  SA   - Serie A (Italy)
  BL1  - Bundesliga (Germany)
  FL1  - Ligue 1 (France)
  PPL  - Primeira Liga (Portugal)
  DED  - Eredivisie (Netherlands)
  SL   - Super Lig (Turkey)
        """
    )
    
    parser.add_argument(
        "--league",
        nargs="+",
        help="League code(s) to import (e.g., PL PD SA)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Import all supported leagues"
    )
    
    args = parser.parse_args()
    
    # Determine which leagues to process
    if args.all:
        leagues_to_process = list(LEAGUE_MAPPINGS.keys())
    elif args.league:
        leagues_to_process = args.league
    else:
        parser.print_help()
        return
    
    print("\n🚀 Starting Teams Import/Update")
    print(f"📋 Leagues to process: {', '.join(leagues_to_process)}")
    
    # Process each league
    total_counts = {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    for league_code in leagues_to_process:
        counts = import_league(league_code.upper())
        for key in total_counts:
            total_counts[key] += counts[key]
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY (ALL LEAGUES)")
    print("=" * 60)
    print(f"✨ Total inserted: {total_counts['inserted']}")
    print(f"🔄 Total updated: {total_counts['updated']}")
    print(f"⏭️  Total unchanged: {total_counts['unchanged']}")
    print(f"❌ Total failed: {total_counts['failed']}")
    print(f"📊 Grand total: {sum(total_counts.values())}")
    print("=" * 60)
    
    if total_counts['inserted'] > 0 or total_counts['updated'] > 0:
        print("\n✨ Import/Update completed successfully!")
    elif total_counts['unchanged'] == sum(total_counts.values()):
        print("\n✅ All teams are up-to-date!")
    else:
        print("\n⚠️ Import/Update completed with some errors")


if __name__ == "__main__":
    main()
