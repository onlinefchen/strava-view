#!/usr/bin/env python3
"""
Generate config.js file with environment variables
This script creates the config.js file using environment variables for sensitive data.
"""

import os
import json
from dotenv import load_dotenv

def generate_config():
    """Generate config.js file from environment variables and template."""
    
    # Load environment variables if .env exists
    if os.path.exists('.env'):
        load_dotenv()
    
    # Get Mapbox token from environment
    mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN', 'your_mapbox_token_here')
    
    # Default configuration template
    config_template = {
        "MAPBOX_ACCESS_TOKEN": mapbox_token,
        "SIGNATURE": {
            "line1": "敢问路在何方，路在脚下",
            "line2": ""
        },
        "NAVIGATION_LINKS": {
            "summary": {
                "title": "Summary",
                "url": "summary.html",
                "target": "_self"
            },
            "blog": {
                "title": "Blog",
                "url": "https://your-blog.com",
                "target": "_blank"
            },
            "about": {
                "title": "About", 
                "url": "https://your-about-page.com",
                "target": "_blank"
            }
        }
    }
    
    # Load existing config.js to preserve custom settings
    existing_config = load_existing_config()
    if existing_config:
        # Merge with existing config, but always update the Mapbox token
        config_template.update(existing_config)
        config_template["MAPBOX_ACCESS_TOKEN"] = mapbox_token
    
    # Generate JavaScript config file
    config_js_content = f"""// Configuration file - Auto-generated by GitHub Actions
// DO NOT edit this file directly in production - use environment variables instead
const CONFIG = {json.dumps(config_template, indent=4)};"""
    
    # Write to config.js
    try:
        with open('config.js', 'w', encoding='utf-8') as f:
            f.write(config_js_content)
        print(f"✅ Generated config.js with Mapbox token")
        print(f"   Mapbox token: {mapbox_token[:20]}..." if len(mapbox_token) > 20 else f"   Mapbox token: {mapbox_token}")
        return True
    except Exception as e:
        print(f"❌ Failed to generate config.js: {e}")
        return False

def load_existing_config():
    """Load existing config.js file and parse its CONFIG object."""
    if not os.path.exists('config.js'):
        return None
    
    try:
        with open('config.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract CONFIG object using simple parsing
        # This is a basic implementation - in production you might want more robust parsing
        start_marker = 'const CONFIG = '
        end_marker = '};'
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return None
        
        start_idx += len(start_marker)
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            return None
        
        config_str = content[start_idx:end_idx + 1]
        
        # Parse JSON (this assumes the config is valid JSON)
        config_obj = json.loads(config_str)
        return config_obj
        
    except Exception as e:
        print(f"⚠️  Could not parse existing config.js: {e}")
        return None

def main():
    """Main function."""
    print("Generating config.js file...")
    success = generate_config()
    
    if success:
        print("✅ Config generation completed successfully")
        exit(0)
    else:
        print("❌ Config generation failed")
        exit(1)

if __name__ == "__main__":
    main()