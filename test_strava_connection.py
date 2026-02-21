#!/usr/bin/env python3
"""
Test Strava API connection
"""

import os
from dotenv import load_dotenv
from sync_strava_data import StravaSync

def main():
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize sync client
        sync_client = StravaSync()
        
        # Test token refresh
        if sync_client.refresh_access_token():
            print("✅ Strava API connection successful!")
            print(f"Access token obtained (expires at: {sync_client.token_expires_at})")
            
            # Test fetching a few activities
            activities = sync_client.get_athlete_activities(page=1, per_page=5)
            if activities:
                print(f"✅ Successfully fetched {len(activities)} recent activities")
                for i, activity in enumerate(activities[:3]):
                    print(f"  {i+1}. {activity.get('name', 'Unnamed')} - {activity.get('start_date', 'No date')}")
            else:
                print("⚠️  No activities found or failed to fetch activities")
        else:
            print("❌ Failed to authenticate with Strava API")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()