"""
CRUD operations for ExerciseTemplate model.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import ExerciseTemplate


def create_exercise_template(
    db: Session, template: ExerciseTemplate
) -> ExerciseTemplate:
    """
    Create a new exercise template in the database.

    Args:
        db: Database session
        template: ExerciseTemplate instance to create

    Returns:
        The created template with ID populated
    """
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_exercise_template(db: Session, template_id: int) -> Optional[ExerciseTemplate]:
    """
    Get an exercise template by its database ID.

    Args:
        db: Database session
        template_id: The database ID

    Returns:
        ExerciseTemplate if found, None otherwise
    """
    stmt = select(ExerciseTemplate).where(ExerciseTemplate.id == template_id)
    return db.execute(stmt).scalar_one_or_none()


def get_exercise_template_by_external_id(
    db: Session, platform: str, external_id: str
) -> Optional[ExerciseTemplate]:
    """
    Get an exercise template by its platform and external ID.

    Args:
        db: Database session
        platform: Platform name (e.g., "hevy")
        external_id: The ID from the external platform

    Returns:
        ExerciseTemplate if found, None otherwise
    """
    stmt = select(ExerciseTemplate).where(
        ExerciseTemplate.platform == platform,
        ExerciseTemplate.external_id == external_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_exercise_templates(
    db: Session,
    platform: Optional[str] = None,
    muscle_group: Optional[str] = None,
    equipment: Optional[str] = None,
    is_custom: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[ExerciseTemplate]:
    """
    Get exercise templates with optional filters.

    Args:
        db: Database session
        platform: Filter by platform (e.g., "hevy")
        muscle_group: Filter by primary muscle group
        equipment: Filter by equipment type
        is_custom: Filter by custom/default exercises
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of exercise templates matching the filters
    """
    stmt = select(ExerciseTemplate).order_by(ExerciseTemplate.title)

    if platform:
        stmt = stmt.where(ExerciseTemplate.platform == platform)
    if muscle_group:
        stmt = stmt.where(ExerciseTemplate.primary_muscle_group == muscle_group)
    if equipment:
        stmt = stmt.where(ExerciseTemplate.equipment == equipment)
    if is_custom is not None:
        stmt = stmt.where(ExerciseTemplate.is_custom == is_custom)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def upsert_exercise_template(
    db: Session, template: ExerciseTemplate
) -> ExerciseTemplate:
    """
    Create or update an exercise template based on platform and external_id.

    If a template with the same platform/external_id exists, it will be updated.

    Args:
        db: Database session
        template: ExerciseTemplate instance with data to upsert

    Returns:
        The created or updated exercise template
    """
    existing = get_exercise_template_by_external_id(
        db, template.platform, template.external_id
    )

    if existing:
        # Update existing template
        existing.title = template.title
        existing.exercise_type = template.exercise_type
        existing.primary_muscle_group = template.primary_muscle_group
        existing.secondary_muscle_groups = template.secondary_muscle_groups
        existing.equipment = template.equipment
        existing.is_custom = template.is_custom
        db.commit()
        db.refresh(existing)
        return existing

    # Create new template
    return create_exercise_template(db, template)
