"""
CSV storage operations for Hevy workout data.
"""

import ast
import csv
import glob
import json
from datetime import datetime, timedelta, timezone
from typing import Any

# CSV filenames
EXERCISE_TEMPLATES_CSV = "data/exercise_templates.csv"


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


def export_exercise_templates_to_csv(
    templates: list[dict[str, Any]], filename: str = EXERCISE_TEMPLATES_CSV
):
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
        "is_custom",
    ]

    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()

        for template in templates:
            row = {
                "id": template.get("id"),
                "title": template.get("title"),
                "type": template.get("type"),
                "primary_muscle_group": template.get("primary_muscle_group"),
                "secondary_muscle_groups": json.dumps(
                    template.get("secondary_muscle_groups", [])
                ),
                "equipment": template.get("equipment"),
                "is_custom": template.get("is_custom"),
            }
            writer.writerow(row)

    print(f"Exported {len(templates)} exercise templates to {filename}")


def load_exercise_templates_from_csv(
    filename: str = EXERCISE_TEMPLATES_CSV,
) -> dict[str, dict[str, Any]]:
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
                    "secondary_muscle_groups": json.loads(
                        row["secondary_muscle_groups"]
                    ),
                    "equipment": row["equipment"],
                    "is_custom": row["is_custom"].lower() == "true",
                }
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Exercise templates CSV not found: {filename}\n"
            f"Run 'python cli.py hevy templates' first to generate it."
        )

    return templates


def get_latest_workouts_csv() -> str:
    """
    Find the most recent hevy_workouts CSV file in data/exports.

    Returns:
        Path to the most recent CSV file

    Raises:
        FileNotFoundError: If no workout CSV files exist
    """
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
    print(
        f"Found workout: {workout.get('title', 'Untitled')} (total: {len(workouts)} workouts)"
    )
    return workout


def get_workouts_since(days: int) -> list[dict[str, Any]]:
    """
    Get all workouts from the past N days from locally synced data.

    Args:
        days: Number of days to look back

    Returns:
        List of workout dicts within the date range
    """
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
