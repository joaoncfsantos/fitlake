"""
SQLAlchemy models for FitLake.

All models should be imported here so they are registered
with Base.metadata when init_db() is called.
"""

from .activity import Activity
from .exercise_template import ExerciseTemplate
from .workout import Workout, WorkoutExercise, WorkoutSet

__all__ = ["Activity", "ExerciseTemplate", "Workout", "WorkoutExercise", "WorkoutSet"]
