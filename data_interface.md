
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
