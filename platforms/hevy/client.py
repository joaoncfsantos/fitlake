"""
Hevy API client for fetching workout data.
https://api.hevyapp.com/docs/#/
"""

import os
from typing import Any

import requests

# API URLs
API_BASE_URL = "https://api.hevyapp.com/v1/workouts"
EXERCISE_TEMPLATES_URL = "https://api.hevyapp.com/v1/exercise_templates"

# API pagination
PAGE_SIZE = 10
TEMPLATES_PAGE_SIZE = 100


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

        response = requests.get(
            EXERCISE_TEMPLATES_URL, headers=headers, params=params, timeout=30
        )
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
