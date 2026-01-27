"""
CRUD (Create, Read, Update, Delete) operations for database models.

These functions provide a clean interface for database operations,
used by both the API and CLI.
"""

from .activities import (
    create_activity,
    get_activities,
    get_activity,
    get_activity_by_external_id,
    upsert_activity,
)
from .exercise_templates import (
    create_exercise_template,
    get_exercise_template,
    get_exercise_template_by_external_id,
    get_exercise_templates,
    upsert_exercise_template,
)
from .workouts import (
    create_workout,
    get_workout,
    get_workout_by_external_id,
    get_workouts,
    upsert_workout,
)

__all__ = [
    "create_activity",
    "get_activity",
    "get_activity_by_external_id",
    "get_activities",
    "upsert_activity",
    "create_exercise_template",
    "get_exercise_template",
    "get_exercise_template_by_external_id",
    "get_exercise_templates",
    "upsert_exercise_template",
    "create_workout",
    "get_workout",
    "get_workout_by_external_id",
    "get_workouts",
    "upsert_workout",
]
