"""
Garmin Connect authentication and session management.
Uses the garminconnect library which handles OAuth internally.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from garminconnect import Garmin, GarminConnectAuthenticationError

if TYPE_CHECKING:
    from garminconnect import Garmin

# Token storage directory (project-local, consistent with Strava)
TOKENS_DIR = Path("data/.garmin_tokens")


def get_credentials() -> tuple[str, str]:
    """
    Get Garmin Connect email and password from environment variables.

    Returns:
        Tuple of (email, password)

    Raises:
        ValueError: If credentials are not set
    """
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    if not email or not password:
        raise ValueError(
            "GARMIN_EMAIL and GARMIN_PASSWORD not found.\n"
            "Please set them in your .env file or environment.\n"
            "Run 'python cli.py garmin auth' for setup instructions."
        )
    return email, password


def get_client() -> "Garmin":
    """
    Get an authenticated Garmin Connect client.

    First tries to resume a session from saved tokens. If that fails,
    performs a fresh login with credentials.

    Returns:
        Authenticated Garmin client instance

    Raises:
        GarminConnectAuthenticationError: If authentication fails
    """
    email, password = get_credentials()
    client = Garmin(email, password)

    # Try to resume session from saved tokens
    if TOKENS_DIR.exists():
        try:
            client.login(tokenstore=str(TOKENS_DIR))
            print("Resumed Garmin session from saved tokens.")
            return client
        except (FileNotFoundError, GarminConnectAuthenticationError):
            # Tokens invalid or missing, need fresh login
            pass

    # Fresh login
    print("Logging in to Garmin Connect...")
    try:
        client.login()
        # Save tokens for future sessions
        client.garth.dump(str(TOKENS_DIR))
        print("Login successful. Tokens saved for future sessions.")
        return client
    except GarminConnectAuthenticationError as e:
        raise GarminConnectAuthenticationError(
            f"Login failed: {e}\n\n"
            "Possible causes:\n"
            "  1. Incorrect email or password\n"
            "  2. Two-factor authentication enabled (disable it or use app password)\n"
            "  3. Account requires verification (log in via browser first)\n"
            "  4. Too many failed attempts (wait and try again)"
        ) from e


def clear_tokens() -> None:
    """Remove saved authentication tokens."""
    import shutil

    if TOKENS_DIR.exists():
        shutil.rmtree(TOKENS_DIR)
        print(f"Removed saved tokens from {TOKENS_DIR}")
    else:
        print("No saved tokens found.")


def print_auth_instructions() -> None:
    """Print instructions for authenticating with Garmin Connect."""
    print(
        """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      GARMIN CONNECT AUTHENTICATION SETUP                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

To use the Garmin integration, you need to:

1. ADD YOUR CREDENTIALS TO .env FILE
   
   GARMIN_EMAIL=your_garmin_email@example.com
   GARMIN_PASSWORD=your_garmin_password

2. IMPORTANT NOTES
   
   - Two-Factor Authentication (2FA/MFA): If enabled on your account, 
     the basic login may not work. Consider:
     * Disabling 2FA temporarily
     * Creating an app-specific password (if supported)
   
   - First Login: You may need to log in via browser first at 
     https://connect.garmin.com to accept any pending terms or verifications.
   
   - Token Storage: After successful login, tokens are saved to 
     ~/.garminconnect for automatic session resumption.

3. TEST YOUR CONNECTION
   
   python cli.py garmin sync

4. AVAILABLE DATA
   
   Garmin Connect provides access to:
   - Daily health stats (steps, calories, heart rate, stress)
   - Sleep data and sleep scores
   - Activities and workouts
   - Body composition (if using Garmin scale)
   - HRV, VO2 Max, Training Readiness
   - And much more!

5. TROUBLESHOOTING
   
   If you get authentication errors:
   - Verify credentials at connect.garmin.com
   - Clear saved tokens: python cli.py garmin logout
   - Check for account verification emails
   - Wait if rate-limited from too many attempts

"""
    )
