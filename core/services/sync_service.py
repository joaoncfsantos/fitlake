"""
Data synchronization service.

Provides shared logic for syncing data from external platforms
to the database. Used by both CLI and API.
"""

from db.crud import upsert_activity, upsert_exercise_template, upsert_workout
from db.crud.daily_stats import upsert_daily_stat
from db.models import Activity, ExerciseTemplate, Workout
from db.database import get_db_session, init_db
from db.models.daily_stats import DailyStats


def sync_strava_activities(activities_data: list[dict]) -> int:
    """
    Sync Strava activities to the database.

    Args:
        activities_data: List of activity dicts from Strava API

    Returns:
        Number of activities synced
    """
    init_db()
    with get_db_session() as db:
        count = 0
        for data in activities_data:
            activity = Activity.from_strava(data)
            upsert_activity(db, activity)
            count += 1
    return count


def sync_garmin_daily_stats(daily_stats_data: list[dict]) -> int:
    """
    Sync Garmin daily stats to the database.

    Args:
        daily_stats_data: List of daily stats dicts from Garmin API

    Returns:
        Number of daily stats synced
    """
    init_db()
    with get_db_session() as db:
        count = 0
        for data in daily_stats_data:
            daily_stat = DailyStats.from_garmin(data)
            upsert_daily_stat(db, daily_stat)
            count += 1
    return count


def sync_hevy_workouts(workouts_data: list[dict]) -> int:
    """
    Sync Hevy workouts to the database.

    Args:
        workouts_data: List of workout dicts from Hevy API

    Returns:
        Number of workouts synced
    """
    init_db()
    with get_db_session() as db:
        count = 0
        for data in workouts_data:
            workout = Workout.from_hevy(data)
            upsert_workout(db, workout)
            count += 1
    return count


def sync_hevy_exercise_templates(templates_data: list[dict]) -> int:
    """
    Sync Hevy exercise templates to the database.

    Args:
        templates_data: List of exercise template dicts from Hevy API

    Returns:
        Number of templates synced
    """
    init_db()
    with get_db_session() as db:
        count = 0
        for data in templates_data:
            template = ExerciseTemplate.from_hevy(data)
            upsert_exercise_template(db, template)
            count += 1
    return count
