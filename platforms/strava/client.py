"""
Strava API client for fetching activity data.
https://developers.strava.com/docs/reference/
"""

import time
from datetime import datetime, timezone
from typing import Any

import requests

from .storage import load_activities_from_csv

# API URLs
API_BASE_URL = "https://www.strava.com/api/v3"

# API pagination
PAGE_SIZE = 30  # Strava default


def _get_headers(access_token: str) -> dict[str, str]:
    """Build standard API headers."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


def fetch_activities_page(
    access_token: str,
    page: int,
    per_page: int = PAGE_SIZE,
    after: int | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch a single page of activities from the API.

    Args:
        access_token: The OAuth2 access token
        page: Page number (1-indexed)
        per_page: Number of items per page (max 200)

    Returns:
        List of activity dicts
    """
    headers = _get_headers(access_token)
    params: dict[str, Any] = {
        "page": page,
        "per_page": per_page,
    }
    if after is not None:
        params["after"] = after

    response = requests.get(
        f"{API_BASE_URL}/athlete/activities",
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_all_activities(access_token: str) -> list[dict[str, Any]]:
    """
    Fetch all activities by iterating through all pages.

    Args:
        access_token: The OAuth2 access token

    Returns:
        List of all activity dicts
    """
    all_activities = []
    page = 1

    print("Fetching activities from Strava API...")

    while True:
        print(f"  Fetching page {page}...")
        activities = fetch_activities_page(access_token, page)

        if not activities:
            break

        all_activities.extend(activities)

        # If we got fewer than requested, we've reached the end
        if len(activities) < PAGE_SIZE:
            break

        page += 1

        # Rate limiting: Strava has a 100 requests per 15 minutes limit
        # and 1000 requests per day limit
        time.sleep(0.5)

    print(f"  Total activities fetched: {len(all_activities)}")
    return all_activities


def fetch_activities_since(access_token: str, since: datetime) -> list[dict[str, Any]]:
    """
    Fetch only activities created after a given datetime (light/incremental sync).

    Uses Strava's `after` filter (Unix timestamp) so only new pages are
    downloaded rather than the full history.

    Args:
        access_token: The OAuth2 access token
        since: Fetch activities strictly after this datetime

    Returns:
        List of activity dicts newer than `since`
    """

    after_ts = int(since.replace(tzinfo=timezone.utc).timestamp())
    all_activities = []
    page = 1

    print(f"Fetching Strava activities since {since.date()} ...")

    while True:
        print(f"  Fetching page {page}...")
        activities = fetch_activities_page(access_token, page, after=after_ts)

        if not activities:
            break

        all_activities.extend(activities)

        if len(activities) < PAGE_SIZE:
            break

        page += 1
        time.sleep(0.5)

    print(f"  Total new activities fetched: {len(all_activities)}")
    return all_activities


def fetch_activity_by_id(access_token: str, activity_id: int) -> dict[str, Any]:
    """
    Fetch a specific activity by its ID.

    Args:
        access_token: The OAuth2 access token
        activity_id: The activity ID

    Returns:
        The detailed activity dict
    """
    headers = _get_headers(access_token)

    response = requests.get(
        f"{API_BASE_URL}/activities/{activity_id}",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_athlete(access_token: str) -> dict[str, Any]:
    """
    Fetch the authenticated athlete's profile.

    Args:
        access_token: The OAuth2 access token

    Returns:
        The athlete profile dict
    """
    headers = _get_headers(access_token)

    response = requests.get(
        f"{API_BASE_URL}/athlete",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_detailed_activity(n: int, access_token: str) -> dict[str, Any] | None:
    """
    Get the nth activity with full details from the API (1-indexed).

    This fetches the DetailedActivity which includes calories and other
    fields not available in SummaryActivity.

    Args:
        n: The position of the activity (1 = most recent, 2 = second most recent, etc.)
        access_token: The OAuth2 access token

    Returns:
        The detailed activity dict if found, None otherwise
    """
    if n < 1:
        raise ValueError("n must be >= 1 (1-indexed)")

    # Fetch the nth activity from the API (page=n, per_page=1)
    print(f"Fetching activity #{n} from Strava API...")
    activities = fetch_activities_page(access_token, page=n, per_page=1)

    if not activities:
        print(f"Activity #{n} not found.")
        return None

    summary_activity = activities[0]
    activity_id = summary_activity.get("id")
    activity_name = summary_activity.get("name", "Untitled")

    print(f"Fetching detailed activity: {activity_name} (ID: {activity_id})...")

    # Fetch the detailed activity from the API
    detailed_activity = fetch_activity_by_id(access_token, int(activity_id))
    return detailed_activity
