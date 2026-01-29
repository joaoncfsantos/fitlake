from datetime import datetime
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
    steps: Mapped[int] = mapped_column(Integer)
    daily_step_goal: Mapped[int] = mapped_column(Integer)
    distance_meters: Mapped[float] = mapped_column(Float)
    total_calories: Mapped[float] = mapped_column(Float)
    active_calories: Mapped[float] = mapped_column(Float)
    bmr_calories: Mapped[float] = mapped_column(Float)
    wellness_calories: Mapped[float] = mapped_column(Float)
    floors_ascended: Mapped[int] = mapped_column(Integer)
    floors_descended: Mapped[int] = mapped_column(Integer)
    min_heart_rate: Mapped[int] = mapped_column(Integer)
    max_heart_rate: Mapped[int] = mapped_column(Integer)
    resting_heart_rate: Mapped[int] = mapped_column(Integer)
    average_stress_level: Mapped[int] = mapped_column(Integer)
    max_stress_level: Mapped[int] = mapped_column(Integer)
    stress_duration: Mapped[int] = mapped_column(Integer)
    rest_stress_duration: Mapped[int] = mapped_column(Integer)
    activity_stress_duration: Mapped[int] = mapped_column(Integer)
    low_stress_duration: Mapped[int] = mapped_column(Integer)
    medium_stress_duration: Mapped[int] = mapped_column(Integer)
    high_stress_duration: Mapped[int] = mapped_column(Integer)
    moderate_intensity_minutes: Mapped[int] = mapped_column(Integer)
    vigorous_intensity_minutes: Mapped[int] = mapped_column(Integer)
    intensity_minutes_goal: Mapped[int] = mapped_column(Integer)
    sleeping_seconds: Mapped[int] = mapped_column(Integer)
    body_battery_charged_value: Mapped[float] = mapped_column(Float)
    body_battery_drained_value: Mapped[float] = mapped_column(Float)
    body_battery_highest_value: Mapped[float] = mapped_column(Float)
    body_battery_lowest_value: Mapped[float] = mapped_column(Float)

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