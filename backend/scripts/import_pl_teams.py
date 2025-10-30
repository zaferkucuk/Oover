"""
Import Premier League teams from Football-Data.org API to Supabase.

This script fetches Premier League teams from the Football-Data API
and imports/updates them into the teams table using UPSERT strategy.

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


def upsert_team(team_data: dict, country_id: str, league_id: str) -> str:
    """
    Insert or update a team in the database (UPSERT).
    
    Args:
        team_data: Team data from API
        country_id: Country UUID
        league_id: League UUID
    
    Returns:
        'inserted', 'updated', or 'failed'
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
                changes.append(f"logo_url: {existing_team.get('logo_url')} → {team_update['logo_url']}")
            
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


def main():
    """Main function to orchestrate the import process."""
    print("\n🚀 Starting Premier League Teams Import/Update")
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
    
    # Step 4: Upsert each team
    print(f"\n📥 Step 4: Processing {len(teams)} teams...")
    print("-" * 50)
    
    inserted_count = 0
    updated_count = 0
    unchanged_count = 0
    failed_count = 0
    
    for team_data in teams:
        result = upsert_team(team_data, country_id, league_id)
        
        if result == "inserted":
            inserted_count += 1
        elif result == "updated":
            updated_count += 1
        elif result == "unchanged":
            unchanged_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 IMPORT/UPDATE SUMMARY")
    print("=" * 50)
    print(f"✨ Newly inserted: {inserted_count}")
    print(f"🔄 Updated: {updated_count}")
    print(f"⏭️  Unchanged: {unchanged_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total processed: {len(teams)}")
    print("=" * 50)
    
    if inserted_count > 0 or updated_count > 0:
        print("\n✨ Import/Update completed successfully!")
    elif unchanged_count == len(teams):
        print("\n✅ All teams are up-to-date!")
    else:
        print("\n⚠️ Import/Update completed with some errors")


if __name__ == "__main__":
    main()
