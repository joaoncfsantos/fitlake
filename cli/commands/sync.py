"""
Database sync commands for CLI.

These commands sync data from external APIs to the SQLite database.
They use the shared core services and do NOT import FastAPI.
"""

from core.services import sync_service


def sync_strava_to_db(activities: list[dict]) -> int:
    """
    Sync Strava activities to the database.

    Args:
        activities: List of activity dicts from Strava API

    Returns:
        Number of activities synced
    """
    count = sync_service.sync_strava_activities(activities)
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
    count = sync_service.sync_garmin_activities(activities)
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
    count = sync_service.sync_hevy_workouts(workouts)
    print(f"  Synced {count} workouts to database")
    return count


def sync_hevy_templates_to_db(templates: list[dict]) -> int:
    """
    Sync Hevy exercise templates to the database.

    Args:
        templates: List of exercise template dicts from Hevy API

    Returns:
        Number of templates synced
    """
    count = sync_service.sync_hevy_exercise_templates(templates)
    print(f"  Synced {count} exercise templates to database")
    return count
