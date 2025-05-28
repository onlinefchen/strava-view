#!/usr/bin/env python3
"""
Calculate running statistics and generate JSON data for the dashboard.
This script processes activities.json and generates pre-calculated stats for each year.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from timezone_config import parse_local_datetime, get_timezone_info

def load_activities():
    """Load activities from JSON file."""
    with open('data/activities.json', 'r') as f:
        return json.load(f)

def format_pace(seconds_per_km):
    """Format pace as MM'SS" per km."""
    if seconds_per_km <= 0:
        return "N/A"
    
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    return f"{minutes}'{seconds:02d}\""

def format_time(total_seconds):
    """Format time as HH:MM:SS or MM:SS."""
    if total_seconds <= 0:
        return "N/A"
    
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def format_date(date_string):
    """Format date as MM/DD."""
    try:
        dt = parse_local_datetime(date_string)
        return dt.strftime("%m/%d")
    except:
        return "N/A"

def extract_city_from_activity(activity):
    """Extract city information from activity data."""
    # First try explicit location fields
    if activity.get('location_city'):
        return activity['location_city']
    
    # Try to extract from timezone
    timezone = activity.get('timezone', '')
    if timezone:
        # Format: "(GMT+08:00) Asia/Shanghai" -> "Shanghai"
        if 'Asia/' in timezone:
            city = timezone.split('Asia/')[-1].strip(')')
            return city
        elif 'Europe/' in timezone:
            city = timezone.split('Europe/')[-1].strip(')')
            return city
        elif 'America/' in timezone:
            city = timezone.split('America/')[-1].strip(')')
            # Handle cases like "America/New_York" -> "New York"
            city = city.replace('_', ' ')
            return city
        elif 'Australia/' in timezone:
            city = timezone.split('Australia/')[-1].strip(')')
            return city
    
    # Try location_country as fallback
    if activity.get('location_country'):
        return activity['location_country']
    
    # Final fallback
    return "Unknown"

def calculate_yearly_stats():
    """Calculate statistics for each year."""
    activities = load_activities()
    yearly_stats = defaultdict(lambda: {
        'total_activities': 0,
        'total_distance': 0,  # in km
        'total_time': 0,
        'heart_rates': [],
        'activities_list': []
    })
    
    # Group activities by year
    for activity in activities:
        if not activity.get('start_date_local'):
            continue
            
        try:
            date = parse_local_datetime(activity['start_date_local'])
            year = date.year
            
            # Only include runs with valid distance and time
            if activity.get('distance', 0) > 1000 and activity.get('moving_time', 0) > 180:
                yearly_stats[year]['total_activities'] += 1
                yearly_stats[year]['total_distance'] += activity['distance'] / 1000  # convert to km
                yearly_stats[year]['total_time'] += activity['moving_time']
                yearly_stats[year]['activities_list'].append(activity)
                
                if activity.get('average_heartrate'):
                    yearly_stats[year]['heart_rates'].append(activity['average_heartrate'])
        except:
            continue
    
    # Calculate derived stats for each year
    final_stats = {}
    
    for year, stats in yearly_stats.items():
        if stats['total_activities'] == 0:
            continue
            
        activities_list = stats['activities_list']
        
        # Calculate averages
        avg_pace = stats['total_time'] / stats['total_distance'] if stats['total_distance'] > 0 else 0
        avg_heart_rate = sum(stats['heart_rates']) / len(stats['heart_rates']) if stats['heart_rates'] else 0
        
        # Find longest distance activity
        longest_activity = max(activities_list, key=lambda x: x.get('distance', 0))
        longest_pace = longest_activity['moving_time'] / (longest_activity['distance'] / 1000)
        
        # Find best pace activity (minimum pace among activities > 1km)
        valid_activities = [a for a in activities_list if a.get('distance', 0) > 1000]
        if valid_activities:
            best_pace_activity = min(valid_activities, 
                                   key=lambda x: x['moving_time'] / (x['distance'] / 1000))
            best_pace = best_pace_activity['moving_time'] / (best_pace_activity['distance'] / 1000)
        else:
            best_pace_activity = longest_activity
            best_pace = longest_pace
        
        final_stats[str(year)] = {
            # Yearly stats
            'total_activities': stats['total_activities'],
            'total_distance': round(stats['total_distance'], 1),
            'avg_pace': format_pace(avg_pace),
            'best_pace': format_pace(best_pace),
            'avg_heart_rate': int(avg_heart_rate) if avg_heart_rate > 0 else 'N/A',
            
            # Longest distance details
            'longest_distance': f"{longest_activity['distance'] / 1000:.1f} km",
            'longest_date': format_date(longest_activity.get('start_date_local', '')),
            'longest_duration': format_time(longest_activity.get('moving_time', 0)),
            'longest_pace': format_pace(longest_pace),
            'longest_city': extract_city_from_activity(longest_activity),
            
            # Best pace details
            'fastest_pace': format_pace(best_pace),
            'fastest_date': format_date(best_pace_activity.get('start_date_local', '')),
            'fastest_distance': f"{best_pace_activity['distance'] / 1000:.1f} km",
            'fastest_duration': format_time(best_pace_activity.get('moving_time', 0)),
            'fastest_city': extract_city_from_activity(best_pace_activity)
        }
    
    return final_stats

def main():
    """Generate stats JSON file."""
    print("Calculating running statistics...")
    
    stats = calculate_yearly_stats()
    
    # Create generated directory if it doesn't exist
    os.makedirs('generated', exist_ok=True)
    
    # Save stats to JSON file
    with open('generated/stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Generated statistics for years: {', '.join(stats.keys())}")
    print("Stats saved to generated/stats.json")
    
    # Print sample data
    for year, year_stats in stats.items():
        print(f"\n{year} Summary:")
        print(f"  Activities: {year_stats['total_activities']}")
        print(f"  Distance: {year_stats['total_distance']} km")
        print(f"  Avg Pace: {year_stats['avg_pace']}")
        print(f"  Best Pace: {year_stats['best_pace']}")
        print(f"  Longest: {year_stats['longest_distance']}")

if __name__ == "__main__":
    main()