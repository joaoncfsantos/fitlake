"""
Sleep data endpoints.

Read-only endpoints for querying sleep data from CSV exports.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.auth import RequireAPIKey
from platforms.garmin.storage import load_sleep_from_csv

router = APIRouter()


# Pydantic schemas for API responses
class SleepDataResponse(BaseModel):
    """Sleep data returned by the API."""

    date: str
    sleepTimeSeconds: Optional[float] = None
    napTimeSeconds: Optional[float] = None
    deepSleepSeconds: Optional[float] = None
    lightSleepSeconds: Optional[float] = None
    remSleepSeconds: Optional[float] = None
    awakeSleepSeconds: Optional[float] = None
    sleepStartTimestampLocal: Optional[float] = None
    sleepEndTimestampLocal: Optional[float] = None
    averageSpO2Value: Optional[float] = None
    lowestSpO2Value: Optional[float] = None
    averageRespirationValue: Optional[float] = None
    lowestRespirationValue: Optional[float] = None
    highestRespirationValue: Optional[float] = None
    avgHeartRate: Optional[float] = None
    sleepScores: Optional[str] = None


class SleepDataListResponse(BaseModel):
    """List of sleep data."""

    items: list[SleepDataResponse]
    total: int


@router.get("/sleep", response_model=SleepDataListResponse)
def list_sleep_data(
    _api_key: RequireAPIKey,
    limit: int = Query(90, ge=1, le=365, description="Maximum number of records to return"),
):
    """
    List sleep data from the most recent CSV export.

    Returns a list of sleep data, ordered by date (most recent first).
    """
    try:
        sleep_data = load_sleep_from_csv()
        
        # Reverse to get most recent first
        sleep_data = list(reversed(sleep_data))
        
        # Apply limit
        sleep_data = sleep_data[:limit]
        
        return SleepDataListResponse(
            items=[SleepDataResponse(**item) for item in sleep_data],
            total=len(sleep_data),
        )
    except FileNotFoundError as e:
        return SleepDataListResponse(items=[], total=0)


@router.get("/sleep/{date}", response_model=SleepDataResponse)
def get_sleep_by_date(
    date: str,
    _api_key: RequireAPIKey,
):
    """
    Get sleep data for a specific date.
    """
    try:
        sleep_data = load_sleep_from_csv()
        
        for item in sleep_data:
            if item.get("date") == date:
                return SleepDataResponse(**item)
        
        return SleepDataResponse(date=date)
    except FileNotFoundError as e:
        return SleepDataResponse(date=date)
