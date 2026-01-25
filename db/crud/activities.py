"""
CRUD operations for Activity model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Activity


def create_activity(db: Session, activity: Activity) -> Activity:
    """
    Create a new activity in the database.

    Args:
        db: Database session
        activity: Activity instance to create

    Returns:
        The created activity with ID populated
    """
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_activity(db: Session, activity_id: int) -> Optional[Activity]:
    """
    Get an activity by its database ID.

    Args:
        db: Database session
        activity_id: The database ID

    Returns:
        Activity if found, None otherwise
    """
    return db.get(Activity, activity_id)


def get_activity_by_external_id(
    db: Session, platform: str, external_id: str
) -> Optional[Activity]:
    """
    Get an activity by its platform and external ID.

    Args:
        db: Database session
        platform: Platform name (e.g., "strava", "garmin")
        external_id: The ID from the external platform

    Returns:
        Activity if found, None otherwise
    """
    stmt = select(Activity).where(
        Activity.platform == platform,
        Activity.external_id == external_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_activities(
    db: Session,
    platform: Optional[str] = None,
    activity_type: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Activity]:
    """
    Get activities with optional filters.

    Args:
        db: Database session
        platform: Filter by platform (e.g., "strava", "garmin")
        activity_type: Filter by activity type (e.g., "Run", "Ride")
        since: Filter activities after this date
        until: Filter activities before this date
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of activities matching the filters
    """
    stmt = select(Activity).order_by(Activity.start_date.desc())

    if platform:
        stmt = stmt.where(Activity.platform == platform)
    if activity_type:
        stmt = stmt.where(Activity.activity_type == activity_type)
    if since:
        stmt = stmt.where(Activity.start_date >= since)
    if until:
        stmt = stmt.where(Activity.start_date <= until)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def upsert_activity(db: Session, activity: Activity) -> Activity:
    """
    Create or update an activity based on platform and external_id.

    If an activity with the same platform/external_id exists, it will be updated.
    Otherwise, a new activity will be created.

    Args:
        db: Database session
        activity: Activity instance with data to upsert

    Returns:
        The created or updated activity
    """
    existing = get_activity_by_external_id(db, activity.platform, activity.external_id)

    if existing:
        # Update existing activity
        for key, value in activity.__dict__.items():
            if not key.startswith("_") and key not in ("id", "created_at"):
                setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new activity
        return create_activity(db, activity)
