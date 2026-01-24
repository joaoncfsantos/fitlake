"""
Platform integrations for fitness data.

Supported platforms:
  - hevy: Strength training workouts
  - strava: Cardio activities (running, cycling, etc.)
"""

from . import hevy
from . import strava

__all__ = ["hevy", "strava"]
