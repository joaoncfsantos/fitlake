"""
Workout endpoints.

Read-only endpoints for querying workouts from the database.
"""

import json
from collections import defaultdict
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


class MuscleDistributionItem(BaseModel):
    """Muscle group distribution data."""

    muscle_group: str
    weighted_sets: float
    percentage: float
    total_sets: int


class MuscleDistributionResponse(BaseModel):
    """Muscle distribution analytics."""

    muscle_distribution: list[MuscleDistributionItem]
    total_sets: int
    total_workouts: int
    primary_muscle_weight: float = 1.0
    secondary_muscle_weight: float = 0.5


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


@router.get("/workouts/muscle-distribution", response_model=MuscleDistributionResponse)
def get_muscle_distribution(
    db: DbSession,
    _api_key: RequireAPIKey,
    platform: Optional[str] = Query(None, description="Filter by platform (hevy)"),
    since: Optional[datetime] = Query(None, description="Filter workouts after this date"),
    until: Optional[datetime] = Query(None, description="Filter workouts before this date"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of workouts to analyze"),
):
    """
    Get muscle group distribution analytics across all workouts.

    Calculates weighted muscle group engagement where:
    - Primary muscles get weight 1.0
    - Secondary muscles get weight 0.5

    Returns aggregated statistics showing which muscle groups are trained most.
    """
    # Fetch workouts with exercises
    workouts = crud.get_workouts(
        db,
        platform=platform,
        since=since,
        until=until,
        skip=0,
        limit=limit,
    )

    # Fetch all exercise templates to map exercises to muscle groups
    exercise_templates = crud.get_exercise_templates(db, platform=platform, limit=10000)
    
    # Create lookup dict for templates
    templates_dict = {}
    for template in exercise_templates:
        templates_dict[template.external_id] = {
            "primary_muscle_group": template.primary_muscle_group,
            "secondary_muscle_groups": (
                json.loads(template.secondary_muscle_groups)
                if template.secondary_muscle_groups
                else []
            ),
        }

    # Calculate muscle distribution
    PRIMARY_MUSCLE_WEIGHT = 1.0
    SECONDARY_MUSCLE_WEIGHT = 0.5
    
    muscle_totals: defaultdict[str, dict] = defaultdict(
        lambda: {"weighted_sets": 0.0, "total_sets": 0}
    )
    total_sets = 0

    for workout in workouts:
        exercises = workout.exercises
        
        for exercise in exercises:
            exercise_template_id = exercise.get("exercise_template_id")
            sets = exercise.get("sets", [])
            num_sets = len(sets)
            total_sets += num_sets

            if exercise_template_id not in templates_dict:
                continue

            template = templates_dict[exercise_template_id]
            primary_muscle = template.get("primary_muscle_group")
            secondary_muscles = template.get("secondary_muscle_groups", [])

            if primary_muscle:
                muscle_totals[primary_muscle]["weighted_sets"] += (
                    num_sets * PRIMARY_MUSCLE_WEIGHT
                )
                muscle_totals[primary_muscle]["total_sets"] += num_sets

            for muscle in secondary_muscles:
                muscle_totals[muscle]["weighted_sets"] += (
                    num_sets * SECONDARY_MUSCLE_WEIGHT
                )
                # Don't count secondary muscle sets in total_sets to avoid double counting

    # Calculate percentages and create response
    total_weighted = sum(data["weighted_sets"] for data in muscle_totals.values())
    
    muscle_items = [
        MuscleDistributionItem(
            muscle_group=muscle,
            weighted_sets=data["weighted_sets"],
            percentage=(data["weighted_sets"] / total_weighted * 100) if total_weighted > 0 else 0,
            total_sets=data["total_sets"],
        )
        for muscle, data in muscle_totals.items()
    ]
    
    # Sort by weighted sets descending
    muscle_items.sort(key=lambda x: x.weighted_sets, reverse=True)

    return MuscleDistributionResponse(
        muscle_distribution=muscle_items,
        total_sets=total_sets,
        total_workouts=len(workouts),
        primary_muscle_weight=PRIMARY_MUSCLE_WEIGHT,
        secondary_muscle_weight=SECONDARY_MUSCLE_WEIGHT,
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
