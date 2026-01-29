"""
Sync endpoints.

Endpoints for syncing data from external platforms to the database.
"""

from fastapi import APIRouter

from api.auth import RequireAPIKey
from core.services.sync_service import  sync_hevy_exercise_templates, sync_hevy_workouts, sync_strava_activities, sync_garmin_daily_stats
import platforms.hevy as hevy
import platforms.strava as strava
import platforms.garmin as garmin

router = APIRouter()

@router.post("/sync/hevy")
def sync_hevy(_api_key: RequireAPIKey):
    """
    Sync Hevy data to the database.
    """
    workouts = hevy.fetch_all_workouts(hevy.get_api_key())
    count = sync_hevy_workouts(workouts)
    return {"message": "Hevy sync completed", "synced": count}

@router.post("/sync/hevy/templates")
def sync_hevy_templates(_api_key: RequireAPIKey):
    """
    Sync Hevy exercise templates to the database.
    """
    templates = hevy.fetch_all_exercise_templates(hevy.get_api_key())
    count = sync_hevy_exercise_templates(templates)
    return {"message": "Hevy exercise templates sync completed", "synced": count}

@router.post("/sync/strava")
def sync_strava(_api_key: RequireAPIKey):
    """
    Sync Strava data to the database.
    """
    activities = strava.fetch_all_activities(strava.get_access_token())
    count = sync_strava_activities(activities)
    return {"message": "Strava sync completed", "synced": count}

@router.post("/sync/garmin")
def sync_garmin(_api_key: RequireAPIKey):
    """
    Sync Garmin daily stats to the database.
    """
    client = garmin.get_client()
    daily_stats = garmin.fetch_all_daily_stats(client)
    count = sync_garmin_daily_stats(daily_stats)
    return {"message": "Garmin sync completed", "synced": count}
