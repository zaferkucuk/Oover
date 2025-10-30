"""
Import Premier League teams from Football-Data.org API to Supabase.

This script fetches Premier League teams from the Football-Data API
and imports them into the teams table.

Usage:
    python scripts/import_pl_teams.py
"""

import os
import sys
import uuid
import requests
from datetime import datetime

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


def get_country_id(country_code: str) -> str:
    """
    Get country UUID from database by ISO code.
    
    Args:
        country_code: ISO country code (e.g., 'ENG', 'ESP')
    
    Returns:
        Country UUID or None if not found
    """
    try:
        # Try with iso_code first (GBR for England)
        if country_code == "ENG":
            country_code = "GBR"
        
        result = supabase.table("countries").select("id").eq("iso_code", country_code).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        print(f"⚠️ Country not found for code: {country_code}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching country: {e}")
        return None


def get_league_id(league_code: str) -> str:
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


def fetch_pl_teams():
    """
    Fetch Premier League teams from Football-Data API.
    
    Returns:
        List of team dictionaries or None if error
    """
    try:
        headers = {
            "X-Auth-Token": FOOTBALL_DATA_API_KEY,
            "Content-Type": "application/json"
        }
        
        url = f"{FOOTBALL_DATA_API_URL}/competitions/2021/teams"
        
        print(f"📡 Fetching teams from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        teams = data.get("teams", [])
        
        print(f"✅ Fetched {len(teams)} teams")
        return teams
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None


def import_team(team_data: dict, country_id: str, league_id: str) -> bool:
    """
    Import a single team into the database.
    
    Args:
        team_data: Team data from API
        country_id: Country UUID
        league_id: League UUID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if team already exists by name
        existing = supabase.table("teams").select("id").eq("name", team_data["name"]).execute()
        
        if existing.data and len(existing.data) > 0:
            print(f"⏭️  Team already exists: {team_data['name']}")
            return True
        
        # Prepare team data
        team = {
            "id": str(uuid.uuid4()),
            "name": team_data["name"],
            "short_name": team_data.get("shortName", team_data["name"]),
            "logo_url": team_data.get("crest"),
            "country_id": country_id,
            "league_id": league_id,
            "api_football_id": None,  # Football-Data doesn't match API-Football IDs
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert into database
        result = supabase.table("teams").insert(team).execute()
        
        if result.data:
            print(f"✅ Imported: {team_data['name']}")
            return True
        else:
            print(f"❌ Failed to import: {team_data['name']}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing team {team_data.get('name', 'Unknown')}: {e}")
        return False


def main():
    """Main function to orchestrate the import process."""
    print("\n🚀 Starting Premier League Teams Import")
    print("=" * 50)
    
    # Step 1: Get country ID (England = GBR)
    print("\n📍 Step 1: Finding England in database...")
    country_id = get_country_id("GBR")
    
    if not country_id:
        print("❌ Could not find England in countries table. Please add it first.")
        return
    
    print(f"✅ Found England: {country_id}")
    
    # Step 2: Get league ID (Premier League)
    print("\n🏆 Step 2: Finding Premier League in database...")
    league_id = get_league_id("PL")
    
    if not league_id:
        print("❌ Could not find Premier League in leagues table. Please add it first.")
        return
    
    print(f"✅ Found Premier League: {league_id}")
    
    # Step 3: Fetch teams from API
    print("\n📡 Step 3: Fetching teams from Football-Data API...")
    teams = fetch_pl_teams()
    
    if not teams:
        print("❌ Failed to fetch teams from API")
        return
    
    # Step 4: Import each team
    print(f"\n📥 Step 4: Importing {len(teams)} teams...")
    print("-" * 50)
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for team_data in teams:
        result = import_team(team_data, country_id, league_id)
        if result:
            if "already exists" in str(result):
                skip_count += 1
            else:
                success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully imported: {success_count}")
    print(f"⏭️  Skipped (already exists): {skip_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total processed: {len(teams)}")
    print("=" * 50)
    
    if success_count > 0:
        print("\n✨ Import completed successfully!")
    elif skip_count == len(teams):
        print("\n✨ All teams already exist in database!")
    else:
        print("\n⚠️ Import completed with some errors")


if __name__ == "__main__":
    main()
