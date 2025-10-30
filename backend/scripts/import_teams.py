"""
Import teams from Football-Data.org API to Supabase.

This script fetches teams from ANY competition using the Football-Data API
and imports/updates them into the teams table using UPSERT strategy.

The script works with competition IDs directly - no hardcoded leagues.
Just pass any valid Football-Data competition ID.

Usage:
    # Import teams from a specific competition
    python scripts/import_teams.py --competition-id 2021  # Premier League
    python scripts/import_teams.py --competition-id 2014  # La Liga
    python scripts/import_teams.py --competition-id 2019  # Serie A

Common Competition IDs:
    2021 - Premier League (England)
    2014 - La Liga (Spain)
    2019 - Serie A (Italy)
    2002 - Bundesliga (Germany)
    2015 - Ligue 1 (France)
    2017 - Primeira Liga (Portugal)
    2003 - Eredivisie (Netherlands)
    (Find more at: https://www.football-data.org/documentation/api)
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


def get_country_id_by_name(country_name: str) -> Optional[str]:
    """
    Get country UUID from database by country name.
    Uses fuzzy matching with ILIKE to handle variations.
    
    Args:
        country_name: Country name from API (e.g., 'England', 'Spain', 'Italy')
    
    Returns:
        Country UUID or None if not found
    """
    try:
        # Try exact match first
        result = supabase.table("countries").select("id, name, code").ilike("name", country_name).execute()
        
        if result.data and len(result.data) > 0:
            country = result.data[0]
            print(f"   ✓ Mapped '{country_name}' → {country['name']} ({country['code']})")
            return country["id"]
        
        # Try fuzzy match (contains)
        result = supabase.table("countries").select("id, name, code").ilike("name", f"%{country_name}%").execute()
        
        if result.data and len(result.data) > 0:
            country = result.data[0]
            print(f"   ✓ Mapped '{country_name}' → {country['name']} ({country['code']})")
            return country["id"]
        
        print(f"   ⚠️ Country not found in database: {country_name}")
        return None
        
    except Exception as e:
        print(f"   ❌ Error fetching country: {e}")
        return None


def fetch_teams(competition_id: int) -> Optional[Dict]:
    """
    Fetch teams from Football-Data API for a specific competition.
    
    Args:
        competition_id: Football-Data API competition ID
    
    Returns:
        API response dictionary or None if error
    """
    try:
        headers = {
            "X-Auth-Token": FOOTBALL_DATA_API_KEY,
            "Content-Type": "application/json"
        }
        
        url = f"{FOOTBALL_DATA_API_URL}/competitions/{competition_id}/teams"
        
        print(f"📡 Fetching teams from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        competition = data.get("competition", {})
        teams = data.get("teams", [])
        
        print(f"✅ Competition: {competition.get('name', 'Unknown')}")
        print(f"✅ Fetched {len(teams)} teams")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"❌ Response: {e.response.text}")
        return None


def upsert_team(team_data: dict) -> str:
    """
    Insert or update a team in the database (UPSERT).
    Uses external_id as the unique identifier.
    
    Args:
        team_data: Team data from API
    
    Returns:
        'inserted', 'updated', 'unchanged', or 'failed'
    """
    try:
        # Get country_id from area name (not code!)
        country_name = team_data.get("area", {}).get("name")
        country_id = None
        
        if country_name:
            country_id = get_country_id_by_name(country_name)
            if not country_id:
                print(f"   ⚠️ Could not map country for team: {team_data.get('name')}")
        
        # Prepare external_id (API team ID as string)
        external_id = str(team_data.get("id"))
        
        # Check if team already exists by external_id
        existing = supabase.table("teams").select("*").eq("external_id", external_id).execute()
        
        # Prepare team data for upsert
        team_update = {
            "name": team_data.get("name"),
            "logo": team_data.get("crest"),
            "external_id": external_id,
            "founded": team_data.get("founded"),
            "country_id": country_id,
            "code": team_data.get("tla"),  # Three Letter Acronym
            "website": team_data.get("website"),
            "market_value": None,  # Not available in Football-Data API
            "is_active": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if existing.data and len(existing.data) > 0:
            # Team exists - check if update needed
            existing_team = existing.data[0]
            team_id = existing_team["id"]
            
            # Check if any field changed
            needs_update = False
            changes = []
            
            for field in ["name", "logo", "founded", "country_id", "code", "website"]:
                old_val = existing_team.get(field)
                new_val = team_update.get(field)
                
                # Handle None comparisons
                if old_val != new_val:
                    needs_update = True
                    changes.append(f"{field}: {old_val} → {new_val}")
            
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
            # Generate UUID for id (text type)
            team_insert = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                **team_update
            }
            
            result = supabase.table("teams").insert(team_insert).execute()
            
            if result.data:
                print(f"✅ Inserted: {team_data['name']} (External ID: {external_id})")
                return "inserted"
            else:
                print(f"❌ Failed to insert: {team_data['name']}")
                return "failed"
            
    except Exception as e:
        print(f"❌ Error upserting team {team_data.get('name', 'Unknown')}: {e}")
        import traceback
        traceback.print_exc()
        return "failed"


def main():
    """Main function to orchestrate the import process."""
    parser = argparse.ArgumentParser(
        description="Import teams from Football-Data API for any competition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import Premier League teams
  python scripts/import_teams.py --competition-id 2021
  
  # Import La Liga teams
  python scripts/import_teams.py --competition-id 2014
  
  # Import Serie A teams
  python scripts/import_teams.py --competition-id 2019

Common Competition IDs:
  2021 - Premier League (England)
  2014 - La Liga (Spain)
  2019 - Serie A (Italy)
  2002 - Bundesliga (Germany)
  2015 - Ligue 1 (France)
  2017 - Primeira Liga (Portugal)
  2003 - Eredivisie (Netherlands)
  
Find more competition IDs at:
https://www.football-data.org/documentation/api
        """
    )
    
    parser.add_argument(
        "--competition-id",
        type=int,
        required=True,
        help="Football-Data API competition ID (e.g., 2021 for Premier League)"
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Starting Teams Import/Update")
    print("=" * 60)
    print(f"📋 Competition ID: {args.competition_id}")
    print("=" * 60)
    
    # Step 1: Fetch teams from API
    print(f"\n📡 Step 1: Fetching teams from Football-Data API...")
    api_data = fetch_teams(args.competition_id)
    
    if not api_data:
        print("❌ Failed to fetch teams from API")
        return
    
    teams = api_data.get("teams", [])
    competition = api_data.get("competition", {})
    
    if not teams:
        print("❌ No teams found in API response")
        return
    
    # Step 2: Upsert each team
    print(f"\n📥 Step 2: Processing {len(teams)} teams from {competition.get('name', 'Unknown')}...")
    print("-" * 60)
    
    counts = {"inserted": 0, "updated": 0, "unchanged": 0, "failed": 0}
    
    for team_data in teams:
        result = upsert_team(team_data)
        counts[result] = counts.get(result, 0) + 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 IMPORT SUMMARY")
    print("=" * 60)
    print(f"✨ Newly inserted: {counts['inserted']}")
    print(f"🔄 Updated: {counts['updated']}")
    print(f"⏭️  Unchanged: {counts['unchanged']}")
    print(f"❌ Failed: {counts['failed']}")
    print(f"📊 Total processed: {len(teams)}")
    print("=" * 60)
    
    if counts['inserted'] > 0 or counts['updated'] > 0:
        print("\n✨ Import/Update completed successfully!")
    elif counts['unchanged'] == len(teams):
        print("\n✅ All teams are up-to-date!")
    else:
        print("\n⚠️ Import/Update completed with some errors")


if __name__ == "__main__":
    main()
