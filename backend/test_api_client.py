"""
Test script for Football-Data.org API client

This script tests the FootballDataClient directly without Django,
to verify the endpoint fix is working correctly.

Usage:
    python test_api_client.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the client
from api_integrations.providers.football_data_org.client import FootballDataClient

def test_client():
    """Test FootballDataClient with Premier League"""
    
    print("=" * 60)
    print("Football-Data.org API Client Test")
    print("=" * 60)
    
    # Get API key from environment
    api_key = os.environ.get('FOOTBALL_DATA_API_KEY', '83834c41da4c4f06a1f9505aa460beb2')
    
    print(f"\n1. Initializing client...")
    print(f"   API Key: {api_key[:10]}...")
    
    try:
        client = FootballDataClient(api_key=api_key)
        print("   ✅ Client initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return
    
    print(f"\n2. Testing get_teams_by_competition('PL')...")
    
    try:
        teams = client.get_teams_by_competition('PL')
        
        print(f"   ✅ Success! Fetched {len(teams)} teams")
        
        if teams:
            print(f"\n3. Sample teams:")
            for i, team in enumerate(teams[:3], 1):
                print(f"   {i}. {team.get('name')} ({team.get('tla')})")
                print(f"      Area: {team.get('area', {}).get('name')}")
                print(f"      Founded: {team.get('founded')}")
                print(f"      Crest: {team.get('crest', 'N/A')[:50]}...")
                print()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"\nFull error details:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_client()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - API client is working correctly!")
    else:
        print("❌ TEST FAILED - Check error details above")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
