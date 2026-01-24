"""
Analysis functions for Strava activity data.
"""

from typing import Any


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
        stats["total_elevation_gain_m"] += float(
            activity.get("total_elevation_gain", 0) or 0
        )
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
        stats["by_type"][activity_type]["distance_m"] += float(
            activity.get("distance", 0) or 0
        )
        stats["by_type"][activity_type]["moving_time_s"] += int(
            activity.get("moving_time", 0) or 0
        )

    return stats
