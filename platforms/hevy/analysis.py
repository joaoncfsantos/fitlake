"""
Analysis functions for Hevy workout data.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from .storage import (
    EXERCISE_TEMPLATES_CSV,
    get_nth_workout,
    get_workouts_since,
    load_exercise_templates_from_csv,
    load_workouts_from_csv,
)

# Muscle weights
PRIMARY_MUSCLE_WEIGHT = 1.0
SECONDARY_MUSCLE_WEIGHT = 0.5


def _calculate_workout_muscles(
    workout: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    verbose: bool = False,
) -> tuple[defaultdict[str, float], int]:
    """
    Calculate muscle group engagement for a single workout.

    This is the core calculation logic used by both single workout
    and multi-workout analysis functions.

    Args:
        workout: The workout dict from the API
        templates: Dict mapping template_id -> template data
        verbose: If True, print detailed info about each exercise

    Returns:
        Tuple of (muscle_totals dict, total_sets int)
    """
    muscle_totals: defaultdict[str, float] = defaultdict(float)
    total_sets = 0
    exercises = workout.get("exercises", [])

    for exercise in exercises:
        exercise_template_id = exercise.get("exercise_template_id")
        exercise_title = exercise.get("title", "Unknown Exercise")
        sets = exercise.get("sets", [])
        num_sets = len(sets)
        total_sets += num_sets

        if exercise_template_id not in templates:
            if verbose:
                print(
                    f"  Warning: Template not found for '{exercise_title}' (ID: {exercise_template_id})"
                )
            continue

        template = templates[exercise_template_id]
        primary_muscle = template.get("primary_muscle_group")
        secondary_muscles = template.get("secondary_muscle_groups", [])

        if verbose:
            print(f"  {exercise_title}: {num_sets} sets")
            print(f"    Primary: {primary_muscle} (+{num_sets * PRIMARY_MUSCLE_WEIGHT})")

        if primary_muscle:
            muscle_totals[primary_muscle] += num_sets * PRIMARY_MUSCLE_WEIGHT

        for muscle in secondary_muscles:
            muscle_totals[muscle] += num_sets * SECONDARY_MUSCLE_WEIGHT
            if verbose:
                print(f"    Secondary: {muscle} (+{num_sets * SECONDARY_MUSCLE_WEIGHT})")

    return muscle_totals, total_sets


def _aggregate_muscle_totals(
    aggregate: defaultdict[str, float], workout_totals: defaultdict[str, float]
) -> None:
    """Add workout muscle totals to the aggregate (in-place)."""
    for muscle, value in workout_totals.items():
        aggregate[muscle] += value


def analyze_workout_muscles(
    n: int, templates_file: str = EXERCISE_TEMPLATES_CSV
) -> tuple[defaultdict[str, float], int]:
    """
    Analyze muscle group engagement for the nth workout.

    Uses locally synced workout data (no API calls).

    Args:
        n: The workout number to analyze (1-indexed)
        templates_file: Path to the exercise templates CSV

    Returns:
        Tuple of (muscle_totals dict, total_sets int)
    """
    workout = get_nth_workout(n)
    if not workout:
        raise ValueError(f"Workout #{n} not found.")

    templates = load_exercise_templates_from_csv(templates_file)

    print(f"\nAnalyzing muscle groups for workout: {workout.get('title', 'Untitled')}")
    print("-" * 60)

    return _calculate_workout_muscles(workout, templates, verbose=True)


def analyze_muscles_for_period(
    days: int, templates_file: str = EXERCISE_TEMPLATES_CSV
) -> tuple[defaultdict[str, float], int, int]:
    """
    Analyze muscle group engagement for all workouts in the past N days.

    Uses locally synced workout data (no API calls).

    Args:
        days: Number of days to look back
        templates_file: Path to the exercise templates CSV

    Returns:
        Tuple of (muscle_totals dict, total_sets int, workout_count int)
    """
    workouts = get_workouts_since(days)
    templates = load_exercise_templates_from_csv(templates_file)

    aggregate_totals: defaultdict[str, float] = defaultdict(float)
    total_sets = 0

    print("-" * 60)
    for workout in workouts:
        workout_title = workout.get("title", "Untitled")
        start_time_str = workout.get("start_time", "")
        try:
            workout_date = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            date_str = workout_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            date_str = "Unknown"

        print(f"  [{date_str}] {workout_title}")

        workout_muscles, workout_sets = _calculate_workout_muscles(workout, templates)
        _aggregate_muscle_totals(aggregate_totals, workout_muscles)
        total_sets += workout_sets

    print("-" * 60)
    return aggregate_totals, total_sets, len(workouts)


def _get_workout_dates_from_csv(workouts: list[dict[str, Any]]) -> set[str]:
    """
    Extract all workout dates from loaded workout data.

    Args:
        workouts: List of workout dicts with 'start_time' field

    Returns:
        Set of date strings (YYYY-MM-DD) that have workouts
    """
    workout_dates = set()

    for workout in workouts:
        start_time_str = workout.get("start_time")
        if not start_time_str:
            continue

        try:
            workout_date = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            workout_dates.add(workout_date.strftime("%Y-%m-%d"))
        except (ValueError, TypeError):
            continue

    return workout_dates


def get_last_recovery_day() -> tuple[str | None, int]:
    """
    Find the most recent full recovery day (day with no workout).

    Uses locally synced workout data (no API calls).

    Returns:
        Tuple of (date string YYYY-MM-DD or None, days ago)
    """
    workouts = load_workouts_from_csv()
    workout_dates = _get_workout_dates_from_csv(workouts)

    today = datetime.now(timezone.utc).date()

    # Look back up to 365 days to find a recovery day
    max_lookback = 365

    # Start from yesterday (today might still have a workout later)
    for days_ago in range(1, max_lookback + 1):
        check_date = today - timedelta(days=days_ago)
        date_str = check_date.strftime("%Y-%m-%d")

        if date_str not in workout_dates:
            return date_str, days_ago

    return None, 0


def count_recovery_days(days: int) -> tuple[int, int, list[str]]:
    """
    Count the number of recovery days in the past N days.

    Uses locally synced workout data (no API calls).

    Args:
        days: Number of days to look back

    Returns:
        Tuple of (recovery_days count, workout_days count, list of recovery date strings)
    """
    workouts = load_workouts_from_csv()
    workout_dates = _get_workout_dates_from_csv(workouts)

    today = datetime.now(timezone.utc).date()

    recovery_dates = []
    # Check each day in the period (excluding today)
    for days_ago in range(1, days + 1):
        check_date = today - timedelta(days=days_ago)
        date_str = check_date.strftime("%Y-%m-%d")

        if date_str not in workout_dates:
            recovery_dates.append(date_str)

    workout_count = days - len(recovery_dates)
    return len(recovery_dates), workout_count, recovery_dates
