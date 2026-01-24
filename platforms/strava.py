#!/usr/bin/env python3
"""
Strava API client for fetching activity data.
https://developers.strava.com/docs/reference/
"""

import csv
import json
import os
import time
from typing import Any
import requests
from datetime import datetime

# API URLs
API_BASE_URL = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"

# API pagination
PAGE_SIZE = 30  # Strava default

# Token cache file
TOKEN_CACHE_FILE = "data/.strava_token_cache.json"


def get_client_credentials() -> tuple[str, str]:
    """Get Strava client ID and secret from environment variables."""
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError(
            "STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET not found.\n"
            "Please set them in your .env file or environment.\n"
            "Get these from: https://www.strava.com/settings/api"
        )
    return client_id, client_secret


def get_refresh_token() -> str:
    """Get Strava refresh token from environment variable."""
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
    if not refresh_token:
        raise ValueError(
            "STRAVA_REFRESH_TOKEN not found.\n"
            "Please set it in your .env file or environment.\n"
            "Run 'python cli.py strava auth' to get your tokens."
        )
    return refresh_token


def load_cached_token() -> dict[str, Any] | None:
    """
    Load the cached access token from file.
    
    Returns:
        Dict with 'access_token' and 'expires_at' if cache exists, None otherwise
    """
    try:
        with open(TOKEN_CACHE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_cached_token(access_token: str, expires_at: int) -> None:
    """
    Save the access token to cache file.
    
    Args:
        access_token: The OAuth2 access token
        expires_at: Unix timestamp when the token expires
    """
    os.makedirs(os.path.dirname(TOKEN_CACHE_FILE), exist_ok=True)
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump({
            "access_token": access_token,
            "expires_at": expires_at
        }, f)


def get_access_token(force_refresh: bool = False) -> str:
    """
    Get a valid Strava access token, using cache when possible.
    
    Checks if a cached token exists and is still valid (with 5 min buffer).
    If valid, returns the cached token. Otherwise, refreshes and caches a new one.
    
    Args:
        force_refresh: If True, bypass cache and always refresh
    
    Returns:
        A valid access token
    """
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached = load_cached_token()
        if cached:
            expires_at = cached.get("expires_at", 0)
            # Add 5 minute buffer before expiry
            if time.time() < (expires_at - 300):
                print("Using cached access token.")
                return cached["access_token"]
    
    # Need to refresh
    print("Refreshing Strava access token...")
    client_id, client_secret = get_client_credentials()
    refresh_token = get_refresh_token()
    
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    
    # Cache the new token
    access_token = data["access_token"]
    expires_at = data["expires_at"]
    save_cached_token(access_token, expires_at)
    
    # Notify if refresh token changed
    new_refresh_token = data.get("refresh_token")
    if new_refresh_token and new_refresh_token != refresh_token:
        print(f"Note: New refresh token received. Update STRAVA_REFRESH_TOKEN in your .env file:")
        print(f"  STRAVA_REFRESH_TOKEN={new_refresh_token}")
    
    return access_token



def _get_headers(access_token: str) -> dict[str, str]:
    """Build standard API headers."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


def fetch_activities_page(access_token: str, page: int, per_page: int = PAGE_SIZE) -> list[dict[str, Any]]:
    """
    Fetch a single page of activities from the API.
    
    Args:
        access_token: The OAuth2 access token
        page: Page number (1-indexed)
        per_page: Number of items per page (max 200)
    
    Returns:
        List of activity dicts
    """
    headers = _get_headers(access_token)
    params = {
        "page": page,
        "per_page": per_page,
    }
    
    response = requests.get(
        f"{API_BASE_URL}/athlete/activities",
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def fetch_all_activities(access_token: str) -> list[dict[str, Any]]:
    """
    Fetch all activities by iterating through all pages.
    
    Args:
        access_token: The OAuth2 access token
    
    Returns:
        List of all activity dicts
    """
    all_activities = []
    page = 1
    
    print("Fetching activities from Strava API...")
    
    while True:
        print(f"  Fetching page {page}...")
        activities = fetch_activities_page(access_token, page)
        
        if not activities:
            break
        
        all_activities.extend(activities)
        
        # If we got fewer than requested, we've reached the end
        if len(activities) < PAGE_SIZE:
            break
        
        page += 1
        
        # Rate limiting: Strava has a 100 requests per 15 minutes limit
        # and 1000 requests per day limit
        time.sleep(0.5)
    
    print(f"  Total activities fetched: {len(all_activities)}")
    return all_activities


def fetch_activity_by_id(access_token: str, activity_id: int) -> dict[str, Any]:
    """
    Fetch a specific activity by its ID.
    
    Args:
        access_token: The OAuth2 access token
        activity_id: The activity ID
    
    Returns:
        The detailed activity dict
    """
    headers = _get_headers(access_token)
    
    response = requests.get(
        f"{API_BASE_URL}/activities/{activity_id}",
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def fetch_athlete(access_token: str) -> dict[str, Any]:
    """
    Fetch the authenticated athlete's profile.
    
    Args:
        access_token: The OAuth2 access token
    
    Returns:
        The athlete profile dict
    """
    headers = _get_headers(access_token)
    
    response = requests.get(
        f"{API_BASE_URL}/athlete",
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def export_to_csv(activities: list[dict[str, Any]], filename: str = "strava_activities.csv"):
    """
    Export activities to a CSV file.
    
    Flattens the activity data for CSV format, handling nested objects.
    
    Args:
        activities: List of activity dicts
        filename: Output filename
    """
    if not activities:
        print("No activities to export.")
        return
    
    # Define CSV columns - these are the most useful fields from SummaryActivity
    columns = [
        "id",
        "name",
        "type",
        "sport_type",
        "start_date",
        "start_date_local",
        "timezone",
        "distance",
        "moving_time",
        "elapsed_time",
        "total_elevation_gain",
        "elev_high",
        "elev_low",
        "average_speed",
        "max_speed",
        "average_heartrate",
        "max_heartrate",
        "average_cadence",
        "average_watts",
        "max_watts",
        "weighted_average_watts",
        "kilojoules",
        "device_watts",
        "has_heartrate",
        "calories",
        "achievement_count",
        "kudos_count",
        "comment_count",
        "athlete_count",
        "photo_count",
        "trainer",
        "commute",
        "manual",
        "private",
        "gear_id",
        "start_latlng",
        "end_latlng",
        "workout_type",
        "upload_id",
        "external_id",
    ]
    
    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for activity in activities:
            row = {}
            for col in columns:
                value = activity.get(col)
                # Handle list values (like latlng)
                if isinstance(value, list):
                    row[col] = json.dumps(value)
                else:
                    row[col] = value
            writer.writerow(row)
    
    print(f"Exported {len(activities)} activities to {filename}")


def print_data_schema() -> None:
    """
    Print example data schema of activities.
    
    Displays the Strava activity structure with placeholder values.
    """
    # Example SummaryActivity structure from Strava API
    # Reference: https://developers.strava.com/docs/reference/#api-models-SummaryActivity
    example_summary = {
        "id": "<long>",
        "external_id": "<string>",
        "upload_id": "<long>",
        "athlete": {
            "id": "<long>",
            "resource_state": "<integer>"
        },
        "name": "<string>",
        "distance": "<float> (meters)",
        "moving_time": "<integer> (seconds)",
        "elapsed_time": "<integer> (seconds)",
        "total_elevation_gain": "<float> (meters)",
        "elev_high": "<float> (meters)",
        "elev_low": "<float> (meters)",
        "type": "<ActivityType: Run, Ride, Swim, etc.>",
        "sport_type": "<SportType: Run, MountainBikeRide, etc.>",
        "start_date": "<ISO 8601 datetime>",
        "start_date_local": "<ISO 8601 datetime>",
        "timezone": "<string>",
        "start_latlng": ["<latitude>", "<longitude>"],
        "end_latlng": ["<latitude>", "<longitude>"],
        "achievement_count": "<integer>",
        "kudos_count": "<integer>",
        "comment_count": "<integer>",
        "athlete_count": "<integer>",
        "photo_count": "<integer>",
        "total_photo_count": "<integer>",
        "map": {
            "id": "<string>",
            "polyline": "<encoded polyline | null>",
            "summary_polyline": "<encoded polyline>"
        },
        "trainer": "<boolean>",
        "commute": "<boolean>",
        "manual": "<boolean>",
        "private": "<boolean>",
        "flagged": "<boolean>",
        "workout_type": "<integer | null>",
        "average_speed": "<float> (meters/second)",
        "max_speed": "<float> (meters/second)",
        "has_kudoed": "<boolean>",
        "has_heartrate": "<boolean>",
        "average_heartrate": "<float | null>",
        "max_heartrate": "<integer | null>",
        "average_cadence": "<float | null>",
        "average_watts": "<float | null>",
        "max_watts": "<integer | null>",
        "weighted_average_watts": "<integer | null>",
        "kilojoules": "<float | null>",
        "device_watts": "<boolean>",
        "gear_id": "<string | null>",
        "calories": "<float>"
    }
    
    print("\n" + "=" * 80)
    print("STRAVA ACTIVITY DATA STRUCTURE (SummaryActivity):")
    print("=" * 80)
    print(json.dumps(example_summary, indent=2))
    print("\n" + "=" * 80)
    print("ACTIVITY TYPES:")
    print("=" * 80)
    print("""
Run, Ride, Swim, Hike, Walk, AlpineSki, BackcountrySki, Canoeing, Crossfit,
EBikeRide, Elliptical, Golf, Handcycle, IceSkate, InlineSkate, Kayaking,
Kitesurf, NordicSki, RockClimbing, RollerSki, Rowing, Sail, Skateboard,
Snowboard, Snowshoe, Soccer, StairStepper, StandUpPaddling, Surfing,
Velomobile, VirtualRide, VirtualRun, WeightTraining, Wheelchair, Windsurf,
Workout, Yoga
    """)
    print("\n" + "=" * 80)
    print("SPORT TYPES (more specific):")
    print("=" * 80)
    print("""
MountainBikeRide, GravelRide, EMountainBikeRide, TrailRun,
HighIntensityIntervalTraining, Pilates, Tennis, Badminton, Pickleball,
Squash, Racquetball, TableTennis, etc.
    """)


def get_latest_activities_csv() -> str:
    """
    Find the most recent strava_activities CSV file in data/exports.
    
    Returns:
        Path to the most recent CSV file
        
    Raises:
        FileNotFoundError: If no activity CSV files exist
    """
    import glob
    
    pattern = "data/exports/strava_activities_*.csv"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(
            "No activity data found. Run 'python cli.py strava sync' first."
        )
    
    # Sort by filename (which includes timestamp) and return the most recent
    return sorted(files)[-1]


def load_activities_from_csv(filename: str | None = None) -> list[dict[str, Any]]:
    """
    Load activities from a CSV file.
    
    Args:
        filename: Path to CSV file. If None, uses the most recent export.
        
    Returns:
        List of activity dicts
    """
    if filename is None:
        filename = get_latest_activities_csv()
    
    activities = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse JSON fields back to Python objects
            for field in ["start_latlng", "end_latlng"]:
                if row.get(field):
                    try:
                        row[field] = json.loads(row[field])
                    except (ValueError, json.JSONDecodeError):
                        row[field] = None
            
            # Convert numeric fields
            for field in ["distance", "moving_time", "elapsed_time", "total_elevation_gain",
                         "elev_high", "elev_low", "average_speed", "max_speed",
                         "average_heartrate", "max_heartrate", "average_cadence",
                         "average_watts", "max_watts", "weighted_average_watts",
                         "kilojoules", "calories", "achievement_count", "kudos_count",
                         "comment_count", "athlete_count", "photo_count"]:
                if row.get(field):
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        pass
            
            # Convert boolean fields
            for field in ["trainer", "commute", "manual", "private", "device_watts", "has_heartrate"]:
                if row.get(field):
                    row[field] = row[field].lower() == "true"
            
            activities.append(row)
    
    return activities


def get_detailed_activity(n: int, access_token: str) -> dict[str, Any] | None:
    """
    Get the nth activity with full details from the API (1-indexed).
    
    This fetches the DetailedActivity which includes calories and other
    fields not available in SummaryActivity.
    
    Args:
        n: The position of the activity (1 = most recent, 2 = second most recent, etc.)
        access_token: The OAuth2 access token
        
    Returns:
        The detailed activity dict if found, None otherwise
    """
    if n < 1:
        raise ValueError("n must be >= 1 (1-indexed)")
    
    # Fetch the nth activity from the API (page=n, per_page=1)
    print(f"Fetching activity #{n} from Strava API...")
    activities = fetch_activities_page(access_token, page=n, per_page=1)
    
    if not activities:
        print(f"Activity #{n} not found.")
        return None
    
    summary_activity = activities[0]
    activity_id = summary_activity.get('id')
    activity_name = summary_activity.get('name', 'Untitled')
    
    print(f"Fetching detailed activity: {activity_name} (ID: {activity_id})...")
    
    # Fetch the detailed activity from the API
    detailed_activity = fetch_activity_by_id(access_token, int(activity_id))
    return detailed_activity


def get_activities_since(days: int) -> list[dict[str, Any]]:
    """
    Get all activities from the past N days from locally synced data.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of activity dicts within the date range
    """
    from datetime import timedelta, timezone
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    activities = load_activities_from_csv()
    
    activities_in_range = []
    for activity in activities:
        start_time_str = activity.get("start_date")
        if not start_time_str:
            continue
        
        try:
            activity_date = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        
        if activity_date >= cutoff_date:
            activities_in_range.append(activity)
    
    print(f"Found {len(activities_in_range)} activities in the past {days} days")
    return activities_in_range


def print_activity_summary(activity: dict[str, Any]) -> None:
    """
    Print a formatted summary of an activity.
    
    Args:
        activity: The activity dict
    """
    print("\n" + "=" * 70)
    print(f"ACTIVITY: {activity.get('name', 'Untitled')}")
    print("=" * 70)
    
    # Basic info
    print(f"Type:          {activity.get('sport_type') or activity.get('type', 'Unknown')}")
    print(f"Date:          {activity.get('start_date_local', 'Unknown')}")
    
    # Distance and time
    distance_m = activity.get('distance', 0)
    distance_km = distance_m / 1000 if distance_m else 0
    print(f"Distance:      {distance_km:.2f} km ({distance_m:.0f} m)")
    
    moving_time = activity.get('moving_time', 0)
    if moving_time:
        hours, remainder = divmod(moving_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Moving Time:   {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    elapsed_time = activity.get('elapsed_time', 0)
    if elapsed_time:
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Elapsed Time:  {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    # Pace and Speed
    avg_speed = activity.get('average_speed', 0)
    if avg_speed:
        # Calculate pace (min/km)
        pace_min_per_km = 1000 / (avg_speed * 60)  # Convert m/s to min/km
        pace_minutes = int(pace_min_per_km)
        pace_seconds = int((pace_min_per_km - pace_minutes) * 60)
        print(f"Avg Pace:      {pace_minutes}:{pace_seconds:02d} min/km")

        # Calculate speed (km/h)
        avg_speed_kmh = avg_speed * 3.6
        print(f"Avg Speed:     {avg_speed_kmh:.1f} km/h ({avg_speed:.2f} m/s)")
    
    max_speed = activity.get('max_speed', 0)
    if max_speed:
        max_speed_kmh = max_speed * 3.6
        print(f"Max Speed:     {max_speed_kmh:.1f} km/h ({max_speed:.2f} m/s)")
    
    # Elevation
    elev_gain = activity.get('total_elevation_gain', 0)
    if elev_gain:
        print(f"Elevation Gain: {elev_gain:.0f} m")
    
    # Heart rate
    if activity.get('has_heartrate'):
        avg_hr = activity.get('average_heartrate')
        max_hr = activity.get('max_heartrate')
        if avg_hr:
            print(f"Avg HR:        {avg_hr:.0f} bpm")
        if max_hr:
            print(f"Max HR:        {max_hr:.0f} bpm")
    
    # Power (for cycling)
    avg_watts = activity.get('average_watts')
    if avg_watts:
        print(f"Avg Power:     {avg_watts:.0f} W")
        max_watts = activity.get('max_watts')
        if max_watts:
            print(f"Max Power:     {max_watts:.0f} W")
    
    # Calories
    calories = activity.get('calories', 0)
    if calories:
        print(f"Calories:      {calories:.0f} kcal")
    
    # Social
    print("-" * 70)
    print(f"Kudos: {activity.get('kudos_count', 0)} | "
          f"Comments: {activity.get('comment_count', 0)} | "
          f"Achievements: {activity.get('achievement_count', 0)}")
    print("=" * 70)


def print_auth_instructions() -> None:
    """Print instructions for authenticating with Strava."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      STRAVA AUTHENTICATION SETUP                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

To use the Strava integration, you need to:

1. CREATE A STRAVA API APPLICATION
   Go to: https://www.strava.com/settings/api
   
   Fill in:
   - Application Name: FitLake (or your choice)
   - Category: Data Analysis
   - Website: http://localhost
   - Authorization Callback Domain: localhost

2. GET YOUR CLIENT CREDENTIALS
   After creating the app, note down:
   - Client ID
   - Client Secret

3. ADD TO YOUR .env FILE
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret

4. GET YOUR REFRESH TOKEN
   Visit this URL in your browser (replace YOUR_CLIENT_ID):
   
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all

   After authorizing, you'll be redirected to:
   http://localhost?code=AUTHORIZATION_CODE
   
   Copy the AUTHORIZATION_CODE and run:
   
   curl -X POST https://www.strava.com/oauth/token \\
     -d client_id=YOUR_CLIENT_ID \\
     -d client_secret=YOUR_CLIENT_SECRET \\
     -d code=AUTHORIZATION_CODE \\
     -d grant_type=authorization_code

5. SAVE THE REFRESH TOKEN
   From the response, copy the refresh_token and add to .env:
   STRAVA_REFRESH_TOKEN=your_refresh_token

NOTE: The access_token expires every 6 hours, but the refresh_token is 
long-lived. The CLI will automatically refresh the access token when needed.

""")


def get_activity_stats(activities: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate aggregate statistics from a list of activities.
    
    Args:
        activities: List of activity dicts
        
    Returns:
        Dict with aggregate statistics
    """
    if not activities:
        return {}
    
    stats = {
        "total_activities": len(activities),
        "total_distance_m": 0,
        "total_moving_time_s": 0,
        "total_elapsed_time_s": 0,
        "total_elevation_gain_m": 0,
        "total_calories": 0,
        "by_type": {},
    }
    
    for activity in activities:
        stats["total_distance_m"] += float(activity.get("distance", 0) or 0)
        stats["total_moving_time_s"] += int(activity.get("moving_time", 0) or 0)
        stats["total_elapsed_time_s"] += int(activity.get("elapsed_time", 0) or 0)
        stats["total_elevation_gain_m"] += float(activity.get("total_elevation_gain", 0) or 0)
        stats["total_calories"] += float(activity.get("calories", 0) or 0)
        
        # Group by type
        activity_type = activity.get("sport_type") or activity.get("type", "Unknown")
        if activity_type not in stats["by_type"]:
            stats["by_type"][activity_type] = {
                "count": 0,
                "distance_m": 0,
                "moving_time_s": 0,
            }
        stats["by_type"][activity_type]["count"] += 1
        stats["by_type"][activity_type]["distance_m"] += float(activity.get("distance", 0) or 0)
        stats["by_type"][activity_type]["moving_time_s"] += int(activity.get("moving_time", 0) or 0)
    
    return stats


def print_activity_stats(stats: dict[str, Any], days: int | None = None) -> None:
    """
    Print formatted activity statistics.
    
    Args:
        stats: Statistics dict from get_activity_stats
        days: Optional number of days (for header)
    """
    if not stats:
        print("No statistics to display.")
        return
    
    print("\n" + "=" * 70)
    if days:
        print(f"ACTIVITY STATISTICS (Past {days} days)")
    else:
        print("ACTIVITY STATISTICS (All time)")
    print("=" * 70)
    
    print(f"Total Activities:    {stats['total_activities']}")
    print(f"Total Distance:      {stats['total_distance_m'] / 1000:.1f} km")
    
    hours, remainder = divmod(stats['total_moving_time_s'], 3600)
    minutes, _ = divmod(remainder, 60)
    print(f"Total Moving Time:   {int(hours)}h {int(minutes)}m")
    
    
    print("\n" + "-" * 70)
    print("BY ACTIVITY TYPE:")
    print("-" * 70)
    print(f"{'Type':<25} {'Count':>10} {'Distance (km)':>15} {'Time':>15}")
    print("-" * 70)
    
    for activity_type, type_stats in sorted(stats["by_type"].items(), 
                                            key=lambda x: x[1]["count"], 
                                            reverse=True):
        hours, remainder = divmod(type_stats["moving_time_s"], 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m"
        
        print(f"{activity_type:<25} {type_stats['count']:>10} "
              f"{type_stats['distance_m'] / 1000:>15.1f} {time_str:>15}")
    
    print("=" * 70)
