"""
Display and formatting functions for Strava data.
"""

import json
from typing import Any


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
        "athlete": {"id": "<long>", "resource_state": "<integer>"},
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
            "summary_polyline": "<encoded polyline>",
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
        "calories": "<float>",
    }

    print("\n" + "=" * 80)
    print("STRAVA ACTIVITY DATA STRUCTURE (SummaryActivity):")
    print("=" * 80)
    print(json.dumps(example_summary, indent=2))
    print("\n" + "=" * 80)
    print("ACTIVITY TYPES:")
    print("=" * 80)
    print(
        """
Run, Ride, Swim, Hike, Walk, AlpineSki, BackcountrySki, Canoeing, Crossfit,
EBikeRide, Elliptical, Golf, Handcycle, IceSkate, InlineSkate, Kayaking,
Kitesurf, NordicSki, RockClimbing, RollerSki, Rowing, Sail, Skateboard,
Snowboard, Snowshoe, Soccer, StairStepper, StandUpPaddling, Surfing,
Velomobile, VirtualRide, VirtualRun, WeightTraining, Wheelchair, Windsurf,
Workout, Yoga
    """
    )
    print("\n" + "=" * 80)
    print("SPORT TYPES (more specific):")
    print("=" * 80)
    print(
        """
MountainBikeRide, GravelRide, EMountainBikeRide, TrailRun,
HighIntensityIntervalTraining, Pilates, Tennis, Badminton, Pickleball,
Squash, Racquetball, TableTennis, etc.
    """
    )


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
    print(
        f"Type:          {activity.get('sport_type') or activity.get('type', 'Unknown')}"
    )
    print(f"Date:          {activity.get('start_date_local', 'Unknown')}")

    # Distance and time
    distance_m = activity.get("distance", 0)
    distance_km = distance_m / 1000 if distance_m else 0
    print(f"Distance:      {distance_km:.2f} km ({distance_m:.0f} m)")

    moving_time = activity.get("moving_time", 0)
    if moving_time:
        hours, remainder = divmod(moving_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Moving Time:   {int(hours)}h {int(minutes)}m {int(seconds)}s")

    elapsed_time = activity.get("elapsed_time", 0)
    if elapsed_time:
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Elapsed Time:  {int(hours)}h {int(minutes)}m {int(seconds)}s")

    # Pace and Speed
    avg_speed = activity.get("average_speed", 0)
    if avg_speed:
        # Calculate pace (min/km)
        pace_min_per_km = 1000 / (avg_speed * 60)  # Convert m/s to min/km
        pace_minutes = int(pace_min_per_km)
        pace_seconds = int((pace_min_per_km - pace_minutes) * 60)
        print(f"Avg Pace:      {pace_minutes}:{pace_seconds:02d} min/km")

        # Calculate speed (km/h)
        avg_speed_kmh = avg_speed * 3.6
        print(f"Avg Speed:     {avg_speed_kmh:.1f} km/h ({avg_speed:.2f} m/s)")

    max_speed = activity.get("max_speed", 0)
    if max_speed:
        max_speed_kmh = max_speed * 3.6
        print(f"Max Speed:     {max_speed_kmh:.1f} km/h ({max_speed:.2f} m/s)")

    # Elevation
    elev_gain = activity.get("total_elevation_gain", 0)
    if elev_gain:
        print(f"Elevation Gain: {elev_gain:.0f} m")

    # Heart rate
    if activity.get("has_heartrate"):
        avg_hr = activity.get("average_heartrate")
        max_hr = activity.get("max_heartrate")
        if avg_hr:
            print(f"Avg HR:        {avg_hr:.0f} bpm")
        if max_hr:
            print(f"Max HR:        {max_hr:.0f} bpm")

    # Power (for cycling)
    avg_watts = activity.get("average_watts")
    if avg_watts:
        print(f"Avg Power:     {avg_watts:.0f} W")
        max_watts = activity.get("max_watts")
        if max_watts:
            print(f"Max Power:     {max_watts:.0f} W")

    # Calories
    calories = activity.get("calories", 0)
    if calories:
        print(f"Calories:      {calories:.0f} kcal")

    # Social
    print("-" * 70)
    print(
        f"Kudos: {activity.get('kudos_count', 0)} | "
        f"Comments: {activity.get('comment_count', 0)} | "
        f"Achievements: {activity.get('achievement_count', 0)}"
    )
    print("=" * 70)


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

    hours, remainder = divmod(stats["total_moving_time_s"], 3600)
    minutes, _ = divmod(remainder, 60)
    print(f"Total Moving Time:   {int(hours)}h {int(minutes)}m")

    print("\n" + "-" * 70)
    print("BY ACTIVITY TYPE:")
    print("-" * 70)
    print(f"{'Type':<25} {'Count':>10} {'Distance (km)':>15} {'Time':>15}")
    print("-" * 70)

    for activity_type, type_stats in sorted(
        stats["by_type"].items(), key=lambda x: x[1]["count"], reverse=True
    ):
        hours, remainder = divmod(type_stats["moving_time_s"], 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m"

        print(
            f"{activity_type:<25} {type_stats['count']:>10} "
            f"{type_stats['distance_m'] / 1000:>15.1f} {time_str:>15}"
        )

    print("=" * 70)
