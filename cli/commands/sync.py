"""
Database sync commands for CLI.

These commands sync data from external APIs to the SQLite database.
They use the shared core services and do NOT import FastAPI.
"""

from db.database import get_db_session, init_db
from core.services import sync_service


def sync_strava_to_db(activities: list[dict]) -> int:
    """
    Sync Strava activities to the database.

    Args:
        activities: List of activity dicts from Strava API

    Returns:
        Number of activities synced
    """
    init_db()  # Ensure tables exist

    with get_db_session() as db:
        count = sync_service.sync_strava_activities(db, activities)
        print(f"  Synced {count} activities to database")
        return count


def sync_garmin_to_db(activities: list[dict]) -> int:
    """
    Sync Garmin activities to the database.

    Args:
        activities: List of activity dicts from Garmin API

    Returns:
        Number of activities synced
    """
    init_db()  # Ensure tables exist

    with get_db_session() as db:
        count = sync_service.sync_garmin_activities(db, activities)
        print(f"  Synced {count} activities to database")
        return count


def sync_hevy_to_db(workouts: list[dict]) -> int:
    """
    Sync Hevy workouts to the database.

    Args:
        workouts: List of workout dicts from Hevy API

    Returns:
        Number of workouts synced
    """
    init_db()  # Ensure tables exist

    with get_db_session() as db:
        count = sync_service.sync_hevy_workouts(db, workouts)
        print(f"  Synced {count} workouts to database")
        return count
