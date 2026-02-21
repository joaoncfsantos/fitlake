"""
Strava platform integration for cardio activities.
https://developers.strava.com/docs/reference/
"""

# Authentication
from .auth import (
    get_client_credentials,
    get_refresh_token,
    get_access_token,
    print_auth_instructions,
)

# API client
from .client import (
    fetch_activities_page,
    fetch_all_activities,
    fetch_activities_since,
    fetch_activity_by_id,
    fetch_athlete,
    get_detailed_activity,
)

# Storage (CSV export/import)
from .storage import (
    export_to_csv,
    load_activities_from_csv,
    get_latest_activities_csv,
    get_activities_since,
)

# Analysis
from .analysis import (
    get_activity_stats,
)

# Display
from .display import (
    print_data_schema,
    print_activity_summary,
    print_activity_stats,
)

__all__ = [
    # Auth
    "get_client_credentials",
    "get_refresh_token",
    "get_access_token",
    "print_auth_instructions",
    # Client
    "fetch_activities_page",
    "fetch_all_activities",
    "fetch_activities_since",
    "fetch_activity_by_id",
    "fetch_athlete",
    "get_detailed_activity",
    # Storage
    "export_to_csv",
    "load_activities_from_csv",
    "get_latest_activities_csv",
    "get_activities_since",
    # Analysis
    "get_activity_stats",
    # Display
    "print_data_schema",
    "print_activity_summary",
    "print_activity_stats",
]
