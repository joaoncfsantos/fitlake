"""
Garmin Connect API client for fetching health and activity data.
https://github.com/cyberjunky/python-garminconnect
"""

from datetime import date, timedelta
from typing import Any

from garminconnect import Garmin


def get_user_start_date(client: Garmin) -> date:
    """Get the date of the user's oldest activity."""
    # Fetch oldest activity using ascending sort from a very old date
    activities = client.get_activities_by_date(
        startdate="2000-01-01",
        sortorder="asc"
    )
    
    if activities:
        oldest = activities[0]
        start_str = oldest.get("startTimeLocal", "")[:10]
        return date.fromisoformat(start_str)
    
    # Fallback if no activities
    return date.today()


def fetch_all_daily_stats(client: Garmin) -> list[dict[str, Any]]:
    """Fetch all daily stats from user's first activity to today."""
    start_date = get_user_start_date(client)
    return fetch_daily_stats_range(client, start_date, date.today())


def fetch_daily_stats(client: Garmin, target_date: date) -> dict[str, Any]:
    """
    Fetch daily health statistics for a specific date.

    Includes: steps, calories, heart rate, stress, floors, etc.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch stats for

    Returns:
        Dict containing daily statistics
    """
    date_str = target_date.isoformat()
    return client.get_stats(date_str)


def fetch_daily_stats_range(
    client: Garmin, start_date: date, end_date: date
) -> list[dict[str, Any]]:
    """
    Fetch daily stats for a date range.

    Args:
        client: Authenticated Garmin client
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        List of daily stats dicts
    """
    all_stats = []
    current_date = start_date

    while current_date <= end_date:
        try:
            stats = fetch_daily_stats(client, current_date)
            if stats:
                stats["date"] = current_date.isoformat()
                all_stats.append(stats)
        except Exception as e:
            print(f"  Warning: Could not fetch stats for {current_date}: {e}")

        current_date += timedelta(days=1)

    return all_stats


def fetch_sleep_data(client: Garmin, target_date: date) -> dict[str, Any] | None:
    """
    Fetch sleep data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch sleep data for

    Returns:
        Dict containing sleep data, or None if no data
    """
    date_str = target_date.isoformat()
    try:
        return client.get_sleep_data(date_str)
    except Exception:
        return None


def fetch_heart_rates(client: Garmin, target_date: date) -> dict[str, Any] | None:
    """
    Fetch heart rate data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch HR data for

    Returns:
        Dict containing heart rate data
    """
    date_str = target_date.isoformat()
    try:
        return client.get_heart_rates(date_str)
    except Exception:
        return None


def fetch_stress_data(client: Garmin, target_date: date) -> dict[str, Any] | None:
    """
    Fetch stress data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch stress data for

    Returns:
        Dict containing stress data
    """
    date_str = target_date.isoformat()
    try:
        return client.get_stress_data(date_str)
    except Exception:
        return None


def fetch_body_battery(client: Garmin, target_date: date) -> list[dict] | None:
    """
    Fetch body battery data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch body battery data for

    Returns:
        List of body battery readings
    """
    date_str = target_date.isoformat()
    try:
        return client.get_body_battery(date_str)
    except Exception:
        return None


def fetch_hrv_data(client: Garmin, target_date: date) -> dict[str, Any] | None:
    """
    Fetch HRV (Heart Rate Variability) data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch HRV data for

    Returns:
        Dict containing HRV data
    """
    date_str = target_date.isoformat()
    try:
        return client.get_hrv_data(date_str)
    except Exception:
        return None


def fetch_activities(
    client: Garmin, start: int = 0, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Fetch activities from Garmin Connect.

    Args:
        client: Authenticated Garmin client
        start: Starting index for pagination
        limit: Maximum number of activities to fetch

    Returns:
        List of activity dicts
    """
    return client.get_activities(start, limit)


def fetch_all_activities(client: Garmin, max_activities: int = 1000) -> list[dict[str, Any]]:
    """
    Fetch all activities by paginating through results.

    Args:
        client: Authenticated Garmin client
        max_activities: Maximum total activities to fetch (safety limit)

    Returns:
        List of all activity dicts
    """
    all_activities = []
    start = 0
    batch_size = 100

    print("Fetching activities from Garmin Connect...")

    while len(all_activities) < max_activities:
        print(f"  Fetching activities {start + 1} to {start + batch_size}...")
        activities = fetch_activities(client, start, batch_size)

        if not activities:
            break

        all_activities.extend(activities)

        if len(activities) < batch_size:
            break

        start += batch_size

    print(f"  Total activities fetched: {len(all_activities)}")
    return all_activities


def fetch_user_profile(client: Garmin) -> dict[str, Any]:
    """
    Fetch the user's profile information.

    Args:
        client: Authenticated Garmin client

    Returns:
        Dict containing user profile data
    """
    return client.get_full_name()


def fetch_user_settings(client: Garmin) -> dict[str, Any]:
    """
    Fetch user settings including units, goals, etc.

    Args:
        client: Authenticated Garmin client

    Returns:
        Dict containing user settings
    """
    return client.get_user_settings()


def fetch_training_readiness(client: Garmin, target_date: date) -> dict[str, Any] | None:
    """
    Fetch training readiness data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch data for

    Returns:
        Dict containing training readiness data
    """
    date_str = target_date.isoformat()
    try:
        return client.get_training_readiness(date_str)
    except Exception:
        return None


def fetch_training_status(client: Garmin, target_date: date) -> dict[str, Any] | None:
    """
    Fetch training status data for a specific date.

    Args:
        client: Authenticated Garmin client
        target_date: The date to fetch data for

    Returns:
        Dict containing training status data
    """
    date_str = target_date.isoformat()
    try:
        return client.get_training_status(date_str)
    except Exception:
        return None
