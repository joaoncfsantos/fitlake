"""
Garmin Connect platform integration for health and fitness data.
https://github.com/cyberjunky/python-garminconnect
"""

# Authentication
from .auth import (
    get_credentials,
    get_client,
    clear_tokens,
    print_auth_instructions,
)

# API client
from .client import (
    fetch_daily_stats,
    fetch_daily_stats_range,
    fetch_sleep_data,
    fetch_heart_rates,
    fetch_stress_data,
    fetch_body_battery,
    fetch_hrv_data,
    fetch_activities,
    fetch_all_activities,
    fetch_user_profile,
    fetch_user_settings,
    fetch_training_readiness,
    fetch_training_status,
)

# Storage (CSV export/import)
from .storage import (
    export_daily_stats_to_csv,
    export_sleep_to_csv,
    export_activities_to_csv,
    get_latest_daily_stats_csv,
    get_latest_activities_csv,
    load_daily_stats_from_csv,
    load_activities_from_csv,
    get_stats_since,
)

# Display
from .display import (
    print_data_schema,
    print_daily_summary,
    print_sleep_summary,
    print_activity_summary,
    print_health_overview,
)

__all__ = [
    # Auth
    "get_credentials",
    "get_client",
    "clear_tokens",
    "print_auth_instructions",
    # Client
    "fetch_daily_stats",
    "fetch_daily_stats_range",
    "fetch_sleep_data",
    "fetch_heart_rates",
    "fetch_stress_data",
    "fetch_body_battery",
    "fetch_hrv_data",
    "fetch_activities",
    "fetch_all_activities",
    "fetch_user_profile",
    "fetch_user_settings",
    "fetch_training_readiness",
    "fetch_training_status",
    # Storage
    "export_daily_stats_to_csv",
    "export_sleep_to_csv",
    "export_activities_to_csv",
    "get_latest_daily_stats_csv",
    "get_latest_activities_csv",
    "load_daily_stats_from_csv",
    "load_activities_from_csv",
    "get_stats_since",
    # Display
    "print_data_schema",
    "print_daily_summary",
    "print_sleep_summary",
    "print_activity_summary",
    "print_health_overview",
]
