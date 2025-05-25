#!/usr/bin/env python3
"""
Strava Data Sync Script
This script fetches activity data from Strava API and updates the local activities.json file.
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StravaSync:
    def __init__(self):
        """Initialize Strava API client with credentials from environment variables."""
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Missing required Strava API credentials in environment variables")
        
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://www.strava.com/api/v3"
        
        # Rate limiting
        self.rate_limit_remaining = 600  # Strava allows 600 requests per 15 minutes
        self.rate_limit_reset_time = None
        
    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        try:
            logger.info("Refreshing Strava access token...")
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post('https://www.strava.com/oauth/token', data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']  # Update refresh token
            self.token_expires_at = token_data['expires_at']
            
            logger.info("Access token refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """Check if the current access token is valid."""
        if not self.access_token or not self.token_expires_at:
            return False
        
        # Add 5 minute buffer before expiration
        return time.time() < (self.token_expires_at - 300)
    
    def ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.is_token_valid():
            return self.refresh_access_token()
        return True
    
    def handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limiting based on response headers."""
        if 'X-RateLimit-Limit' in response.headers:
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Usage', '0').split(',')[0])
            
        if response.status_code == 429:  # Rate limited
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 900))
            sleep_time = reset_time - time.time()
            logger.warning(f"Rate limited. Sleeping for {sleep_time:.0f} seconds...")
            time.sleep(max(sleep_time, 0))
    
    def make_api_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the Strava API with proper error handling."""
        if not self.ensure_valid_token():
            logger.error("Failed to get valid access token")
            return None
        
        # Check rate limit
        if self.rate_limit_remaining <= 5:
            logger.warning("Approaching rate limit, sleeping for 60 seconds...")
            time.sleep(60)
        
        url = f"{self.base_url}/{endpoint}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(url, headers=headers, params=params or {})
            self.handle_rate_limit(response)
            
            if response.status_code == 429:
                # Retry after rate limit reset
                return self.make_api_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
    
    def get_athlete_activities(self, page: int = 1, per_page: int = 50, after: Optional[int] = None) -> List[Dict]:
        """Fetch athlete activities from Strava API."""
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if after:
            params['after'] = after
        
        logger.info(f"Fetching activities page {page} (per_page={per_page})")
        
        activities = self.make_api_request('athlete/activities', params)
        return activities if activities else []
    
    def get_activity_details(self, activity_id: int) -> Optional[Dict]:
        """Fetch detailed information for a specific activity."""
        logger.info(f"Fetching details for activity {activity_id}")
        return self.make_api_request(f'activities/{activity_id}')
    
    def load_existing_activities(self) -> List[Dict]:
        """Load existing activities from local JSON file."""
        activities_file = 'data/activities.json'
        
        if not os.path.exists(activities_file):
            logger.info("No existing activities file found, starting fresh")
            return []
        
        try:
            with open(activities_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)
            logger.info(f"Loaded {len(activities)} existing activities")
            return activities
        except Exception as e:
            logger.error(f"Failed to load existing activities: {e}")
            return []
    
    def save_activities(self, activities: List[Dict]) -> bool:
        """Save activities to local JSON file."""
        try:
            os.makedirs('data', exist_ok=True)
            
            # Sort activities by start_date (newest first)
            activities.sort(key=lambda x: x.get('start_date', ''), reverse=True)
            
            with open('data/activities.json', 'w', encoding='utf-8') as f:
                json.dump(activities, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(activities)} activities to data/activities.json")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save activities: {e}")
            return False
    
    def get_last_activity_date(self, activities: List[Dict]) -> Optional[datetime]:
        """Get the date of the most recent activity."""
        if not activities:
            return None
        
        try:
            # Activities should be sorted by date, so take the first one
            latest_date_str = activities[0].get('start_date')
            if latest_date_str:
                return datetime.fromisoformat(latest_date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Failed to parse last activity date: {e}")
        
        return None
    
    def sync_activities(self, full_sync: bool = False) -> bool:
        """
        Sync activities from Strava API.
        
        Args:
            full_sync: If True, fetch all activities. If False, only fetch new ones.
        """
        logger.info(f"Starting {'full' if full_sync else 'incremental'} sync...")
        
        # Load existing activities
        existing_activities = self.load_existing_activities()
        existing_ids = {act.get('id') for act in existing_activities if act.get('id')}
        
        # Determine sync parameters
        after_timestamp = None
        if not full_sync and existing_activities:
            last_date = self.get_last_activity_date(existing_activities)
            if last_date:
                # Fetch activities after the last known activity (with 1 day buffer)
                after_date = last_date - timedelta(days=1)
                after_timestamp = int(after_date.timestamp())
                logger.info(f"Incremental sync from {after_date.isoformat()}")
        
        # Fetch activities from Strava
        all_new_activities = []
        page = 1
        
        while True:
            activities = self.get_athlete_activities(
                page=page, 
                per_page=50, 
                after=after_timestamp
            )
            
            if not activities:
                break
            
            logger.info(f"Fetched {len(activities)} activities from page {page}")
            
            # Filter out activities we already have (for incremental sync)
            new_activities = []
            for activity in activities:
                if activity.get('id') not in existing_ids:
                    new_activities.append(activity)
            
            all_new_activities.extend(new_activities)
            
            # If we got less than 50 activities, we've reached the end
            if len(activities) < 50:
                break
            
            page += 1
            
            # Add delay to respect rate limits
            time.sleep(1)
        
        logger.info(f"Found {len(all_new_activities)} new activities")
        
        # Fetch detailed information for new activities
        detailed_activities = []
        for i, activity in enumerate(all_new_activities):
            activity_id = activity.get('id')
            if not activity_id:
                continue
            
            logger.info(f"Processing activity {i+1}/{len(all_new_activities)}: {activity_id}")
            
            # Get detailed activity data
            detailed_activity = self.get_activity_details(activity_id)
            if detailed_activity:
                detailed_activities.append(detailed_activity)
            
            # Rate limiting: sleep between requests
            time.sleep(0.5)
        
        # Combine with existing activities
        if full_sync:
            # Replace all activities
            final_activities = detailed_activities
        else:
            # Add new activities to existing ones
            final_activities = detailed_activities + existing_activities
        
        # Remove duplicates based on ID
        seen_ids = set()
        unique_activities = []
        for activity in final_activities:
            activity_id = activity.get('id')
            if activity_id and activity_id not in seen_ids:
                seen_ids.add(activity_id)
                unique_activities.append(activity)
        
        # Save updated activities
        if self.save_activities(unique_activities):
            logger.info(f"Sync completed successfully. Total activities: {len(unique_activities)}")
            return True
        else:
            logger.error("Failed to save activities")
            return False

def main():
    """Main function to run the sync process."""
    try:
        # Load environment variables from .env file if it exists
        if os.path.exists('.env'):
            from dotenv import load_dotenv
            load_dotenv()
            logger.info("Loaded environment variables from .env file")
        
        # Initialize sync client
        sync_client = StravaSync()
        
        # Determine sync type
        full_sync = os.getenv('FULL_SYNC', '').lower() in ('true', '1', 'yes')
        
        # Run sync
        success = sync_client.sync_activities(full_sync=full_sync)
        
        if success:
            logger.info("Strava data sync completed successfully")
            
            # Run statistics calculation
            try:
                import subprocess
                logger.info("Generating statistics and visualizations...")
                result = subprocess.run(['python', 'calculate_stats.py'], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("Statistics generated successfully")
                else:
                    logger.error(f"Statistics generation failed: {result.stderr}")
                
                # Generate visualizations
                result = subprocess.run(['python', 'generate_visualizations.py'], 
                                      capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    logger.info("Visualizations generated successfully")
                else:
                    logger.error(f"Visualization generation failed: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Failed to run post-processing: {e}")
            
            exit(0)
        else:
            logger.error("Strava data sync failed")
            exit(1)
            
    except Exception as e:
        logger.error(f"Sync process failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()