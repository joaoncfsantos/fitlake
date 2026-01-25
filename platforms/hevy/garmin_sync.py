"""
Sync Hevy workouts to Garmin Connect by generating FIT files.
"""

import os
from datetime import datetime
from typing import Any

from ..hevy.storage import load_workouts_from_csv, load_exercise_templates_from_csv


def is_cardio_only_workout(workout: dict[str, Any], exercise_templates: dict[str, dict]) -> bool:
    """
    Check if a workout contains only one exercise and it's a cardio exercise.
    
    Args:
        workout: The workout dict with exercises
        exercise_templates: Dict of exercise templates keyed by ID
        
    Returns:
        True if workout has exactly 1 exercise and it's cardio type
    """
    exercises = workout.get("exercises", [])
    
    # Check if there's exactly 1 exercise
    if len(exercises) != 1:
        return False
    
    # Get the exercise template ID
    exercise = exercises[0]
    template_id = exercise.get("exercise_template_id")
    
    if not template_id or template_id not in exercise_templates:
        return False
    
    # Check if primary muscle group is "cardio"
    template = exercise_templates[template_id]
    return template.get("primary_muscle_group") == "cardio"


def filter_workouts_for_garmin(workouts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filter out cardio-only workouts from the list.
    
    Args:
        workouts: List of all workouts
        
    Returns:
        List of workouts suitable for Garmin strength training import
    """
    # Load exercise templates to check types
    exercise_templates = load_exercise_templates_from_csv()
    
    filtered = []
    excluded_count = 0
    
    for workout in workouts:
        if is_cardio_only_workout(workout, exercise_templates):
            excluded_count += 1
            print(f"  Excluding cardio-only workout: {workout.get('title', 'Untitled')} ({workout.get('start_time')})")
        else:
            filtered.append(workout)
    
    print(f"\nFiltered {len(filtered)} workouts for Garmin import (excluded {excluded_count} cardio-only)")
    return filtered


def export_filtered_workouts(output_filename: str | None = None) -> str:
    """
    Export filtered workouts (excluding cardio-only) to a new CSV file.
    
    Args:
        output_filename: Optional custom output filename
        
    Returns:
        Path to the exported file
    """
    from ..hevy.storage import export_to_csv
    
    # Load all workouts
    workouts = load_workouts_from_csv()
    print(f"Loaded {len(workouts)} total workouts from CSV")
    
    # Filter out cardio-only workouts
    filtered_workouts = filter_workouts_for_garmin(workouts)
    
    # Generate output filename if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"data/exports/hevy_workouts_for_garmin_{timestamp}.csv"
    
    # Export to CSV
    export_to_csv(filtered_workouts, output_filename)
    
    return output_filename
