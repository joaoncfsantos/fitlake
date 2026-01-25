"""
Workout models for strength training (Hevy).

Stores workout sessions with their exercises and sets.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # Relationships
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )

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
        )

        # Add exercises
        for idx, exercise_data in enumerate(data.get("exercises", [])):
            exercise = WorkoutExercise.from_hevy(exercise_data, order=idx)
            workout.exercises.append(exercise)

        return workout


class WorkoutExercise(Base):
    """
    Represents a single exercise within a workout.

    An exercise contains multiple sets with weight/reps.
    """

    __tablename__ = "workout_exercises"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    workout_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Exercise info
    exercise_template_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Order within workout
    exercise_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    workout: Mapped["Workout"] = relationship("Workout", back_populates="exercises")
    sets: Mapped[list["WorkoutSet"]] = relationship(
        "WorkoutSet", back_populates="exercise", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkoutExercise(id={self.id}, title='{self.title}')>"

    @classmethod
    def from_hevy(cls, data: dict, order: int) -> "WorkoutExercise":
        """
        Create a WorkoutExercise from Hevy API data.

        Args:
            data: Exercise dict from Hevy API
            order: Position of this exercise in the workout

        Returns:
            WorkoutExercise instance with sets
        """
        exercise = cls(
            exercise_template_id=data.get("exercise_template_id"),
            title=data.get("title", "Unknown Exercise"),
            notes=data.get("notes"),
            exercise_order=order,
        )

        # Add sets
        for idx, set_data in enumerate(data.get("sets", [])):
            workout_set = WorkoutSet.from_hevy(set_data, order=idx)
            exercise.sets.append(workout_set)

        return exercise


class WorkoutSet(Base):
    """
    Represents a single set within an exercise.

    Contains weight, reps, and other performance metrics.
    """

    __tablename__ = "workout_sets"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    exercise_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Set info
    set_order: Mapped[int] = mapped_column(Integer, nullable=False)
    set_type: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")

    # Performance metrics
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rpe: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Rate of Perceived Exertion

    # Relationships
    exercise: Mapped["WorkoutExercise"] = relationship("WorkoutExercise", back_populates="sets")

    def __repr__(self) -> str:
        return f"<WorkoutSet(id={self.id}, weight={self.weight_kg}kg, reps={self.reps})>"

    @classmethod
    def from_hevy(cls, data: dict, order: int) -> "WorkoutSet":
        """
        Create a WorkoutSet from Hevy API data.

        Args:
            data: Set dict from Hevy API
            order: Position of this set in the exercise

        Returns:
            WorkoutSet instance
        """
        return cls(
            set_order=order,
            set_type=data.get("set_type", "normal"),
            weight_kg=data.get("weight_kg"),
            reps=data.get("reps"),
            distance_meters=data.get("distance_meters"),
            duration_seconds=data.get("duration_seconds"),
            rpe=data.get("rpe"),
        )
