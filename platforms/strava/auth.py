"""
Strava OAuth authentication and token management.
"""

import json
import os
import time
from typing import Any

import requests

# API URLs
TOKEN_URL = "https://www.strava.com/oauth/token"

# Token cache file
TOKEN_CACHE_FILE = "data/.strava_token_cache.json"


def get_client_credentials() -> tuple[str, str]:
    """Get Strava client ID and secret from environment variables."""
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET not found.\n"
            "Please set them in your .env file or environment.\n"
            "Get these from: https://www.strava.com/settings/api"
        )
    return client_id, client_secret


def get_refresh_token() -> str:
    """Get Strava refresh token from environment variable."""
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
    if not refresh_token:
        raise ValueError(
            "STRAVA_REFRESH_TOKEN not found.\n"
            "Please set it in your .env file or environment.\n"
            "Run 'python cli.py strava auth' to get your tokens."
        )
    return refresh_token


def load_cached_token() -> dict[str, Any] | None:
    """
    Load the cached access token from file.

    Returns:
        Dict with 'access_token' and 'expires_at' if cache exists, None otherwise
    """
    try:
        with open(TOKEN_CACHE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_cached_token(access_token: str, expires_at: int) -> None:
    """
    Save the access token to cache file.

    Args:
        access_token: The OAuth2 access token
        expires_at: Unix timestamp when the token expires
    """
    os.makedirs(os.path.dirname(TOKEN_CACHE_FILE), exist_ok=True)
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump({"access_token": access_token, "expires_at": expires_at}, f)


def get_access_token(force_refresh: bool = False) -> str:
    """
    Get a valid Strava access token, using cache when possible.

    Checks if a cached token exists and is still valid (with 5 min buffer).
    If valid, returns the cached token. Otherwise, refreshes and caches a new one.

    Args:
        force_refresh: If True, bypass cache and always refresh

    Returns:
        A valid access token
    """
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached = load_cached_token()
        if cached:
            expires_at = cached.get("expires_at", 0)
            # Add 5 minute buffer before expiry
            if time.time() < (expires_at - 300):
                print("Using cached access token.")
                return cached["access_token"]

    # Need to refresh
    print("Refreshing Strava access token...")
    client_id, client_secret = get_client_credentials()
    refresh_token = get_refresh_token()

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    # Cache the new token
    access_token = data["access_token"]
    expires_at = data["expires_at"]
    save_cached_token(access_token, expires_at)

    # Notify if refresh token changed
    new_refresh_token = data.get("refresh_token")
    if new_refresh_token and new_refresh_token != refresh_token:
        print(
            f"Note: New refresh token received. Update STRAVA_REFRESH_TOKEN in your .env file:"
        )
        print(f"  STRAVA_REFRESH_TOKEN={new_refresh_token}")

    return access_token


def print_auth_instructions() -> None:
    """Print instructions for authenticating with Strava."""
    print(
        """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      STRAVA AUTHENTICATION SETUP                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

To use the Strava integration, you need to:

1. CREATE A STRAVA API APPLICATION
   Go to: https://www.strava.com/settings/api
   
   Fill in:
   - Application Name: FitLake (or your choice)
   - Category: Data Analysis
   - Website: http://localhost
   - Authorization Callback Domain: localhost

2. GET YOUR CLIENT CREDENTIALS
   After creating the app, note down:
   - Client ID
   - Client Secret

3. ADD TO YOUR .env FILE
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret

4. GET YOUR REFRESH TOKEN
   Visit this URL in your browser (replace YOUR_CLIENT_ID):
   
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all

   After authorizing, you'll be redirected to:
   http://localhost?code=AUTHORIZATION_CODE
   
   Copy the AUTHORIZATION_CODE and run:
   
   curl -X POST https://www.strava.com/oauth/token \\
     -d client_id=YOUR_CLIENT_ID \\
     -d client_secret=YOUR_CLIENT_SECRET \\
     -d code=AUTHORIZATION_CODE \\
     -d grant_type=authorization_code

5. SAVE THE REFRESH TOKEN
   From the response, copy the refresh_token and add to .env:
   STRAVA_REFRESH_TOKEN=your_refresh_token

NOTE: The access_token expires every 6 hours, but the refresh_token is 
long-lived. The CLI will automatically refresh the access token when needed.

"""
    )
