"""
Activity endpoints.

Read-only endpoints for querying activities from the database.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.auth import RequireAPIKey
from api.dependencies import DbSession
from db import crud

router = APIRouter()


# Pydantic schemas for API responses
class ActivityResponse(BaseModel):
    """Activity data returned by the API."""

    id: int
    platform: str
    external_id: str
    name: str
    activity_type: str
    sport_type: Optional[str] = None
    start_date: datetime
    elapsed_time_seconds: int
    moving_time_seconds: Optional[int] = None
    distance_meters: Optional[float] = None
    average_speed_mps: Optional[float] = None
    max_speed_mps: Optional[float] = None
    total_elevation_gain_meters: Optional[float] = None
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    calories: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Paginated list of activities."""

    items: list[ActivityResponse]
    total: int
    skip: int
    limit: int


@router.get("/activities", response_model=ActivityListResponse)
def list_activities(
    db: DbSession,
    _api_key: RequireAPIKey,
    platform: Optional[str] = Query(None, description="Filter by platform (strava, garmin)"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type (Run, Ride, etc.)"),
    since: Optional[datetime] = Query(None, description="Filter activities after this date"),
    until: Optional[datetime] = Query(None, description="Filter activities before this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
):
    """
    List activities with optional filters.

    Returns a paginated list of activities, ordered by start date (most recent first).
    """
    activities = crud.get_activities(
        db,
        platform=platform,
        activity_type=activity_type,
        since=since,
        until=until,
        skip=skip,
        limit=limit,
    )

    return ActivityListResponse(
        items=activities,
        total=len(activities),  # Note: This is items returned, not total count
        skip=skip,
        limit=limit,
    )


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: DbSession, _api_key: RequireAPIKey):
    """
    Get a specific activity by its database ID.
    """
    activity = crud.get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.get("/activities/platform/{platform}/{external_id}", response_model=ActivityResponse)
def get_activity_by_external_id(platform: str, external_id: str, db: DbSession, _api_key: RequireAPIKey):
    """
    Get a specific activity by its platform and external ID.

    Useful for looking up activities by their original platform ID.
    """
    activity = crud.get_activity_by_external_id(db, platform, external_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity
