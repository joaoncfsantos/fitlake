"""
Activity model for cardio activities (Strava, Garmin).

Stores common activity data that can come from multiple platforms.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Activity(Base):
    """
    Represents a cardio activity (run, ride, swim, etc.).

    This model stores normalized activity data from multiple platforms
    (Strava, Garmin) in a unified format.
    """

    __tablename__ = "activities"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # External identifiers
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sport_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Timing
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    elapsed_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)  # Total time
    moving_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Active time

    # Distance and speed
    distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_speed_mps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # m/s
    max_speed_mps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # m/s

    # Elevation
    total_elevation_gain_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    elevation_high_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    elevation_low_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Heart rate
    average_heartrate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_heartrate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Power (cycling)
    average_watts: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_watts: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Calories
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Additional data (JSON stored as text for portability)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, name='{self.name}', type='{self.activity_type}')>"

    @classmethod
    def from_strava(cls, data: dict) -> "Activity":
        """
        Create an Activity from Strava API data.

        Args:
            data: Activity dict from Strava API

        Returns:
            Activity instance (not yet added to session)
        """
        return cls(
            platform="strava",
            external_id=str(data["id"]),
            name=data.get("name", "Untitled"),
            activity_type=data.get("type", "Unknown"),
            sport_type=data.get("sport_type"),
            start_date=datetime.fromisoformat(data["start_date"].replace("Z", "+00:00")),
            elapsed_time_seconds=data.get("elapsed_time", 0),
            moving_time_seconds=data.get("moving_time"),
            distance_meters=data.get("distance"),
            average_speed_mps=data.get("average_speed"),
            max_speed_mps=data.get("max_speed"),
            total_elevation_gain_meters=data.get("total_elevation_gain"),
            elevation_high_meters=data.get("elev_high"),
            elevation_low_meters=data.get("elev_low"),
            average_heartrate=data.get("average_heartrate"),
            max_heartrate=data.get("max_heartrate"),
            average_watts=data.get("average_watts"),
            max_watts=data.get("max_watts"),
            calories=data.get("calories"),
            description=data.get("description"),
        )

    @classmethod
    def from_garmin(cls, data: dict) -> "Activity":
        """
        Create an Activity from Garmin API data.

        Args:
            data: Activity dict from Garmin API

        Returns:
            Activity instance (not yet added to session)
        """
        # Parse Garmin's timestamp format
        start_time = data.get("startTimeLocal") or data.get("startTimeGMT")
        if isinstance(start_time, str):
            # Handle various Garmin date formats
            try:
                start_date = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                start_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        else:
            start_date = datetime.utcnow()

        return cls(
            platform="garmin",
            external_id=str(data.get("activityId", data.get("id", ""))),
            name=data.get("activityName", "Untitled"),
            activity_type=data.get("activityType", {}).get("typeKey", "Unknown")
            if isinstance(data.get("activityType"), dict)
            else str(data.get("activityType", "Unknown")),
            sport_type=data.get("sportType"),
            start_date=start_date,
            elapsed_time_seconds=int(data.get("duration", 0)),
            moving_time_seconds=int(data.get("movingDuration")) if data.get("movingDuration") else None,
            distance_meters=data.get("distance"),
            average_speed_mps=data.get("averageSpeed"),
            max_speed_mps=data.get("maxSpeed"),
            total_elevation_gain_meters=data.get("elevationGain"),
            elevation_high_meters=data.get("maxElevation"),
            elevation_low_meters=data.get("minElevation"),
            average_heartrate=data.get("averageHR"),
            max_heartrate=data.get("maxHR"),
            average_watts=data.get("avgPower"),
            max_watts=data.get("maxPower"),
            calories=data.get("calories"),
            description=data.get("description"),
        )
