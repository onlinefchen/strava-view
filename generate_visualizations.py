#!/usr/bin/env python3
"""
Script to pre-generate clock and heatmap visualizations from Strava data.
This script processes activities.json and generates SVG visualizations.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
import math
import calendar
from timezone_config import parse_local_datetime, get_timezone_info

def load_activities(file_path='data/activities.json'):
    """Load activities from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return []

def generate_clock_visualization(activities, year=None, size=120):
    """Generate circular clock visualization matching strava_circular.svg format showing activity distribution by day of year."""
    if year is None:
        year = datetime.now().year
    
    # Create daily activity data structure
    from collections import defaultdict
    import calendar
    
    daily_data = defaultdict(float)
    
    # Filter activities by year and aggregate by date
    for activity in activities:
        try:
            # Use start_date_local with proper timezone handling
            start_time = parse_local_datetime(activity['start_date_local'])
            
            if start_time.year == year:
                date_str = start_time.strftime('%Y-%m-%d')
                distance_km = activity['distance'] / 1000
                daily_data[date_str] += distance_km
        except (ValueError, KeyError):
            continue
    
    # Calculate total distance
    total_distance = sum(daily_data.values())
    
    # Check if leap year
    is_leap_year = calendar.isleap(year)
    days_in_year = 366 if is_leap_year else 365
    
    # Generate SVG with configurable size
    svg_parts = [
        '<?xml version="1.0" encoding="utf-8" ?>',
        f'<svg baseProfile="full" height="{size}mm" version="1.1" viewBox="0,0,{size},{size}" width="{size}mm" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">',
        '<defs />',
        f'<rect fill="#222222" height="{size}" width="{size}" x="0" y="0" />'
    ]
    
    # Center coordinates and radii (scaled to size)
    center_x, center_y = size/2.0, size/2.0
    min_size = size
    outer_radius = 0.5 * min_size - 6  # 54.0
    inner_radius = outer_radius / 4     # 13.5
    
    # Calculate degrees per day
    df = 360.0 / days_in_year
    
    # Remove animations for cleaner display
    no_animate = ''
    
    # Center text - Year (larger font size)
    year_style = f"dominant-baseline: central; font-size:{min_size * 6.0 / 80.0}px; font-family:Arial;"
    svg_parts.append(f'<text alignment-baseline="middle" fill="#FFFFFF" style="{year_style}" text-anchor="middle" x="{center_x}" y="{center_y}">{year}</text>')
    
    # Top left - Distance (repositioned to top left, avoid circle overlap)
    distance_style = f"dominant-baseline: central; font-size:{min_size * 4.0 / 80.0}px; font-family:Arial;"
    svg_parts.append(f'<text alignment-baseline="middle" fill="#FFFFFF" style="{distance_style}" text-anchor="start" x="5" y="8">{total_distance:.0f} km</text>')
    
    # Generate daily segments following GitHubPoster logic
    day = 0
    date = datetime(year, 1, 1).date()
    
    # Find max distance for normalization
    max_distance = max(daily_data.values()) if daily_data.values() else 1
    
    while date.year == year:
        text_date = date.strftime('%Y-%m-%d')
        a1 = math.radians(day * df)
        a2 = math.radians((day + 1) * df)
        
        # Month markers and labels (first day of each month)
        if date.day == 1:
            (_, last_day) = calendar.monthrange(date.year, date.month)
            a3 = math.radians((day + last_day - 1) * df)
            sin_a1, cos_a1 = math.sin(a1), math.cos(a1)
            sin_a3, cos_a3 = math.sin(a3), math.cos(a3)
            r1 = outer_radius + 1
            r2 = outer_radius + 6
            r3 = outer_radius + 2
            
            # Month marker line
            line_x1 = center_x + r1 * sin_a1
            line_y1 = center_y - r1 * cos_a1  
            line_x2 = center_x + r2 * sin_a1
            line_y2 = center_y - r2 * cos_a1
            svg_parts.append(f'<line stroke="#FFFFFF" stroke-width="0.3" x1="{line_x1:.1f}" x2="{line_x2:.1f}" y1="{line_y1:.1f}" y2="{line_y2:.1f}"{no_animate}></line>')
            
            # Curved path for month name
            path_x = center_x + r3 * sin_a1
            path_y = center_y - r3 * cos_a1
            arc_dx = r3 * (sin_a3 - sin_a1)
            arc_dy = r3 * (cos_a1 - cos_a3)
            path_id = f"month{date.month}"
            svg_parts.append(f'<path d="M {path_x:.1f} {path_y:.1f} a{r3},{r3} 0 0,1 {arc_dx:.1f}, {arc_dy:.1f}" fill="none" id="{path_id}" stroke="none"{no_animate}></path>')
            
            # Month name on curved path
            month_style = f"font-size:{min_size * 3.75 / 80.0}px; font-family:Arial;"
            text_offset = 0.5 * r3 * (a3 - a1)
            svg_parts.append(f'<text fill="#FFFFFF" style="{month_style}" text-anchor="middle"><textPath startOffset="{text_offset:.1f}" xlink:href="#{path_id}">{date.strftime("%B")}</textPath></text>')
        
        # Draw activity segment if there's data for this date
        if text_date in daily_data:
            distance = daily_data[text_date]
            # Calculate radius based on activity intensity (matching GitHubPoster logic)
            intensity_ratio = distance / max_distance
            r1 = inner_radius
            r2 = inner_radius + (outer_radius - inner_radius) * intensity_ratio
            
            # Get color based on distance
            color = get_circular_hour_color(intensity_ratio)
            
            # Calculate path coordinates
            sin_a1, cos_a1 = math.sin(a1), math.cos(a1)
            sin_a2, cos_a2 = math.sin(a2), math.cos(a2)
            
            # Create segment path following GitHubPoster format
            start_x = center_x + r1 * sin_a1
            start_y = center_y - r1 * cos_a1
            
            path_data = f"M {start_x:.1f} {start_y:.1f}"
            path_data += f" l {(r2 - r1) * sin_a1:.1f} {(r1 - r2) * cos_a1:.1f}"
            path_data += f" a{r2},{r2} 0 0,0 {r2 * (sin_a2 - sin_a1):.1f},{r2 * (cos_a1 - cos_a2):.1f}"
            path_data += f" l {(r1 - r2) * sin_a2:.1f} {(r2 - r1) * cos_a2:.1f}"
            
            svg_parts.append(f'<path d="{path_data}" fill="{color}" stroke="none"></path>')
        
        day += 1
        date += timedelta(days=1)
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def get_circular_hour_color(intensity):
    """Get color for circular hour visualization based on intensity, using strava_circular.svg colors."""
    if intensity < 0.1:
        return '#4bddff'  # Light blue (low intensity)
    elif intensity < 0.3:
        return '#46fff6'  # Cyan (medium-low intensity)
    elif intensity < 0.5:
        return '#ffe200'  # Yellow (medium intensity)
    elif intensity < 0.7:
        return '#3effb2'  # Green (medium-high intensity)
    elif intensity < 0.9:
        return '#72ff27'  # Bright green (high intensity)
    else:
        return '#ffda00'  # Gold (maximum intensity)

def generate_heatmap_visualization(activities, year=None):
    """Generate Nike-style heatmap visualization."""
    # Initialize data structure
    if year:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
    else:
        # Use current year if no year specified
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)
    
    # Create date range
    date_data = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        date_data[date_str] = {'distance': 0, 'count': 0}
        current_date += timedelta(days=1)
    
    # Filter activities by year if specified
    filtered_activities = activities
    if year:
        temp_filtered = []
        for activity in activities:
            try:
                start_time = parse_local_datetime(activity['start_date_local'])
                
                if start_time.year == year:
                    temp_filtered.append(activity)
            except (ValueError, KeyError):
                continue
        filtered_activities = temp_filtered
    
    # Aggregate activity data
    for activity in filtered_activities:
        try:
            activity_date = parse_local_datetime(activity["start_date_local"])
            date_str = activity_date.strftime('%Y-%m-%d')
            if date_str in date_data:
                date_data[date_str]['distance'] += activity['distance'] / 1000  # Convert to km
                date_data[date_str]['count'] += 1
        except (ValueError, KeyError):
            continue
    
    # Generate SVG with larger size and internal labels
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg width="1200" height="280" viewBox="0 0 1200 280" xmlns="http://www.w3.org/2000/svg">',
        '  <style>',
        '    .heatmap-cell { rx: 3; }',
        '    .year-label { fill: #c9d1d9; font-size: 28px; font-family: Arial, sans-serif; font-weight: bold; }',
        '    .month-label { fill: #8b949e; font-size: 14px; font-family: Arial, sans-serif; text-anchor: middle; }',
        '  </style>'
    ]
    
    cell_size = 18
    gap = 3
    start_x = 25
    start_y = 80  # Leave space for year and month labels
    
    # Get current year for display
    display_year = year if year else datetime.now().year
    
    # Add year label
    svg_parts.append(f'  <text x="{start_x}" y="40" class="year-label">{display_year} Activity Heatmap</text>')
    
    # Add month labels
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for i, month_label in enumerate(month_labels):
        x = start_x + i * (cell_size + gap) * 4.5  # Approximate width per month
        svg_parts.append(f'  <text x="{x}" y="75" class="month-label">{month_label}</text>')
    
    # Group days by week
    weeks = []
    current_week = []
    
    for date_str in sorted(date_data.keys()):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date_obj.weekday()  # Monday = 0, Sunday = 6
        
        if day_of_week == 0 and current_week:  # Start of new week
            weeks.append(current_week)
            current_week = []
        
        current_week.append({
            'date': date_str,
            'data': date_data[date_str]
        })
    
    if current_week:
        weeks.append(current_week)
    
    # Draw heatmap cells
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            x = start_x + week_index * (cell_size + gap)
            y = start_y + day_index * (cell_size + gap)
            
            distance = day['data']['distance']
            color = get_heatmap_color(distance)
            
            svg_parts.append(f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" class="heatmap-cell">')
            svg_parts.append(f'    <title>{day["date"]}: {day["data"]["distance"]:.1f}km ({day["data"]["count"]} activities)</title>')
            svg_parts.append('  </rect>')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def generate_nike_style_heatmap(activities, year=None):
    """Generate Nike-style heatmap with same height as clock for summary page display."""
    if year is None:
        year = datetime.now().year
    
    # Create heatmap data structure
    date_data = {}
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        date_data[date_str] = {'distance': 0, 'count': 0}
        current_date += timedelta(days=1)
    
    # Filter activities by year if specified
    filtered_activities = activities
    if year:
        filtered_activities = [
            activity for activity in activities
            if parse_local_datetime(activity["start_date_local"]).year == year
        ]
    
    # Aggregate activity data
    for activity in filtered_activities:
        try:
            activity_date = parse_local_datetime(activity["start_date_local"])
            date_str = activity_date.strftime('%Y-%m-%d')
            if date_str in date_data:
                date_data[date_str]['distance'] += activity['distance'] / 1000  # Convert to km
                date_data[date_str]['count'] += 1
        except (ValueError, KeyError):
            continue
    
    # Calculate total distance
    total_distance = sum(day['distance'] for day in date_data.values())
    
    # Calculate optimal dimensions based on grid requirements
    # One year: ~53 weeks (horizontal) × 7 days (vertical)
    weeks_per_year = 53
    days_per_week = 7
    
    # Match clock size (120px) and design proper layout
    clock_size = 120  # Match the clock height exactly
    
    # Layout design from top to bottom:
    # 1. Year total distance (15px height)
    # 2. Month labels (12px height) 
    # 3. Activity grid (remaining space)
    # 4. Bottom margin (8px)
    
    distance_label_height = 15
    month_label_height = 12
    bottom_margin = 8
    side_margin = 10
    
    # Calculate available space for the grid
    available_grid_height = clock_size - distance_label_height - month_label_height - bottom_margin
    
    # Calculate optimal cell size based on available grid height
    cell_size = (available_grid_height - (days_per_week - 1) * 1) / days_per_week  # 1px gap
    gap = 1.0  # Fixed gap for clean appearance
    
    # Calculate actual grid dimensions
    grid_height = days_per_week * cell_size + (days_per_week - 1) * gap
    grid_width = weeks_per_year * cell_size + (weeks_per_year - 1) * gap
    
    # Calculate final SVG dimensions
    svg_width = grid_width + (side_margin * 2)
    svg_height = clock_size  # Exactly match clock height
    grid_width = weeks_per_year * cell_size + (weeks_per_year - 1) * gap
    
    # Generate SVG with calculated optimal dimensions (no units for pixel-based display)
    svg_parts = [
        '<?xml version="1.0" encoding="utf-8" ?>',
        f'<svg baseProfile="full" height="{svg_height}" version="1.1" viewBox="0,0,{svg_width},{svg_height}" width="{svg_width}" xmlns="http://www.w3.org/2000/svg">',
        '<defs />',
        f'<rect fill="#222222" height="{svg_height}" width="{svg_width}" x="0" y="0" />'
    ]
    
    # Layout positioning based on design
    # 1. Distance label at top
    distance_font_size = 11
    distance_y = 12
    distance_style = f"font-size:{distance_font_size}px; font-family:Arial; font-weight:bold;"
    svg_parts.append(f'<text fill="#FFFFFF" style="{distance_style}" text-anchor="start" x="{side_margin}" y="{distance_y}">{total_distance:.0f} km</text>')
    
    # 2. Grid positioning
    grid_start_x = side_margin
    grid_start_y = distance_label_height + month_label_height
    
    # Group days by week
    weeks = []
    current_week = []
    
    for date_str in sorted(date_data.keys()):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date_obj.weekday()  # Monday = 0, Sunday = 6
        
        if day_of_week == 0 and current_week:  # Start of new week
            weeks.append(current_week)
            current_week = []
        
        current_week.append({
            'date': date_str,
            'data': date_data[date_str]
        })
    
    if current_week:
        weeks.append(current_week)
    
    # Draw month labels
    month_starts = []
    current_month = None
    for week_index, week in enumerate(weeks):
        for day in week:
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            if current_month != date_obj.month:
                current_month = date_obj.month
                month_starts.append((week_index, date_obj.strftime('%b')))
                break
    
    # 3. Add month labels
    month_font_size = 9
    month_y = distance_label_height + month_label_height - 2
    month_style = f"font-size:{month_font_size}px; font-family:Arial;"
    for week_index, month_name in month_starts:
        if week_index < len(weeks):
            x = grid_start_x + week_index * (cell_size + gap)
            svg_parts.append(f'<text fill="#8b949e" style="{month_style}" text-anchor="start" x="{x:.1f}" y="{month_y}">{month_name}</text>')
    
    # 4. Draw heatmap cells in the grid area
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            x = grid_start_x + week_index * (cell_size + gap)
            y = grid_start_y + day_index * (cell_size + gap)
            
            distance = day['data']['distance']
            color = get_nike_heatmap_color(distance)
            
            # Use proportional rounded corners
            corner_radius = max(1, cell_size * 0.1)
            svg_parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size:.1f}" height="{cell_size:.1f}" fill="{color}" rx="{corner_radius:.1f}">')
            
            # Add tooltip
            if distance > 0:
                svg_parts.append(f'<title>{day["date"]}: {distance:.2f} km ({day["data"]["count"]} activities)</title>')
            else:
                svg_parts.append(f'<title>{day["date"]}</title>')
            
            svg_parts.append('</rect>')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def get_heatmap_color(distance):
    """Get Nike-style color for heatmap based on distance (matching GitHubPoster Nike colors)."""
    if distance == 0:
        return '#444444'  # No activity - dark gray
    elif distance < 1:
        return '#f4ec5e'  # Light activity - light yellow
    elif distance < 2:
        return '#f4ea5c'  # Low activity - yellow
    elif distance < 3:
        return '#fff300'  # Medium activity - bright yellow
    elif distance < 4:
        return '#ffef00'  # High activity - gold
    elif distance < 5:
        return '#ffe900'  # Very high activity - orange-yellow
    elif distance < 7:
        return '#ffeb00'  # Intense activity - orange
    else:
        return 'red'      # Maximum activity - Nike red (7km+)

def get_nike_heatmap_color(distance):
    """Get Nike-style color for heatmap based on distance (same as get_heatmap_color)."""
    return get_heatmap_color(distance)

def calculate_yearly_stats(activities, year=None):
    """Calculate yearly statistics."""
    # Filter activities by year if specified
    filtered_activities = activities
    if year:
        filtered_activities = [
            activity for activity in activities
            if parse_local_datetime(activity["start_date_local"]).year == year
        ]
    
    if not filtered_activities:
        return {
            'total_activities': 0,
            'total_distance': 0,
            'total_time': 0,
            'avg_pace': 0,
            'best_pace': 0,
            'avg_heart_rate': 0,
            'streak': 0
        }
    
    total_activities = len(filtered_activities)
    total_distance = sum(activity['distance'] for activity in filtered_activities) / 1000  # km
    total_time = sum(activity['moving_time'] for activity in filtered_activities)  # seconds
    
    # Calculate average pace (seconds per km)
    avg_pace = total_time / total_distance if total_distance > 0 else 0
    
    # Calculate best pace (fastest pace for runs > 1km)
    best_pace = float('inf')
    for activity in filtered_activities:
        if activity.get('moving_time') and activity.get('distance') and activity['distance'] > 1000:
            pace = activity['moving_time'] / (activity['distance'] / 1000)
            if pace < best_pace and pace > 180:  # Sanity check: pace should be > 3 minutes per km
                best_pace = pace
    best_pace = best_pace if best_pace != float('inf') else 0
    
    # Calculate average heart rate
    heart_rate_activities = [activity for activity in filtered_activities if activity.get('average_heartrate')]
    avg_heart_rate = (
        sum(activity['average_heartrate'] for activity in heart_rate_activities) / len(heart_rate_activities)
        if heart_rate_activities else 0
    )
    
    # Calculate streak
    streak = calculate_streak(filtered_activities)
    
    return {
        'total_activities': total_activities,
        'total_distance': total_distance,
        'total_time': total_time,
        'avg_pace': avg_pace,
        'best_pace': best_pace,
        'avg_heart_rate': avg_heart_rate,
        'streak': streak
    }

def calculate_streak(activities):
    """Calculate current activity streak."""
    if not activities:
        return 0
    
    # Get unique activity dates
    activity_dates = set()
    for activity in activities:
        try:
            activity_date = parse_local_datetime(activity["start_date_local"])
            activity_dates.add(activity_date.date())
        except (ValueError, KeyError):
            continue
    
    if not activity_dates:
        return 0
    
    # Sort dates in descending order
    sorted_dates = sorted(activity_dates, reverse=True)
    
    # Check if streak is current
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    if sorted_dates[0] != today and sorted_dates[0] != yesterday:
        return 0
    
    # Count consecutive days
    streak = 1
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i-1] - sorted_dates[i] == timedelta(days=1):
            streak += 1
        else:
            break
    
    return streak

def create_data_interface():
    """Create a simple data interface for future API integration."""
    interface_template = '''
# Data Interface

This file provides a template for integrating with external data sources.

## API Endpoints (for future implementation)

### Get Activities
- **Endpoint**: `/api/activities`
- **Method**: GET
- **Parameters**:
  - `year` (optional): Filter by year
  - `limit` (optional): Limit number of results
  - `offset` (optional): Pagination offset

### Get Statistics
- **Endpoint**: `/api/stats`
- **Method**: GET
- **Parameters**:
  - `year` (optional): Filter by year

### Update Activity Data
- **Endpoint**: `/api/activities/sync`
- **Method**: POST
- **Description**: Sync latest activity data from Strava

## Data Format

Activities should follow this JSON structure:
```json
{
  "id": "activity_id",
  "name": "Activity Name",
  "distance": 5000,
  "moving_time": 1800,
  "type": "Run",
  "start_date_local": "2025-01-01T08:00:00Z",
  "start_latlng": [31.113161, 121.588016],
  "end_latlng": [31.112855, 121.587645],
  "map": {
    "summary_polyline": "encoded_polyline_string"
  },
  "average_heartrate": 150,
  "average_speed": 2.78
}
```

## Environment Variables

Required environment variables:
- `MAPBOX_ACCESS_TOKEN`: Mapbox API token for map rendering
- `STRAVA_CLIENT_ID`: Strava API client ID (for future integration)
- `STRAVA_CLIENT_SECRET`: Strava API client secret (for future integration)
'''
    
    with open('data_interface.md', 'w', encoding='utf-8') as f:
        f.write(interface_template)

def main():
    """Main function to generate all visualizations."""
    print("Loading activities data...")
    activities = load_activities()
    
    if not activities:
        print("No activities found. Please ensure data/activities.json exists and contains valid data.")
        return
    
    print(f"Loaded {len(activities)} activities")
    
    # Get current year and available years
    current_year = datetime.now().year
    years = set()
    for activity in activities:
        try:
            activity_date = parse_local_datetime(activity["start_date_local"])
            years.add(activity_date.year)
        except (ValueError, KeyError):
            continue
    
    print(f"Found activities for years: {sorted(years)}")
    
    # Create output directory
    os.makedirs('generated', exist_ok=True)
    
    # Generate visualizations for each year and overall
    for year in sorted(years):
        print(f"Generating visualizations for {year}...")
        
        # Generate clock visualization with default size
        clock_svg = generate_clock_visualization(activities, year, size=120)
        with open(f'generated/clock_{year}.svg', 'w', encoding='utf-8') as f:
            f.write(clock_svg)
        
        # Generate heatmap visualization
        heatmap_svg = generate_heatmap_visualization(activities, year)
        with open(f'generated/heatmap_{year}.svg', 'w', encoding='utf-8') as f:
            f.write(heatmap_svg)
        
        # Generate Nike-style heatmap visualization
        nike_heatmap_svg = generate_nike_style_heatmap(activities, year)
        with open(f'generated/nike_heatmap_{year}.svg', 'w', encoding='utf-8') as f:
            f.write(nike_heatmap_svg)
        
        # Generate stats
        stats = calculate_yearly_stats(activities, year)
        with open(f'generated/stats_{year}.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
    
    # Generate overall visualizations
    print("Generating overall visualizations...")
    clock_svg = generate_clock_visualization(activities, size=120)
    with open('generated/clock_all.svg', 'w', encoding='utf-8') as f:
        f.write(clock_svg)
    
    heatmap_svg = generate_heatmap_visualization(activities)
    with open('generated/heatmap_all.svg', 'w', encoding='utf-8') as f:
        f.write(heatmap_svg)
    
    nike_heatmap_svg = generate_nike_style_heatmap(activities)
    with open('generated/nike_heatmap_all.svg', 'w', encoding='utf-8') as f:
        f.write(nike_heatmap_svg)
    
    stats = calculate_yearly_stats(activities)
    with open('generated/stats_all.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    # Create data interface documentation
    create_data_interface()
    
    print("Visualization generation complete!")
    print("Generated files:")
    print("- Clock visualizations: generated/clock_*.svg")
    print("- Heatmap visualizations: generated/heatmap_*.svg")
    print("- Nike-style heatmap visualizations: generated/nike_heatmap_*.svg")
    print("- Statistics: generated/stats_*.json")
    print("- Data interface documentation: data_interface.md")

if __name__ == "__main__":
    main()