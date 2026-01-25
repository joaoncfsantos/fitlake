"""
CRUD operations for Workout model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db.models import Workout


def create_workout(db: Session, workout: Workout) -> Workout:
    """
    Create a new workout in the database.

    Args:
        db: Database session
        workout: Workout instance to create (including exercises and sets)

    Returns:
        The created workout with ID populated
    """
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


def get_workout(db: Session, workout_id: int) -> Optional[Workout]:
    """
    Get a workout by its database ID, including exercises and sets.

    Args:
        db: Database session
        workout_id: The database ID

    Returns:
        Workout if found, None otherwise
    """
    stmt = (
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(Workout.id == workout_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_workout_by_external_id(
    db: Session, platform: str, external_id: str
) -> Optional[Workout]:
    """
    Get a workout by its platform and external ID.

    Args:
        db: Database session
        platform: Platform name (e.g., "hevy")
        external_id: The ID from the external platform

    Returns:
        Workout if found, None otherwise
    """
    stmt = (
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(
            Workout.platform == platform,
            Workout.external_id == external_id,
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def get_workouts(
    db: Session,
    platform: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Workout]:
    """
    Get workouts with optional filters.

    Args:
        db: Database session
        platform: Filter by platform (e.g., "hevy")
        since: Filter workouts after this date
        until: Filter workouts before this date
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of workouts matching the filters
    """
    stmt = (
        select(Workout)
        .options(selectinload(Workout.exercises))
        .order_by(Workout.start_time.desc())
    )

    if platform:
        stmt = stmt.where(Workout.platform == platform)
    if since:
        stmt = stmt.where(Workout.start_time >= since)
    if until:
        stmt = stmt.where(Workout.start_time <= until)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def upsert_workout(db: Session, workout: Workout) -> Workout:
    """
    Create or update a workout based on platform and external_id.

    If a workout with the same platform/external_id exists, it will be
    deleted and recreated (simpler than updating nested relationships).

    Args:
        db: Database session
        workout: Workout instance with data to upsert

    Returns:
        The created or updated workout
    """
    existing = get_workout_by_external_id(db, workout.platform, workout.external_id)

    if existing:
        # Delete existing workout (cascade will delete exercises and sets)
        db.delete(existing)
        db.flush()

    # Create new workout
    return create_workout(db, workout)
