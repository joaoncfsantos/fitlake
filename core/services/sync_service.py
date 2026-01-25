"""
Data synchronization service.

Provides shared logic for syncing data from external platforms
to the database. Used by both CLI and API.
"""

from sqlalchemy.orm import Session

from db.crud import upsert_activity, upsert_workout
from db.models import Activity, Workout


def sync_strava_activities(db: Session, activities_data: list[dict]) -> int:
    """
    Sync Strava activities to the database.

    Args:
        db: Database session
        activities_data: List of activity dicts from Strava API

    Returns:
        Number of activities synced
    """
    count = 0
    for data in activities_data:
        activity = Activity.from_strava(data)
        upsert_activity(db, activity)
        count += 1
    return count


def sync_garmin_activities(db: Session, activities_data: list[dict]) -> int:
    """
    Sync Garmin activities to the database.

    Args:
        db: Database session
        activities_data: List of activity dicts from Garmin API

    Returns:
        Number of activities synced
    """
    count = 0
    for data in activities_data:
        activity = Activity.from_garmin(data)
        upsert_activity(db, activity)
        count += 1
    return count


def sync_hevy_workouts(db: Session, workouts_data: list[dict]) -> int:
    """
    Sync Hevy workouts to the database.

    Args:
        db: Database session
        workouts_data: List of workout dicts from Hevy API

    Returns:
        Number of workouts synced
    """
    count = 0
    for data in workouts_data:
        workout = Workout.from_hevy(data)
        upsert_workout(db, workout)
        count += 1
    return count
