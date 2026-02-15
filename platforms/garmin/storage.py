"""
CSV storage operations for Garmin Connect data.
"""

import csv
import glob
import json
from datetime import datetime, timedelta, timezone
from typing import Any


def export_daily_stats_to_csv(
    stats_list: list[dict[str, Any]], filename: str = "garmin_daily_stats.csv"
) -> None:
    """
    Export daily statistics to a CSV file.

    Args:
        stats_list: List of daily stats dicts
        filename: Output filename
    """
    if not stats_list:
        print("No daily stats to export.")
        return

    # Define CSV columns for daily stats
    columns = [
        "date",
        "totalSteps",
        "dailyStepGoal",
        "totalDistanceMeters",
        "totalKilocalories",
        "activeKilocalories",
        "bmrKilocalories",
        "wellnessKilocalories",
        "floorsAscended",
        "floorsDescended",
        "minHeartRate",
        "maxHeartRate",
        "restingHeartRate",
        "averageStressLevel",
        "maxStressLevel",
        "stressDuration",
        "restStressDuration",
        "activityStressDuration",
        "lowStressDuration",
        "mediumStressDuration",
        "highStressDuration",
        "moderateIntensityMinutes",
        "vigorousIntensityMinutes",
        "intensityMinutesGoal",
        "sleepingSeconds",
        "bodyBatteryChargedValue",
        "bodyBatteryDrainedValue",
        "bodyBatteryHighestValue",
        "bodyBatteryLowestValue",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()

        for stats in stats_list:
            row = {col: stats.get(col) for col in columns}
            writer.writerow(row)

    print(f"Exported {len(stats_list)} days of stats to {filename}")


def export_sleep_to_csv(
    sleep_list: list[dict[str, Any]], filename: str = "garmin_sleep.csv"
) -> None:
    """
    Export sleep data to a CSV file.

    Args:
        sleep_list: List of sleep data dicts
        filename: Output filename
    """
    if not sleep_list:
        print("No sleep data to export.")
        return

    columns = [
        "date",
        "sleepTimeSeconds",
        "napTimeSeconds",
        "deepSleepSeconds",
        "lightSleepSeconds",
        "remSleepSeconds",
        "awakeSleepSeconds",
        "sleepStartTimestampLocal",
        "sleepEndTimestampLocal",
        "averageSpO2Value",
        "lowestSpO2Value",
        "averageRespirationValue",
        "lowestRespirationValue",
        "highestRespirationValue",
        "avgHeartRate",
        "sleepScores"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()

        for sleep in sleep_list:
            row = {"date": sleep.get("date")}

            # Flatten daily sleep data
            daily_sleep = sleep.get("dailySleepDTO", {})
            for key in [
                "sleepTimeSeconds",
                "napTimeSeconds",
                "deepSleepSeconds",
                "lightSleepSeconds",
                "remSleepSeconds",
                "awakeSleepSeconds",
                "sleepStartTimestampLocal",
                "sleepEndTimestampLocal",
                "averageSpO2Value",
                "lowestSpO2Value",
                "averageRespirationValue",
                "lowestRespirationValue",
                "highestRespirationValue",
                "avgHeartRate",
                "sleepScores",
            ]:
                row[key] = daily_sleep.get(key)

            # Extract sleep scores
            sleep_scores = sleep.get("sleepScores", {})
            overall = sleep_scores.get("overall", {})
            row["sleepScores_overall_value"] = overall.get("value")

            total_duration = sleep_scores.get("totalDuration", {})
            row["sleepScores_totalDuration_qualifierKey"] = total_duration.get(
                "qualifierKey"
            )

            writer.writerow(row)

    print(f"Exported {len(sleep_list)} days of sleep data to {filename}")


def export_activities_to_csv(
    activities: list[dict[str, Any]], filename: str = "garmin_activities.csv"
) -> None:
    """
    Export activities to a CSV file.

    Args:
        activities: List of activity dicts
        filename: Output filename
    """
    if not activities:
        print("No activities to export.")
        return

    columns = [
        "activityId",
        "activityName",
        "activityType",
        "sportType",
        "startTimeLocal",
        "startTimeGMT",
        "distance",
        "duration",
        "elapsedDuration",
        "movingDuration",
        "elevationGain",
        "elevationLoss",
        "averageSpeed",
        "maxSpeed",
        "calories",
        "bmrCalories",
        "averageHR",
        "maxHR",
        "averageRunningCadenceInStepsPerMinute",
        "maxRunningCadenceInStepsPerMinute",
        "steps",
        "avgPower",
        "maxPower",
        "normPower",
        "aerobicTrainingEffect",
        "anaerobicTrainingEffect",
        "trainingEffectLabel",
        "activityTrainingLoad",
        "minTemperature",
        "maxTemperature",
        "vO2MaxValue",
        "lactateThresholdBpm",
        "deviceId",
        "locationName",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()

        for activity in activities:
            row = {}
            for col in columns:
                value = activity.get(col)
                # Handle nested activityType
                if col == "activityType" and isinstance(value, dict):
                    value = value.get("typeKey", str(value))
                elif col == "sportType" and isinstance(
                    activity.get("activityType"), dict
                ):
                    value = activity.get("activityType", {}).get("typeKey")
                row[col] = value
            writer.writerow(row)

    print(f"Exported {len(activities)} activities to {filename}")


def get_latest_daily_stats_csv() -> str:
    """
    Find the most recent garmin_daily_stats CSV file in data/exports.

    Returns:
        Path to the most recent CSV file

    Raises:
        FileNotFoundError: If no stats CSV files exist
    """
    pattern = "data/exports/garmin_daily_stats_*.csv"
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            "No Garmin daily stats found. Run 'python cli.py garmin sync' first."
        )

    return sorted(files)[-1]


def get_latest_activities_csv() -> str:
    """
    Find the most recent garmin_activities CSV file in data/exports.

    Returns:
        Path to the most recent CSV file

    Raises:
        FileNotFoundError: If no activity CSV files exist
    """
    pattern = "data/exports/garmin_activities_*.csv"
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            "No Garmin activities found. Run 'python cli.py garmin sync' first."
        )

    return sorted(files)[-1]


def load_daily_stats_from_csv(filename: str | None = None) -> list[dict[str, Any]]:
    """
    Load daily stats from a CSV file.

    Args:
        filename: Path to CSV file. If None, uses the most recent export.

    Returns:
        List of daily stats dicts
    """
    if filename is None:
        filename = get_latest_daily_stats_csv()

    stats = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for field in [
                "totalSteps",
                "dailyStepGoal",
                "totalDistanceMeters",
                "totalKilocalories",
                "activeKilocalories",
                "bmrKilocalories",
                "floorsAscended",
                "floorsDescended",
                "minHeartRate",
                "maxHeartRate",
                "restingHeartRate",
                "averageHeartRate",
                "averageStressLevel",
                "maxStressLevel",
                "moderateIntensityMinutes",
                "vigorousIntensityMinutes",
                "sleepingSeconds",
            ]:
                if row.get(field):
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        pass
            stats.append(row)

    return stats


def load_activities_from_csv(filename: str | None = None) -> list[dict[str, Any]]:
    """
    Load activities from a CSV file.

    Args:
        filename: Path to CSV file. If None, uses the most recent export.

    Returns:
        List of activity dicts
    """
    if filename is None:
        filename = get_latest_activities_csv()

    activities = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for field in [
                "distance",
                "duration",
                "elapsedDuration",
                "movingDuration",
                "elevationGain",
                "elevationLoss",
                "averageSpeed",
                "maxSpeed",
                "calories",
                "averageHR",
                "maxHR",
                "steps",
                "avgPower",
                "maxPower",
            ]:
                if row.get(field):
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        pass
            activities.append(row)

    return activities


def get_latest_sleep_csv() -> str:
    """
    Find the most recent garmin_sleep CSV file in data/exports.

    Returns:
        Path to the most recent CSV file

    Raises:
        FileNotFoundError: If no sleep CSV files exist
    """
    pattern = "data/exports/garmin_sleep_*.csv"
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            "No Garmin sleep data found. Run 'python cli.py garmin sync' first."
        )

    return sorted(files)[-1]


def load_sleep_from_csv(filename: str | None = None) -> list[dict[str, Any]]:
    """
    Load sleep data from a CSV file.

    Args:
        filename: Path to CSV file. If None, uses the most recent export.

    Returns:
        List of sleep data dicts
    """
    if filename is None:
        filename = get_latest_sleep_csv()

    sleep_data = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for field in [
                "sleepTimeSeconds",
                "napTimeSeconds",
                "deepSleepSeconds",
                "lightSleepSeconds",
                "remSleepSeconds",
                "awakeSleepSeconds",
                "sleepStartTimestampLocal",
                "sleepEndTimestampLocal",
                "averageSpO2Value",
                "lowestSpO2Value",
                "averageRespirationValue",
                "lowestRespirationValue",
                "highestRespirationValue",
                "avgHeartRate",
            ]:
                if row.get(field):
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        pass
            sleep_data.append(row)

    return sleep_data


def get_stats_since(days: int) -> list[dict[str, Any]]:
    """
    Get daily stats from the past N days from locally synced data.

    Args:
        days: Number of days to look back

    Returns:
        List of stats dicts within the date range
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    stats = load_daily_stats_from_csv()

    stats_in_range = []
    for stat in stats:
        date_str = stat.get("date")
        if not date_str:
            continue

        try:
            stat_date = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        if stat_date >= cutoff_date:
            stats_in_range.append(stat)

    print(f"Found {len(stats_in_range)} days of stats in the past {days} days")
    return stats_in_range
