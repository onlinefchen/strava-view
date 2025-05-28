#!/usr/bin/env python3
"""
Timezone configuration module for FitFlow.
Reads timezone settings from config.js and provides utilities for timezone conversion.
"""

import json
import re
import os
from datetime import datetime, timezone, timedelta
from typing import Optional


def load_timezone_config() -> dict:
    """Load timezone configuration from config.js file."""
    config_file = 'config.js'
    if not os.path.exists(config_file):
        # Default to UTC+8 (Beijing time) if config not found
        return {'offset': 8, 'name': 'Asia/Shanghai'}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract TIMEZONE configuration from JavaScript
        timezone_match = re.search(r'"TIMEZONE":\s*{([^}]+)}', content)
        if timezone_match:
            timezone_content = timezone_match.group(1)
            
            # Extract offset
            offset_match = re.search(r'"offset":\s*(\d+)', timezone_content)
            offset = int(offset_match.group(1)) if offset_match else 8
            
            # Extract name (optional)
            name_match = re.search(r'"name":\s*"([^"]+)"', timezone_content)
            name = name_match.group(1) if name_match else 'Asia/Shanghai'
            
            return {'offset': offset, 'name': name}
    except Exception as e:
        print(f"Warning: Failed to load timezone config from {config_file}: {e}")
    
    # Default fallback
    return {'offset': 8, 'name': 'Asia/Shanghai'}


def get_local_timezone() -> timezone:
    """Get the configured local timezone as a timezone object."""
    config = load_timezone_config()
    offset_hours = config['offset']
    return timezone(timedelta(hours=offset_hours))


def parse_local_datetime(date_string: str) -> Optional[datetime]:
    """Parse datetime string handling both UTC and local timezone based on config."""
    if not date_string:
        return None
    
    try:
        if date_string.endswith('Z'):
            # If it has Z suffix, it's UTC time, convert to configured local timezone
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            local_tz = get_local_timezone()
            return dt.astimezone(local_tz)
        else:
            # Assume it's already local time
            return datetime.fromisoformat(date_string)
    except Exception as e:
        print(f"Warning: Failed to parse datetime '{date_string}': {e}")
        return None


def format_local_datetime(dt: datetime) -> str:
    """Format datetime in local timezone."""
    if not dt:
        return ""
    
    # Ensure datetime is in local timezone
    if dt.tzinfo is None:
        # Assume it's already in local timezone if no timezone info
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Convert to local timezone
        local_tz = get_local_timezone()
        local_dt = dt.astimezone(local_tz)
        return local_dt.strftime('%Y-%m-%d %H:%M:%S')


def get_timezone_info() -> dict:
    """Get current timezone configuration info."""
    config = load_timezone_config()
    tz = get_local_timezone()
    
    return {
        'offset': config['offset'],
        'name': config.get('name', 'Unknown'),
        'timezone_object': tz,
        'offset_string': f"UTC{'+' if config['offset'] >= 0 else ''}{config['offset']}"
    }


if __name__ == "__main__":
    # Test the timezone configuration
    info = get_timezone_info()
    print(f"Configured timezone: {info['name']} ({info['offset_string']})")
    
    # Test parsing
    test_utc = "2024-01-01T12:00:00Z"
    test_local = "2024-01-01T20:00:00"
    
    print(f"UTC time '{test_utc}' -> Local: {parse_local_datetime(test_utc)}")
    print(f"Local time '{test_local}' -> Parsed: {parse_local_datetime(test_local)}")