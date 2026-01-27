"""
Workout models for strength training (Hevy).

Stores workout sessions with their exercises and sets.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Workout(Base):
    """
    Represents a strength training workout session.

    A workout contains multiple exercises, each with multiple sets.
    """

    __tablename__ = "workouts"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # External identifier
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="hevy", index=True)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timing
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Json column for exercises
    exercises: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        return f"<Workout(id={self.id}, title='{self.title}')>"

    @classmethod
    def from_hevy(cls, data: dict) -> "Workout":
        """
        Create a Workout from Hevy API data.

        Args:
            data: Workout dict from Hevy API

        Returns:
            Workout instance with exercises (not yet added to session)
        """
        # Parse timestamps
        start_time = datetime.fromisoformat(data["start_time"].replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(data["end_time"].replace("Z", "+00:00"))
        duration = int((end_time - start_time).total_seconds())

        workout = cls(
            platform="hevy",
            external_id=data["id"],
            title=data.get("title", "Untitled Workout"),
            description=data.get("description"),
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            exercises=data.get("exercises", []),
        )

        return workout

