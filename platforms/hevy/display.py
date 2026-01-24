"""
Display and formatting functions for Hevy data.
"""

import json
from collections import defaultdict
from datetime import datetime


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
                        "custom_metric": "<number | null>",
                    }
                ],
            }
        ],
    }

    print("\n" + "=" * 80)
    print("ORIGINAL DATA STRUCTURE (from Hevy API):")
    print("=" * 80)
    print(json.dumps(example_original, indent=2))


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


def print_recovery_analysis(
    recovery_count: int, workout_count: int, recovery_dates: list[str], days: int
) -> None:
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
            days_ago = (
                datetime.now().date() - datetime.strptime(date_str, "%Y-%m-%d").date()
            ).days
            print(f"  {date_str} ({days_ago} day{'s' if days_ago != 1 else ''} ago)")
        if len(recovery_dates) > 10:
            print(f"  ... and {len(recovery_dates) - 10} more")
    print("=" * 50)
