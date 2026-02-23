"""
Hevy platform integration for strength training workouts.
https://api.hevyapp.com/docs/#/
"""

# API client
from .client import (
    get_api_key,
    fetch_workouts_page,
    fetch_all_workouts,
    fetch_workouts_since,
    fetch_all_exercise_templates,
)

# Storage (CSV export/import)
from .storage import (
    export_to_csv,
    export_exercise_templates_to_csv,
    load_exercise_templates_from_csv,
    load_workouts_from_csv,
    get_latest_workouts_csv,
    get_nth_workout,
    get_workouts_since,
)

# Analysis
from .analysis import (
    analyze_workout_muscles,
    analyze_muscles_for_period,
    get_last_recovery_day,
    count_recovery_days,
)

# Display
from .display import (
    print_data_schema,
    print_muscle_analysis,
    print_recovery_analysis,
)

__all__ = [
    # Client
    "get_api_key",
    "fetch_workouts_page",
    "fetch_all_workouts",
    "fetch_workouts_since",
    "fetch_all_exercise_templates",
    # Storage
    "export_to_csv",
    "export_exercise_templates_to_csv",
    "load_exercise_templates_from_csv",
    "load_workouts_from_csv",
    "get_latest_workouts_csv",
    "get_nth_workout",
    "get_workouts_since",
    # Analysis
    "analyze_workout_muscles",
    "analyze_muscles_for_period",
    "get_last_recovery_day",
    "count_recovery_days",
    # Display
    "print_data_schema",
    "print_muscle_analysis",
    "print_recovery_analysis",
]
