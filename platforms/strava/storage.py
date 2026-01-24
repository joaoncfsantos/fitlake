"""
CSV storage operations for Strava activity data.
"""

import csv
import glob
import json
from datetime import datetime, timedelta, timezone
from typing import Any


def export_to_csv(
    activities: list[dict[str, Any]], filename: str = "strava_activities.csv"
):
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
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
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


def get_latest_activities_csv() -> str:
    """
    Find the most recent strava_activities CSV file in data/exports.

    Returns:
        Path to the most recent CSV file

    Raises:
        FileNotFoundError: If no activity CSV files exist
    """
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
            for field in [
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
                "calories",
                "achievement_count",
                "kudos_count",
                "comment_count",
                "athlete_count",
                "photo_count",
            ]:
                if row.get(field):
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        pass

            # Convert boolean fields
            for field in [
                "trainer",
                "commute",
                "manual",
                "private",
                "device_watts",
                "has_heartrate",
            ]:
                if row.get(field):
                    row[field] = row[field].lower() == "true"

            activities.append(row)

    return activities


def get_activities_since(days: int) -> list[dict[str, Any]]:
    """
    Get all activities from the past N days from locally synced data.

    Args:
        days: Number of days to look back

    Returns:
        List of activity dicts within the date range
    """
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
