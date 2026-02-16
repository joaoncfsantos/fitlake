"""
Daily stats endpoints.

Read-only endpoints for querying daily health stats from the database.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.auth import RequireAPIKey
from api.dependencies import DbSession
from db import crud
from db.models.daily_stats import DailyStats

router = APIRouter()


# Pydantic schemas for API responses
class DailyStatsResponse(BaseModel):
    """Daily stats data returned by the API."""

    id: int
    platform: str
    date: datetime
    steps: Optional[int] = None
    daily_step_goal: Optional[int] = None
    distance_meters: Optional[float] = None
    total_calories: Optional[float] = None
    active_calories: Optional[float] = None
    bmr_calories: Optional[float] = None
    wellness_calories: Optional[float] = None
    floors_ascended: Optional[int] = None
    floors_descended: Optional[int] = None
    min_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    average_stress_level: Optional[int] = None
    max_stress_level: Optional[int] = None
    stress_duration: Optional[int] = None
    rest_stress_duration: Optional[int] = None
    activity_stress_duration: Optional[int] = None
    low_stress_duration: Optional[int] = None
    medium_stress_duration: Optional[int] = None
    high_stress_duration: Optional[int] = None
    moderate_intensity_minutes: Optional[int] = None
    vigorous_intensity_minutes: Optional[int] = None
    intensity_minutes_goal: Optional[int] = None
    sleeping_seconds: Optional[int] = None
    deep_sleep_seconds: Optional[int] = None
    light_sleep_seconds: Optional[int] = None
    rem_sleep_seconds: Optional[int] = None
    awake_sleep_seconds: Optional[int] = None
    body_battery_charged_value: Optional[float] = None
    body_battery_drained_value: Optional[float] = None
    body_battery_highest_value: Optional[float] = None
    body_battery_lowest_value: Optional[float] = None

    class Config:
        from_attributes = True


class DailyStatsListResponse(BaseModel):
    """List of daily stats."""

    items: list[DailyStatsResponse]
    total: int


@router.get("/daily-stats", response_model=DailyStatsListResponse)
def list_daily_stats(
    db: DbSession,
    _api_key: RequireAPIKey,
    platform: Optional[str] = Query(None, description="Filter by platform (garmin)"),
    since: Optional[datetime] = Query(None, description="Filter stats after this date"),
    until: Optional[datetime] = Query(None, description="Filter stats before this date"),
    limit: int = Query(90, ge=1, le=365, description="Maximum number of records to return"),
):
    """
    List daily stats with optional filters.

    Returns a list of daily stats, ordered by date (most recent first).
    """
    query = db.query(DailyStats)
    
    if platform:
        query = query.filter(DailyStats.platform == platform)
    
    if since:
        query = query.filter(DailyStats.date >= since)
    
    if until:
        query = query.filter(DailyStats.date <= until)
    
    query = query.order_by(DailyStats.date.desc())
    query = query.limit(limit)
    
    daily_stats = query.all()

    return DailyStatsListResponse(
        items=daily_stats,
        total=len(daily_stats),
    )


@router.get("/daily-stats/{stat_id}", response_model=DailyStatsResponse)
def get_daily_stat(stat_id: int, db: DbSession, _api_key: RequireAPIKey):
    """
    Get a specific daily stat by its database ID.
    """
    daily_stat = db.query(DailyStats).filter(DailyStats.id == stat_id).first()
    if not daily_stat:
        raise HTTPException(status_code=404, detail="Daily stat not found")
    return daily_stat


@router.get("/daily-stats/date/{date}", response_model=DailyStatsResponse)
def get_daily_stat_by_date(
    date: datetime, 
    db: DbSession, 
    _api_key: RequireAPIKey,
    platform: str = Query("garmin", description="Platform to filter by"),
):
    """
    Get daily stats for a specific date.
    """
    daily_stat = crud.get_daily_stat_date(db, platform, date)
    if not daily_stat:
        raise HTTPException(status_code=404, detail="Daily stat not found for this date")
    return daily_stat
