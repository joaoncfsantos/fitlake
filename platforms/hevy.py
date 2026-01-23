#!/usr/bin/env python3
"""
Hevy API client for fetching workout data.
https://api.hevyapp.com/docs/#/
"""

import csv
import json
import os
from typing import Any
import requests
from datetime import datetime
from collections import defaultdict

# API URLs
API_BASE_URL = "https://api.hevyapp.com/v1/workouts"
EXERCISE_TEMPLATES_URL = "https://api.hevyapp.com/v1/exercise_templates"

# API pagination
PAGE_SIZE = 10
TEMPLATES_PAGE_SIZE = 100

# CSV filenames
EXERCISE_TEMPLATES_CSV = "data/exercise_templates.csv"

# Muscle weights
PRIMARY_MUSCLE_WEIGHT = 1.0
SECONDARY_MUSCLE_WEIGHT = 0.5

def get_api_key() -> str:
    """Get Hevy API key from environment variable."""
    api_key = os.getenv("HEVY_API_KEY")
    if not api_key:
        raise ValueError(
            "HEVY_API_KEY not found. Please set it in your .env file or environment."
        )
    return api_key

def _get_headers(api_key: str) -> dict[str, str]:
    """Build standard API headers."""
    return {
        "api-key": api_key,
        "Accept": "application/json",
    }


def fetch_workouts_page(api_key: str, page: int) -> dict[str, Any]:
    """Fetch a single page of workouts from the API."""
    headers = _get_headers(api_key)
    params = {
        "page": page,
        "pageSize": PAGE_SIZE,
    }
    
    response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_all_workouts(api_key: str) -> list[dict[str, Any]]:
    """Fetch all workouts by iterating through all pages."""
    all_workouts = []
    page = 1
    
    print("Fetching workouts from Hevy API...")
    
    while True:
        print(f"  Fetching page {page}...")
        data = fetch_workouts_page(api_key, page)
        
        workouts = data.get("workouts", [])
        if not workouts:
            break
            
        all_workouts.extend(workouts)
        
        # Check if there are more pages
        page_count = data.get("page_count", 1)
        if page >= page_count:
            break
            
        page += 1
    
    print(f"  Total workouts fetched: {len(all_workouts)}")
    return all_workouts


def fetch_nth_workout(api_key: str, n: int) -> dict[str, Any] | None:
    """
    Fetch the nth workout from the API (1-indexed).
    
    Uses pageSize=1 and page=n to efficiently fetch only the single workout
    at position n, minimizing data transfer.
    
    Args:
        api_key: The API key for authentication
        n: The position of the workout to fetch (1 = first workout, 2 = second, etc.)
    
    Returns:
        The workout dict if found, None otherwise
    """
    if n < 1:
        raise ValueError("n must be >= 1 (1-indexed)")
    
    headers = _get_headers(api_key)
    # Use pageSize=1 and page=n to fetch exactly the nth workout
    params = {
        "page": n,
        "pageSize": 1,
    }
    
    print(f"Fetching workout #{n} (using pageSize=1, page={n})...")
    
    response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    workouts = data.get("workouts", [])
    page_count = data.get("page_count", 0)
    
    if not workouts:
        print(f"Workout #{n} not found. Total workouts available: {page_count}")
        return None
    
    workout = workouts[0]
    print(f"Found workout: {workout.get('title', 'Untitled')} (total: {page_count} workouts)")
    return workout


def flatten_workout(workout: dict[str, Any]) -> dict[str, Any]:
    """Flatten a workout object for CSV export."""
    # Extract base workout info
    flat = {
        "id": workout.get("id"),
        "title": workout.get("title"),
        "description": workout.get("description", ""),
        "start_time": workout.get("start_time"),
        "end_time": workout.get("end_time"),
        "created_at": workout.get("created_at"),
        "updated_at": workout.get("updated_at"),
    }
    
    # Calculate duration if times are available
    if flat["start_time"] and flat["end_time"]:
        try:
            start = datetime.fromisoformat(flat["start_time"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(flat["end_time"].replace("Z", "+00:00"))
            duration_minutes = (end - start).total_seconds() / 60
            flat["duration_minutes"] = round(duration_minutes, 2)
        except (ValueError, TypeError):
            flat["duration_minutes"] = None
    else:
        flat["duration_minutes"] = None
    
    # Count exercises
    exercises = workout.get("exercises", [])
    flat["exercise_count"] = len(exercises)
    
    # List exercise names
    exercise_names = [ex.get("title", "") for ex in exercises]
    flat["exercises"] = "; ".join(exercise_names)
    
    # Calculate total sets
    total_sets = sum(len(ex.get("sets", [])) for ex in exercises)
    flat["total_sets"] = total_sets
    
    return flat


def export_to_csv(workouts: list[dict[str, Any]], filename: str = "hevy_workouts.csv"):
    """Export workouts to a CSV file."""
    if not workouts:
        print("No workouts to export.")
        return
    
    # Flatten all workouts
    flat_workouts = [flatten_workout(w) for w in workouts]
    
    # Get all unique keys for CSV headers
    headers = list(flat_workouts[0].keys())
    
    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flat_workouts)
    
    print(f"Exported {len(flat_workouts)} workouts to {filename}")


def print_data_structures(api_key: str, n: int = 1) -> None:
    """
    Print the original and flattened data structures for the nth workout.
    
    Efficiently fetches only the single workout at position n using
    pageSize=1 and page=n, then displays both the original API response
    and the flattened version.
    
    Args:
        api_key: The API key for authentication
        n: The position of the workout to fetch (1 = first, default)
    """
    workout = fetch_nth_workout(api_key, n)
    
    if not workout:
        print("No workout to display.")
        return
    
    # Print original data structure from API
    print("\n" + "=" * 80)
    print(f"ORIGINAL DATA STRUCTURE (workout #{n} from API):")
    print("=" * 80)
    print(json.dumps(workout, indent=2, default=str))
    
    # Print flattened data structure
    print("\n" + "=" * 80)
    print(f"FLATTENED DATA STRUCTURE (workout #{n}, ready for CSV):")
    print("=" * 80)
    flat_workout = flatten_workout(workout)
    print(json.dumps(flat_workout, indent=2, default=str))
    print("=" * 80 + "\n")


def fetch_all_exercise_templates(api_key: str) -> list[dict[str, Any]]:
    """
    Fetch all exercise templates from the Hevy API.
    
    Iterates through all pages (100 templates per page) until all
    templates are retrieved.
    
    Args:
        api_key: The API key for authentication
        
    Returns:
        List of all exercise template dicts
    """
    all_templates = []
    page = 1
    
    headers = _get_headers(api_key)
    
    print("Fetching exercise templates from Hevy API...")
    
    while True:
        print(f"  Fetching page {page}...")
        params = {
            "page": page,
            "pageSize": TEMPLATES_PAGE_SIZE,
        }
        
        response = requests.get(EXERCISE_TEMPLATES_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        templates = data.get("exercise_templates", [])
        if not templates:
            break
            
        all_templates.extend(templates)
        
        # Check if there are more pages
        page_count = data.get("page_count", 1)
        if page >= page_count:
            break
            
        page += 1
    
    print(f"  Total exercise templates fetched: {len(all_templates)}")
    return all_templates


def export_exercise_templates_to_csv(templates: list[dict[str, Any]], filename: str = EXERCISE_TEMPLATES_CSV):
    """
    Export exercise templates to a CSV file.
    
    Args:
        templates: List of exercise template dicts
        filename: Output CSV filename (default: data/exercise_templates.csv)
    """
    if not templates:
        print("No exercise templates to export.")
        return
    
    # Define the CSV headers
    headers = [
        "id",
        "title",
        "type",
        "primary_muscle_group",
        "secondary_muscle_groups",
        "equipment",
        "is_custom"
    ]
    
    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        
        for template in templates:
            row = {
                "id": template.get("id"),
                "title": template.get("title"),
                "type": template.get("type"),
                "primary_muscle_group": template.get("primary_muscle_group"),
                "secondary_muscle_groups": json.dumps(template.get("secondary_muscle_groups", [])),
                "equipment": template.get("equipment"),
                "is_custom": template.get("is_custom"),
            }
            writer.writerow(row)
    
    print(f"Exported {len(templates)} exercise templates to {filename}")


def load_exercise_templates_from_csv(filename: str = EXERCISE_TEMPLATES_CSV) -> dict[str, dict[str, Any]]:
    """
    Load exercise templates from CSV into a dict keyed by template ID.
    
    Args:
        filename: The CSV file to read from
        
    Returns:
        Dict mapping template_id -> template data
    """
    templates = {}
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                template_id = row["id"]
                templates[template_id] = {
                    "id": template_id,
                    "title": row["title"],
                    "type": row["type"],
                    "primary_muscle_group": row["primary_muscle_group"],
                    "secondary_muscle_groups": json.loads(row["secondary_muscle_groups"]),
                    "equipment": row["equipment"],
                    "is_custom": row["is_custom"].lower() == "true",
                }
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Exercise templates CSV not found: {filename}\n"
            f"Run 'python cli.py hevy templates' first to generate it."
        )
    
    return templates


def analyze_workout_muscles(api_key: str, n: int, templates_file: str = EXERCISE_TEMPLATES_CSV) -> tuple[defaultdict[str, float], int]:
    """
    Analyze muscle group engagement for the nth workout.
    
    For each exercise in the workout:
    - Primary muscle group: 1.0 weight per set
    - Secondary muscle groups: 0.5 weight per set
    
    Args:
        api_key: The API key for authentication
        n: The workout number to analyze (1-indexed)
        templates_file: Path to the exercise templates CSV
        
    Returns:
        Tuple of (muscle_totals dict, total_sets int)
        - muscle_totals: Dict mapping muscle_group -> total weighted sets
        - total_sets: The actual total number of sets in the workout
    """
    # Fetch the workout
    workout = fetch_nth_workout(api_key, n)
    if not workout:
        raise ValueError(f"Workout #{n} not found.")
    
    # Load exercise templates
    templates = load_exercise_templates_from_csv(templates_file)
    
    # Calculate muscle engagement
    muscle_totals: defaultdict[str, float] = defaultdict(float)
    total_sets = 0   
    exercises = workout.get("exercises", [])
    
    print(f"\nAnalyzing muscle groups for workout: {workout.get('title', 'Untitled')}")
    print("-" * 60)
    
    for exercise in exercises:
        exercise_template_id = exercise.get("exercise_template_id")
        exercise_title = exercise.get("title", "Unknown Exercise")
        sets = exercise.get("sets", [])
        num_sets = len(sets)
        total_sets += num_sets
        
        if exercise_template_id not in templates:
            print(f"  Warning: Template not found for '{exercise_title}' (ID: {exercise_template_id})")
            continue
        
        template = templates[exercise_template_id]
        primary_muscle = template.get("primary_muscle_group")
        secondary_muscles = template.get("secondary_muscle_groups", [])
        
        print(f"  {exercise_title}: {num_sets} sets")
        print(f"    Primary: {primary_muscle} (+{num_sets * PRIMARY_MUSCLE_WEIGHT})")
        
        if primary_muscle:
            muscle_totals[primary_muscle] += num_sets * PRIMARY_MUSCLE_WEIGHT
        
        for muscle in secondary_muscles:
            muscle_totals[muscle] += num_sets * SECONDARY_MUSCLE_WEIGHT
            print(f"    Secondary: {muscle} (+{num_sets * SECONDARY_MUSCLE_WEIGHT})")
    
    return muscle_totals, total_sets


def print_muscle_analysis(muscle_totals: defaultdict[str, float], total_sets: int) -> None:
    """
    Print a formatted summary of muscle group engagement.
    
    Args:
        muscle_totals: Dict mapping muscle_group -> total weighted sets
        total_sets: The actual total number of sets in the workout
    """
    if not muscle_totals:
        print("No muscle data to display.")
        return
    
    # Sort by total sets (descending)
    sorted_muscles = sorted(muscle_totals.items(), key=lambda x: x[1], reverse=True)
    
    print("\n" + "=" * 60)
    print("MUSCLE GROUP SUMMARY")
    print("=" * 60)
    print(f"{'Muscle Group':<25} {'Weighted Sets':>15}")
    print("-" * 60)
    
    for muscle, total in sorted_muscles:
        # Format as integer if whole number, otherwise with 1 decimal
        if total == int(total):
            formatted = f"{int(total)}"
        else:
            formatted = f"{total:.1f}"
        print(f"{muscle:<25} {formatted:>15}")
    
    print("-" * 60)
    print(f"{'TOTAL SETS':<25} {total_sets:>15}")
    print("=" * 60)
