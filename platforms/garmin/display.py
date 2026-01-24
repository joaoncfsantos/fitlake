"""
Display and formatting functions for Garmin Connect data.
"""

import json
from datetime import datetime
from typing import Any


def print_data_schema() -> None:
    """
    Print example data schema of Garmin daily stats and activities.
    """
    example_daily_stats = {
        "date": "<YYYY-MM-DD>",
        "totalSteps": "<integer>",
        "dailyStepGoal": "<integer>",
        "totalDistanceMeters": "<float>",
        "totalKilocalories": "<integer>",
        "activeKilocalories": "<integer>",
        "bmrKilocalories": "<integer>",
        "floorsAscended": "<integer>",
        "floorsDescended": "<integer>",
        "minHeartRate": "<integer>",
        "maxHeartRate": "<integer>",
        "restingHeartRate": "<integer>",
        "averageStressLevel": "<integer (0-100)>",
        "maxStressLevel": "<integer>",
        "moderateIntensityMinutes": "<integer>",
        "vigorousIntensityMinutes": "<integer>",
        "bodyBatteryHighestValue": "<integer (0-100)>",
        "bodyBatteryLowestValue": "<integer (0-100)>",
        "sleepingSeconds": "<integer>",
    }

    example_sleep = {
        "dailySleepDTO": {
            "sleepTimeSeconds": "<integer>",
            "napTimeSeconds": "<integer>",
            "deepSleepSeconds": "<integer>",
            "lightSleepSeconds": "<integer>",
            "remSleepSeconds": "<integer>",
            "awakeSleepSeconds": "<integer>",
            "sleepStartTimestampLocal": "<timestamp>",
            "sleepEndTimestampLocal": "<timestamp>",
        },
        "sleepScores": {
            "overall": {"value": "<integer (0-100)>"},
            "totalDuration": {"qualifierKey": "<EXCELLENT|GOOD|FAIR|POOR>"},
        },
    }

    example_activity = {
        "activityId": "<long>",
        "activityName": "<string>",
        "activityType": {"typeKey": "<running|cycling|swimming|...>"},
        "startTimeLocal": "<ISO 8601 datetime>",
        "distance": "<float (meters)>",
        "duration": "<float (seconds)>",
        "elevationGain": "<float (meters)>",
        "averageSpeed": "<float (m/s)>",
        "maxSpeed": "<float (m/s)>",
        "calories": "<integer>",
        "averageHR": "<integer>",
        "maxHR": "<integer>",
        "aerobicTrainingEffect": "<float (0-5)>",
        "anaerobicTrainingEffect": "<float (0-5)>",
        "vO2MaxValue": "<float>",
    }

    print("\n" + "=" * 80)
    print("GARMIN DAILY STATS STRUCTURE:")
    print("=" * 80)
    print(json.dumps(example_daily_stats, indent=2))

    print("\n" + "=" * 80)
    print("GARMIN SLEEP DATA STRUCTURE:")
    print("=" * 80)
    print(json.dumps(example_sleep, indent=2))

    print("\n" + "=" * 80)
    print("GARMIN ACTIVITY STRUCTURE:")
    print("=" * 80)
    print(json.dumps(example_activity, indent=2))


def print_daily_summary(stats: dict[str, Any]) -> None:
    """
    Print a formatted summary of daily statistics.

    Args:
        stats: Daily stats dict from Garmin API
    """
    date_str = stats.get("date", stats.get("calendarDate", "Unknown"))

    print("\n" + "=" * 70)
    print(f"DAILY SUMMARY: {date_str}")
    print("=" * 70)

    # Steps
    steps = stats.get("totalSteps", 0)
    step_goal = stats.get("dailyStepGoal", 0)
    step_pct = (steps / step_goal * 100) if step_goal else 0
    print(f"Steps:           {steps:,} / {step_goal:,} ({step_pct:.0f}%)")

    # Distance
    distance_m = stats.get("totalDistanceMeters", 0)
    if distance_m:
        print(f"Distance:        {distance_m / 1000:.2f} km")

    # Calories
    total_cal = stats.get("totalKilocalories", 0)
    active_cal = stats.get("activeKilocalories", 0)
    if total_cal:
        print(f"Calories:        {total_cal:,} total ({active_cal:,} active)")

    # Floors
    floors_up = stats.get("floorsAscended", 0)
    floors_down = stats.get("floorsDescended", 0)
    floors_goal = stats.get("floorsAscendedGoal", 0)
    if floors_up or floors_down:
        print(f"Floors:          {floors_up} up / {floors_down} down (goal: {floors_goal})")

    print("-" * 70)

    # Heart Rate
    resting_hr = stats.get("restingHeartRate")
    avg_hr = stats.get("averageHeartRate")
    min_hr = stats.get("minHeartRate")
    max_hr = stats.get("maxHeartRate")
    if resting_hr:
        print(f"Resting HR:      {resting_hr} bpm")
    if avg_hr:
        print(f"Average HR:      {avg_hr} bpm (min: {min_hr}, max: {max_hr})")

    # Stress
    avg_stress = stats.get("averageStressLevel")
    max_stress = stats.get("maxStressLevel")
    if avg_stress:
        stress_label = _get_stress_label(avg_stress)
        print(f"Stress:          {avg_stress} avg, {max_stress} max ({stress_label})")

    # Body Battery
    bb_high = stats.get("bodyBatteryHighestValue")
    bb_low = stats.get("bodyBatteryLowestValue")
    if bb_high:
        print(f"Body Battery:    {bb_low} - {bb_high}")

    print("-" * 70)

    # Intensity Minutes
    moderate_min = stats.get("moderateIntensityMinutes", 0)
    vigorous_min = stats.get("vigorousIntensityMinutes", 0)
    intensity_goal = stats.get("intensityMinutesGoal", 0)
    total_intensity = moderate_min + (vigorous_min * 2)  # Vigorous counts double
    if moderate_min or vigorous_min:
        print(
            f"Intensity Min:   {moderate_min} moderate + {vigorous_min} vigorous "
            f"= {total_intensity} (goal: {intensity_goal})"
        )

    # Sleep (if available)
    sleep_sec = stats.get("sleepingSeconds")
    if sleep_sec:
        hours, remainder = divmod(sleep_sec, 3600)
        minutes = remainder // 60
        print(f"Sleep:           {int(hours)}h {int(minutes)}m")

    print("=" * 70)


def _get_stress_label(stress_level: int) -> str:
    """Get a descriptive label for stress level."""
    if stress_level <= 25:
        return "Rest"
    elif stress_level <= 50:
        return "Low"
    elif stress_level <= 75:
        return "Medium"
    else:
        return "High"


def print_sleep_summary(sleep_data: dict[str, Any]) -> None:
    """
    Print a formatted summary of sleep data.

    Args:
        sleep_data: Sleep data dict from Garmin API
    """
    daily_sleep = sleep_data.get("dailySleepDTO", {})
    sleep_scores = sleep_data.get("sleepScores", {})

    print("\n" + "=" * 70)
    print("SLEEP SUMMARY")
    print("=" * 70)

    # Total sleep time
    total_sec = daily_sleep.get("sleepTimeSeconds", 0)
    if total_sec:
        hours, remainder = divmod(total_sec, 3600)
        minutes = remainder // 60
        print(f"Total Sleep:     {int(hours)}h {int(minutes)}m")

    # Sleep score
    overall_score = sleep_scores.get("overall", {}).get("value")
    if overall_score:
        score_label = _get_sleep_score_label(overall_score)
        print(f"Sleep Score:     {overall_score} ({score_label})")

    # Sleep stages
    deep = daily_sleep.get("deepSleepSeconds", 0)
    light = daily_sleep.get("lightSleepSeconds", 0)
    rem = daily_sleep.get("remSleepSeconds", 0)
    awake = daily_sleep.get("awakeSleepSeconds", 0)

    if deep or light or rem:
        print("-" * 70)
        print("SLEEP STAGES:")
        if total_sec > 0:
            print(
                f"  Deep:          {_format_duration(deep)} ({deep / total_sec * 100:.0f}%)"
            )
            print(
                f"  Light:         {_format_duration(light)} ({light / total_sec * 100:.0f}%)"
            )
            print(
                f"  REM:           {_format_duration(rem)} ({rem / total_sec * 100:.0f}%)"
            )
            print(f"  Awake:         {_format_duration(awake)}")

    # Sleep times
    start_time = daily_sleep.get("sleepStartTimestampLocal")
    end_time = daily_sleep.get("sleepEndTimestampLocal")
    if start_time and end_time:
        print("-" * 70)
        # Parse timestamps and format nicely
        try:
            if isinstance(start_time, int):
                start_dt = datetime.fromtimestamp(start_time / 1000)
                end_dt = datetime.fromtimestamp(end_time / 1000)
            else:
                start_dt = datetime.fromisoformat(str(start_time))
                end_dt = datetime.fromisoformat(str(end_time))
            print(f"Bedtime:         {start_dt.strftime('%H:%M')}")
            print(f"Wake time:       {end_dt.strftime('%H:%M')}")
        except (ValueError, TypeError, OSError):
            pass

    print("=" * 70)


def _get_sleep_score_label(score: int) -> str:
    """Get a descriptive label for sleep score."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"


def _format_duration(seconds: int) -> str:
    """Format seconds as Xh Ym."""
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f"{int(hours)}h {int(minutes)}m"
    return f"{int(minutes)}m"


def print_activity_summary(activity: dict[str, Any]) -> None:
    """
    Print a formatted summary of an activity.

    Args:
        activity: Activity dict from Garmin API
    """
    print("\n" + "=" * 70)
    print(f"ACTIVITY: {activity.get('activityName', 'Untitled')}")
    print("=" * 70)

    # Type and date
    activity_type = activity.get("activityType", {})
    if isinstance(activity_type, dict):
        type_str = activity_type.get("typeKey", "Unknown")
    else:
        type_str = str(activity_type)
    print(f"Type:            {type_str}")
    print(f"Date:            {activity.get('startTimeLocal', 'Unknown')}")

    # Distance and duration
    distance = activity.get("distance", 0)
    if distance:
        print(f"Distance:        {distance / 1000:.2f} km")

    duration = activity.get("duration", 0)
    if duration:
        print(f"Duration:        {_format_duration(int(duration))}")

    # Speed/Pace
    avg_speed = activity.get("averageSpeed", 0)
    if avg_speed and distance:
        # Calculate pace (min/km)
        pace_sec_per_km = 1000 / avg_speed
        pace_min = int(pace_sec_per_km // 60)
        pace_sec = int(pace_sec_per_km % 60)
        print(f"Avg Pace:        {pace_min}:{pace_sec:02d} min/km")
        print(f"Avg Speed:       {avg_speed * 3.6:.1f} km/h")

    # Elevation
    elev_gain = activity.get("elevationGain", 0)
    elev_loss = activity.get("elevationLoss", 0)
    if elev_gain or elev_loss:
        print(f"Elevation:       +{elev_gain:.0f}m / -{elev_loss:.0f}m")

    print("-" * 70)

    # Heart rate
    avg_hr = activity.get("averageHR")
    max_hr = activity.get("maxHR")
    if avg_hr:
        print(f"Avg HR:          {avg_hr} bpm")
    if max_hr:
        print(f"Max HR:          {max_hr} bpm")

    # Calories
    calories = activity.get("calories", 0)
    if calories:
        print(f"Calories:        {calories} kcal")

    # Training Effect
    aerobic_te = activity.get("aerobicTrainingEffect")
    anaerobic_te = activity.get("anaerobicTrainingEffect")
    if aerobic_te:
        print(f"Aerobic TE:      {aerobic_te:.1f}")
    if anaerobic_te:
        print(f"Anaerobic TE:    {anaerobic_te:.1f}")

    # VO2 Max
    vo2max = activity.get("vO2MaxValue")
    if vo2max:
        print(f"VO2 Max:         {vo2max:.1f}")

    print("=" * 70)


def print_health_overview(
    stats: dict[str, Any],
    sleep: dict[str, Any] | None = None,
    hrv: dict[str, Any] | None = None,
    training_readiness: dict[str, Any] | None = None,
) -> None:
    """
    Print a comprehensive health overview combining multiple data sources.

    Args:
        stats: Daily stats dict
        sleep: Optional sleep data dict
        hrv: Optional HRV data dict
        training_readiness: Optional training readiness dict
    """
    date_str = stats.get("date", stats.get("calendarDate", "Unknown"))

    print("\n" + "=" * 70)
    print(f"HEALTH OVERVIEW: {date_str}")
    print("=" * 70)

    # Key metrics in a compact format
    metrics = []

    # Steps
    steps = stats.get("totalSteps", 0)
    step_goal = stats.get("dailyStepGoal", 0)
    if steps:
        pct = (steps / step_goal * 100) if step_goal else 0
        metrics.append(f"Steps: {steps:,} ({pct:.0f}%)")

    # Resting HR
    resting_hr = stats.get("restingHeartRate")
    if resting_hr:
        metrics.append(f"RHR: {resting_hr} bpm")

    # Stress
    avg_stress = stats.get("averageStressLevel")
    if avg_stress:
        metrics.append(f"Stress: {avg_stress}")

    # Body Battery
    bb_high = stats.get("bodyBatteryHighestValue")
    bb_low = stats.get("bodyBatteryLowestValue")
    if bb_high:
        metrics.append(f"Body Battery: {bb_low}-{bb_high}")

    # Sleep score
    if sleep:
        sleep_score = sleep.get("sleepScores", {}).get("overall", {}).get("value")
        if sleep_score:
            metrics.append(f"Sleep Score: {sleep_score}")

    # Training readiness
    if training_readiness:
        readiness = training_readiness.get("score")
        if readiness:
            metrics.append(f"Training Readiness: {readiness}")

    # Print metrics in rows of 3
    for i in range(0, len(metrics), 3):
        row = metrics[i : i + 3]
        print("  " + "  |  ".join(row))

    print("=" * 70)
