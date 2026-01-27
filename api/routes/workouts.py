"""
Workout endpoints.

Read-only endpoints for querying workouts from the database.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.auth import RequireAPIKey
from api.dependencies import DbSession
from db import crud

router = APIRouter()
    

class WorkoutResponse(BaseModel):
    """Workout data returned by the API."""

    id: int
    platform: str
    external_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    exercises: list[dict] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutSummaryResponse(BaseModel):
    """Summary workout data (without exercises) for list views."""

    id: int
    platform: str
    external_id: str
    title: str
    start_time: datetime
    duration_seconds: int
    exercise_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutListResponse(BaseModel):
    """Paginated list of workouts."""

    items: list[WorkoutSummaryResponse]
    total: int
    skip: int
    limit: int


@router.get("/workouts", response_model=WorkoutListResponse)
def list_workouts(
    db: DbSession,
    _api_key: RequireAPIKey,
    platform: Optional[str] = Query(None, description="Filter by platform (hevy)"),
    since: Optional[datetime] = Query(None, description="Filter workouts after this date"),
    until: Optional[datetime] = Query(None, description="Filter workouts before this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
):
    """
    List workouts with optional filters.

    Returns a paginated list of workout summaries, ordered by start time (most recent first).
    """
    workouts = crud.get_workouts(
        db,
        platform=platform,
        since=since,
        until=until,
        skip=skip,
        limit=limit,
    )

    # Convert to summary responses
    summaries = [
        WorkoutSummaryResponse(
            id=w.id,
            platform=w.platform,
            external_id=w.external_id,
            title=w.title,
            start_time=w.start_time,
            duration_seconds=w.duration_seconds,
            exercise_count=len(w.exercises),
            created_at=w.created_at,
        )
        for w in workouts
    ]

    return WorkoutListResponse(
        items=summaries,
        total=len(summaries),
        skip=skip,
        limit=limit,
    )


@router.get("/workouts/{workout_id}", response_model=WorkoutResponse)
def get_workout(workout_id: int, db: DbSession, _api_key: RequireAPIKey):
    """
    Get a specific workout by its database ID.

    Includes all exercises and sets.
    """
    workout = crud.get_workout(db, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.get("/workouts/platform/{platform}/{external_id}", response_model=WorkoutResponse)
def get_workout_by_external_id(platform: str, external_id: str, db: DbSession, _api_key: RequireAPIKey):
    """
    Get a specific workout by its platform and external ID.

    Useful for looking up workouts by their original platform ID.
    """
    workout = crud.get_workout_by_external_id(db, platform, external_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout
