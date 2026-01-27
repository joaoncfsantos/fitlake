"""
Exercise template models for Hevy.

Stores exercise definitions with muscle group information.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ExerciseTemplate(Base):
    """
    Represents an exercise template from Hevy.

    Contains exercise definitions with muscle groups and equipment info.
    """

    __tablename__ = "exercise_templates"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # External identifier
    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, default="hevy", index=True
    )
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Exercise info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    exercise_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Muscle groups
    primary_muscle_group: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    secondary_muscle_groups: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON array stored as text

    # Equipment
    equipment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Custom exercise flag
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<ExerciseTemplate(id={self.id}, title='{self.title}')>"

    @classmethod
    def from_hevy(cls, data: dict) -> "ExerciseTemplate":
        """
        Create an ExerciseTemplate from Hevy API data.

        Args:
            data: Exercise template dict from Hevy API

        Returns:
            ExerciseTemplate instance
        """
        import json

        # Convert secondary_muscle_groups list to JSON string
        secondary_muscles = data.get("secondary_muscle_groups", [])
        secondary_muscles_json = (
            json.dumps(secondary_muscles) if secondary_muscles else None
        )

        return cls(
            platform="hevy",
            external_id=data["id"],
            title=data.get("title", "Unknown Exercise"),
            exercise_type=data.get("type"),
            primary_muscle_group=data.get("primary_muscle_group"),
            secondary_muscle_groups=secondary_muscles_json,
            equipment=data.get("equipment"),
            is_custom=data.get("is_custom", False),
        )
