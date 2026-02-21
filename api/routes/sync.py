"""
Sync endpoints.

Endpoints for syncing data from external platforms to the database.
"""

from fastapi import APIRouter

from api.auth import RequireAPIKey
from core.services.sync_service import sync_hevy_exercise_templates, sync_hevy_workouts, sync_strava_activities, sync_garmin_daily_stats
from db.crud import get_latest_activity_date
from db.database import get_db_session
import platforms.hevy as hevy
import platforms.strava as strava
import platforms.garmin as garmin

router = APIRouter()

@router.post("/sync/hevy")
def sync_hevy(_api_key: RequireAPIKey):
    """
    Sync Hevy data (exercise templates + workouts) to the database.
    """
    # Sync templates first
    templates = hevy.fetch_all_exercise_templates(hevy.get_api_key())
    templates_count = sync_hevy_exercise_templates(templates)
    
    # Then sync workouts
    workouts = hevy.fetch_all_workouts(hevy.get_api_key())
    workouts_count = sync_hevy_workouts(workouts)
    
    return {
        "message": "Hevy sync completed", 
        "synced_templates": templates_count,
        "synced_workouts": workouts_count
    }

@router.post("/sync/hevy/templates")
def sync_hevy_templates(_api_key: RequireAPIKey):
    """
    Sync Hevy exercise templates to the database.
    """
    templates = hevy.fetch_all_exercise_templates(hevy.get_api_key())
    count = sync_hevy_exercise_templates(templates)
    return {"message": "Hevy exercise templates sync completed", "synced": count}

@router.post("/sync/strava")
def sync_strava(_api_key: RequireAPIKey, light: bool = False):
    """
    Sync Strava data to the database.

    When `light=true`, only activities newer than the most recently stored
    activity are fetched (incremental sync). When `light=false` (default),
    all activities are fetched from Strava.
    """
    access_token = strava.get_access_token()

    if light:
        with get_db_session() as db:
            latest_date = get_latest_activity_date(db, "strava")
        if latest_date:
            activities = strava.fetch_activities_since(access_token, latest_date)
        else:
            # No data in DB yet — fall back to full sync
            activities = strava.fetch_all_activities(access_token)
    else:
        activities = strava.fetch_all_activities(access_token)

    count = sync_strava_activities(activities)
    return {"message": "Strava sync completed", "synced": count, "light": light}

@router.post("/sync/garmin")
def sync_garmin(_api_key: RequireAPIKey):
    """
    Sync Garmin daily stats to the database.
    """
    client = garmin.get_client()
    daily_stats = garmin.fetch_all_daily_stats(client)
    count = sync_garmin_daily_stats(daily_stats)
    return {"message": "Garmin sync completed", "synced": count}
