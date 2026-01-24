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



def export_to_csv(workouts: list[dict[str, Any]], filename: str = "hevy_workouts.csv"):
    """Export workouts to a CSV file."""
    if not workouts:
        print("No workouts to export.")
        return
    
    
    # Get all unique keys for CSV headers
    headers = list(workouts[0].keys())
    
    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(workouts)
    
    print(f"Exported {len(workouts)} workouts to {filename}")


def print_data_schema() -> None:
    """
    Print example data schema of workouts.
    
    Displays the original API response structure with placeholder values to demonstrate the format.
    """
    # Example workout structure from API
    # Reference: https://api.hevyapp.com/docs/
    example_original = {
        "id": "<string>",
        "title": "<string>",
        "routine_id": "<string | null>",
        "description": "<string>",
        "start_time": "<ISO 8601 datetime>",
        "end_time": "<ISO 8601 datetime>",
        "updated_at": "<ISO 8601 datetime>",
        "created_at": "<ISO 8601 datetime>",
        "exercises": [
            {
                "index": "<integer>",
                "title": "<string>",
                "notes": "<string>",
                "exercise_template_id": "<string>",
                "superset_id": "<integer | null>",
                "sets": [
                    {
                        "index": "<integer>",
                        "type": "<warmup | normal | failure | dropset>",
                        "weight_kg": "<number | null>",
                        "reps": "<integer | null>",
                        "distance_meters": "<integer | null>",
                        "duration_seconds": "<integer | null>",
                        "rpe": "<number | null>",
                        "custom_metric": "<number | null>"
                    }
                ]
            }
        ]
    }
    
    
    print("\n" + "=" * 80)
    print("ORIGINAL DATA STRUCTURE (from Hevy API):")
    print("=" * 80)
    print(json.dumps(example_original, indent=2))


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


def _calculate_workout_muscles(
    workout: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    verbose: bool = False
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
                print(f"  Warning: Template not found for '{exercise_title}' (ID: {exercise_template_id})")
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
    aggregate: defaultdict[str, float],
    workout_totals: defaultdict[str, float]
) -> None:
    """Add workout muscle totals to the aggregate (in-place)."""
    for muscle, value in workout_totals.items():
        aggregate[muscle] += value


def analyze_workout_muscles(n: int, templates_file: str = EXERCISE_TEMPLATES_CSV) -> tuple[defaultdict[str, float], int]:
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


def fetch_workouts_since(api_key: str, days: int) -> list[dict[str, Any]]:
    """
    Fetch all workouts from the past N days.
    
    Args:
        api_key: The API key for authentication
        days: Number of days to look back
        
    Returns:
        List of workout dicts within the date range
    """
    from datetime import timedelta, timezone
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    workouts_in_range = []
    page = 1
    headers = _get_headers(api_key)
    
    print(f"Fetching workouts from the past {days} days...")
    print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    while True:
        params = {"page": page, "pageSize": PAGE_SIZE}
        response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        workouts = data.get("workouts", [])
        if not workouts:
            break
        
        past_cutoff = False
        for workout in workouts:
            start_time_str = workout.get("start_time")
            if not start_time_str:
                continue
            
            try:
                workout_date = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue
            
            if workout_date < cutoff_date:
                past_cutoff = True
                break
            
            workouts_in_range.append(workout)
        
        if past_cutoff:
            break
        
        page_count = data.get("page_count", 1)
        if page >= page_count:
            break
        
        page += 1
    
    print(f"Found {len(workouts_in_range)} workout(s) in the past {days} days")
    return workouts_in_range


def analyze_muscles_for_period(days: int, templates_file: str = EXERCISE_TEMPLATES_CSV) -> tuple[defaultdict[str, float], int, int]:
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
    
    # Calculate sum of weighted sets for percentage calculation
    weighted_total = sum(muscle_totals.values())
    
    print("\n" + "=" * 70)
    print("MUSCLE GROUP SUMMARY")
    print("=" * 70)
    print(f"{'Muscle Group':<25} {'Weighted Sets':>15} {'Percentage':>15}")
    print("-" * 70)
    
    for muscle, total in sorted_muscles:
        # Format as integer if whole number, otherwise with 1 decimal
        if total == int(total):
            formatted = f"{int(total)}"
        else:
            formatted = f"{total:.1f}"
        
        # Calculate percentage
        percentage = (total / weighted_total) * 100 if weighted_total > 0 else 0
        print(f"{muscle:<25} {formatted:>15} {percentage:>14.1f}%")
    
    print("-" * 70)
    print(f"{'TOTAL SETS':<25} {total_sets:>15} {'100.0%':>15}")
    print("=" * 70)


def get_latest_workouts_csv() -> str:
    """
    Find the most recent hevy_workouts CSV file in data/exports.
    
    Returns:
        Path to the most recent CSV file
        
    Raises:
        FileNotFoundError: If no workout CSV files exist
    """
    import glob
    
    pattern = "data/exports/hevy_workouts_*.csv"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(
            "No workout data found. Run 'python cli.py hevy sync workouts' first."
        )
    
    # Sort by filename (which includes timestamp) and return the most recent
    return sorted(files)[-1]


def load_workouts_from_csv(filename: str | None = None) -> list[dict[str, Any]]:
    """
    Load workouts from a CSV file.
    
    Args:
        filename: Path to CSV file. If None, uses the most recent export.
        
    Returns:
        List of workout dicts with parsed 'exercises' field
    """
    import ast
    
    if filename is None:
        filename = get_latest_workouts_csv()
    
    workouts = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse exercises from string representation to actual Python objects
            if row.get("exercises"):
                try:
                    row["exercises"] = ast.literal_eval(row["exercises"])
                except (ValueError, SyntaxError):
                    row["exercises"] = []
            workouts.append(row)
    
    return workouts


def get_nth_workout(n: int) -> dict[str, Any] | None:
    """
    Get the nth workout from locally synced data (1-indexed).
    
    Args:
        n: The position of the workout (1 = most recent, 2 = second most recent, etc.)
        
    Returns:
        The workout dict if found, None otherwise
    """
    if n < 1:
        raise ValueError("n must be >= 1 (1-indexed)")
    
    workouts = load_workouts_from_csv()
    
    if n > len(workouts):
        print(f"Workout #{n} not found. Total workouts available: {len(workouts)}")
        return None
    
    workout = workouts[n - 1]  # Convert to 0-indexed
    print(f"Found workout: {workout.get('title', 'Untitled')} (total: {len(workouts)} workouts)")
    return workout


def get_workouts_since(days: int) -> list[dict[str, Any]]:
    """
    Get all workouts from the past N days from locally synced data.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of workout dicts within the date range
    """
    from datetime import timedelta, timezone
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    workouts = load_workouts_from_csv()
    
    workouts_in_range = []
    for workout in workouts:
        start_time_str = workout.get("start_time")
        if not start_time_str:
            continue
        
        try:
            workout_date = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        
        if workout_date >= cutoff_date:
            workouts_in_range.append(workout)
    
    print(f"Found {len(workouts_in_range)} workout(s) in the past {days} days")
    return workouts_in_range


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
    from datetime import timedelta, timezone
    
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
    from datetime import timedelta, timezone
    
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


def print_recovery_analysis(recovery_count: int, workout_count: int, recovery_dates: list[str], days: int) -> None:
    """
    Print a formatted summary of recovery days.
    
    Args:
        recovery_count: Number of recovery days
        workout_count: Number of workout days
        recovery_dates: List of recovery date strings
        days: Total days in the period
    """
    print("\n" + "=" * 50)
    print("RECOVERY ANALYSIS")
    print("=" * 50)
    print(f"Period: Past {days} days")
    print("-" * 50)
    print(f"Recovery days: {recovery_count}")
    print(f"Workout days:  {workout_count}")
    print(f"Recovery rate: {(recovery_count / days) * 100:.1f}%")
    print("-" * 50)
    
    if recovery_dates:
        print("Recovery dates:")
        for date_str in sorted(recovery_dates, reverse=True)[:10]:
            days_ago = (datetime.now().date() - datetime.strptime(date_str, "%Y-%m-%d").date()).days
            print(f"  {date_str} ({days_ago} day{'s' if days_ago != 1 else ''} ago)")
        if len(recovery_dates) > 10:
            print(f"  ... and {len(recovery_dates) - 10} more")
    print("=" * 50)
