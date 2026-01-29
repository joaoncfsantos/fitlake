from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base

class DailyStats(Base):
    """
    Represents a daily health stat.
    """

    __tablename__ = "daily_stats"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # External identifier
    platform: Mapped[str] = mapped_column(String(50),  default="garmin", index=True)

    # Basic info
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    daily_step_goal: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    active_calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bmr_calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wellness_calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floors_ascended: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    floors_descended: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    min_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resting_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    average_stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stress_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rest_stress_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activity_stress_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    low_stress_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    medium_stress_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    high_stress_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    moderate_intensity_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vigorous_intensity_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    intensity_minutes_goal: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleeping_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    body_battery_charged_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_battery_drained_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_battery_highest_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_battery_lowest_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<DailyStats(id={self.id}, date='{self.date}')>"

    @classmethod
    def from_garmin(cls, data: dict) -> "DailyStats":
        """
        Create a DailyStats from Garmin API data.
        """
        return cls(
            platform="garmin",
            date=data.get("date"),
            steps=data.get("totalSteps"),
            daily_step_goal=data.get("dailyStepGoal"),
            distance_meters=data.get("totalDistanceMeters"),
            total_calories=data.get("totalKilocalories"),
            active_calories=data.get("activeKilocalories"),
            bmr_calories=data.get("bmrKilocalories"),
            wellness_calories=data.get("wellnessKilocalories"),
            floors_ascended=data.get("floorsAscended"),
            floors_descended=data.get("floorsDescended"),
            min_heart_rate=data.get("minHeartRate"),
            max_heart_rate=data.get("maxHeartRate"),
            resting_heart_rate=data.get("restingHeartRate"),
            average_stress_level=data.get("averageStressLevel"),
            max_stress_level=data.get("maxStressLevel"),
            stress_duration=data.get("stressDuration"),
            rest_stress_duration=data.get("restStressDuration"),
            activity_stress_duration=data.get("activityStressDuration"),
            low_stress_duration=data.get("lowStressDuration"),
            medium_stress_duration=data.get("mediumStressDuration"),
            high_stress_duration=data.get("highStressDuration"),
            moderate_intensity_minutes=data.get("moderateIntensityMinutes"),
            vigorous_intensity_minutes=data.get("vigorousIntensityMinutes"),
            intensity_minutes_goal=data.get("intensityMinutesGoal"),
            sleeping_seconds=data.get("sleepingSeconds"),
            body_battery_charged_value=data.get("bodyBatteryChargedValue"),
            body_battery_drained_value=data.get("bodyBatteryDrainedValue"),
            body_battery_highest_value=data.get("bodyBatteryHighestValue"),
            body_battery_lowest_value=data.get("bodyBatteryLowestValue"),
        )