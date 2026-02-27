"""
Insights endpoints.

AI-generated insights about the user's fitness data.
"""

import os
from datetime import datetime, timedelta
from statistics import mean
from typing import Optional

from fastapi import APIRouter, Query
from openai import OpenAI
from pydantic import BaseModel

from api.auth import RequireAPIKey  
from api.dependencies import DbSession
from db import crud
from db.models.daily_stats import DailyStats
from db.models.activity import Activity
from db.models.workout import Workout
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()


class InsightsResponse(BaseModel):
    insight: str
    period_start: datetime
    period_end: datetime


@router.get("/insight", response_model=InsightsResponse)
def get_insights(
    db: DbSession,
    _api_key: RequireAPIKey,
    since: Optional[datetime] = Query(None, description="Start of the period (default: 7 days ago)"),
    until: Optional[datetime] = Query(None, description="End of the period (default: today)"),
):
    """
    Generate an AI insight about the user's fitness data for the given period.
    Defaults to the last 7 days if no date range is provided.
    """
    until = until or datetime.utcnow()
    since = since or (until - timedelta(days=7))

    # --- Fetch data ---
    daily_stats = (
        db.query(DailyStats)
        .filter(DailyStats.date >= since, DailyStats.date <= until)
        .order_by(DailyStats.date.desc())
        .all()
    )

    runs = crud.get_activities(
        db, activity_type="Run", since=since, until=until, limit=50
    )

    workouts = crud.get_workouts(db, since=since, until=until, limit=50)

    # --- Summarise health data ---
    health_summary = _summarise_health(daily_stats)

    # --- Summarise running data ---
    running_summary = _summarise_running(runs)

    # --- Summarise strength data ---
    strength_summary = _summarise_strength(workouts)

    # --- Build prompt and call LLM ---
    context = _build_context(since, until, health_summary, running_summary, strength_summary)
    insight = _call_llm(context)

    return InsightsResponse(insight=insight, period_start=since, period_end=until)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summarise_health(stats: list) -> dict:
    if not stats:
        return {}

    def avg(values):
        filtered = [v for v in values if v is not None]
        return round(mean(filtered), 1) if filtered else None

    step_goal_hits = sum(
        1 for s in stats
        if s.steps and s.daily_step_goal and s.steps >= s.daily_step_goal
    )

    return {
        "days": len(stats),
        "step_goal_hit": f"{step_goal_hits}/{len(stats)}",
        "avg_steps": avg([s.steps for s in stats]),
        "avg_sleep_hours": round(avg([s.sleeping_seconds for s in stats]) / 3600, 1)
            if avg([s.sleeping_seconds for s in stats]) else None,
        "avg_deep_sleep_pct": round(
            avg([
                s.deep_sleep_seconds / s.sleeping_seconds * 100
                for s in stats
                if s.sleeping_seconds and s.deep_sleep_seconds
            ]), 1
        ),
        "avg_resting_hr": avg([s.resting_heart_rate for s in stats]),
        "resting_hr_trend": [s.resting_heart_rate for s in reversed(stats) if s.resting_heart_rate],
        "avg_stress": avg([s.average_stress_level for s in stats]),
        "high_stress_days": sum(1 for s in stats if s.average_stress_level and s.average_stress_level > 50),
        "avg_body_battery_low": avg([s.body_battery_lowest_value for s in stats]),
        "avg_body_battery_high": avg([s.body_battery_highest_value for s in stats]),
    }


def _summarise_running(runs: list) -> dict:
    if not runs:
        return {}

    def avg(values):
        filtered = [v for v in values if v is not None]
        return round(mean(filtered), 2) if filtered else None

    total_km = sum((r.distance_meters or 0) for r in runs) / 1000
    avg_pace_mps = avg([r.average_speed_mps for r in runs])
    avg_pace_min_km = round(1000 / avg_pace_mps / 60, 2) if avg_pace_mps else None

    return {
        "count": len(runs),
        "total_km": round(total_km, 1),
        "avg_pace_min_per_km": avg_pace_min_km,
        "avg_hr": avg([r.average_heartrate for r in runs]),
        "total_elevation_m": round(sum((r.total_elevation_gain_meters or 0) for r in runs), 0),
    }


def _summarise_strength(workouts: list) -> dict:
    if not workouts:
        return {}

    muscle_sets: dict[str, int] = {}
    total_sets = 0

    for workout in workouts:
        for exercise in (workout.exercises or []):
            sets = len(exercise.get("sets", []))
            total_sets += sets
            muscle = exercise.get("primary_muscle_group")
            if muscle:
                muscle_sets[muscle] = muscle_sets.get(muscle, 0) + sets

    top_muscles = sorted(muscle_sets.items(), key=lambda x: x[1], reverse=True)[:4]

    return {
        "count": len(workouts),
        "total_sets": total_sets,
        "top_muscle_groups": [
            {"muscle": m, "pct": round(s / total_sets * 100, 1)}
            for m, s in top_muscles
        ] if total_sets else [],
    }


def _build_context(since, until, health, running, strength) -> str:
    lines = [
        f"Period: {since.date()} to {until.date()}",
        "",
        "=== Health (Garmin) ===",
    ]

    if health:
        lines += [
            f"Days tracked: {health['days']}",
            f"Step goal hit: {health['step_goal_hit']} days",
            f"Avg steps: {health['avg_steps']}",
            f"Avg sleep: {health['avg_sleep_hours']}h (deep sleep: {health['avg_deep_sleep_pct']}%)",
            f"Avg resting HR: {health['avg_resting_hr']} bpm | Trend: {health['resting_hr_trend']}",
            f"Avg stress: {health['avg_stress']} | High-stress days: {health['high_stress_days']}",
            f"Body battery — avg low: {health['avg_body_battery_low']}, avg high: {health['avg_body_battery_high']}",
        ]
    else:
        lines.append("No health data for this period.")

    lines += ["", "=== Running (Strava) ==="]
    if running:
        lines += [
            f"Runs: {running['count']} | Total: {running['total_km']} km",
            f"Avg pace: {running['avg_pace_min_per_km']} min/km | Avg HR: {running['avg_hr']} bpm",
            f"Total elevation: {running['total_elevation_m']} m",
        ]
    else:
        lines.append("No runs for this period.")

    lines += ["", "=== Strength (Hevy) ==="]
    if strength:
        muscle_str = ", ".join(
            f"{m['muscle']} ({m['pct']}%)" for m in strength["top_muscle_groups"]
        )
        lines += [
            f"Workouts: {strength['count']} | Total sets: {strength['total_sets']}",
            f"Top muscle groups: {muscle_str}",
        ]
    else:
        lines.append("No strength workouts for this period.")

    return "\n".join(lines)


def _call_llm(context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
               "content": (
    "You are an analytical fitness coach reviewing a user's last seven days of data. "
    "Your response must always cover exactly three topics — Health, Running, and Strength."
    "If there is no data for a topic, say so. "
    "followed by one final sentence with a concrete, data-driven recommendation. "
    "Each sentence must be on its own line. "
    "Be precise: reference the actual numbers from the data. "
    "Use an objective, analytical tone — no motivational language. "
    "Plain prose only; no bullet points, no headers."
    "Group your sentences into three paragraphs — Health, Running, and Strength — separated by blank lines (\n\n). Each sentence within a paragraph should be on its own line."
),
            },
            {"role": "user", "content": context},
        ],
        max_tokens=250,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()