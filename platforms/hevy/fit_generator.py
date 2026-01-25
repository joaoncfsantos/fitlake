"""
Generate FIT files from Hevy workout data for Garmin Connect import.
"""

from datetime import datetime, timezone
from typing import Any

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.set_message import SetMessage
from fit_tool.profile.messages.event_message import EventMessage


# FIT constants
FIT_EPOCH = datetime(1989, 12, 31, 0, 0, 0, tzinfo=timezone.utc)


def datetime_to_fit_timestamp(dt_str: str) -> int:
    """
    Convert ISO datetime string to FIT timestamp for fit-tool library.
    
    The fit-tool library expects Unix timestamp in milliseconds.
    It will automatically handle the FIT epoch offset.
    
    Args:
        dt_str: ISO format datetime string (e.g., "2026-01-24T09:51:43+00:00")
        
    Returns:
        Unix timestamp in milliseconds since Jan 1, 1970 00:00:00 UTC
    """
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)  # Convert to milliseconds


def get_set_type(set_data: dict[str, Any]) -> int:
    """
    Map Hevy set type to FIT set type.
    
    FIT Set Types (based on actual testing):
    0 = Rest
    1 = Active (normal working set)
    2 = Warmup
    3 = Failure
    4 = Drop
    
    Args:
        set_data: Hevy set dict
        
    Returns:
        FIT set type integer
    """
    set_type = set_data.get("type", "normal")
    
    if set_type == "warmup":
        return 2
    elif set_type == "failure":
        return 3
    elif set_type == "drop_set":
        return 4
    else:
        # normal, unknown - use Active
        return 1


def generate_fit_file(workout: dict[str, Any], output_path: str) -> str:
    """
    Generate a FIT file from a Hevy workout.
    
    Args:
        workout: Hevy workout dict with exercises and sets
        output_path: Path to save the .fit file
        
    Returns:
        Path to the generated FIT file
    """
    builder = FitFileBuilder(auto_define=True, min_string_size=0)
    
    # Parse times
    start_time_str = workout.get("start_time")
    end_time_str = workout.get("end_time")
    
    if not start_time_str or not end_time_str:
        raise ValueError("Workout must have start_time and end_time")
    
    start_timestamp_ms = datetime_to_fit_timestamp(start_time_str)
    end_timestamp_ms = datetime_to_fit_timestamp(end_time_str)
    total_duration_ms = end_timestamp_ms - start_timestamp_ms
    total_duration_sec = total_duration_ms / 1000.0  # Convert to seconds for time fields
    
    # 1. File ID Message (required)
    file_id = FileIdMessage()
    file_id.type = 4  # Activity file
    file_id.manufacturer = 1  # Garmin
    file_id.product = 0
    file_id.time_created = start_timestamp_ms
    file_id.serial_number = 0
    builder.add(file_id)
    
    # 2. Event Message - Timer Start
    event_start = EventMessage()
    event_start.timestamp = start_timestamp_ms
    event_start.event = 0  # Timer
    event_start.event_type = 0  # Start
    builder.add(event_start)
    
    # 3. Process exercises and sets
    exercises = workout.get("exercises", [])
    set_index = 0
    current_time_ms = start_timestamp_ms
    
    # Estimate time per set (assume 60 seconds per set + rest between)
    total_sets = sum(len(ex.get("sets", [])) for ex in exercises)
    if total_sets > 0:
        avg_time_per_set_ms = total_duration_ms / total_sets
    else:
        avg_time_per_set_ms = 0
    
    for exercise in exercises:
        exercise_title = exercise.get("title", "Unknown")
        sets = exercise.get("sets", [])
        
        for set_data in sets:
            set_msg = SetMessage()
            
            # Timestamp for this set
            set_msg.timestamp = current_time_ms
            set_msg.start_time = current_time_ms
            
            # Estimate set duration (use actual if available, otherwise estimate)
            set_duration_sec = set_data.get("duration_seconds")
            if not set_duration_sec:
                # Estimate: 3 seconds per rep, minimum 30 seconds
                reps = set_data.get("reps", 10)
                set_duration_sec = max(30, reps * 3)
            
            set_msg.duration = float(set_duration_sec)
            
            # Set basic data
            weight_kg = set_data.get("weight_kg")
            if weight_kg:
                set_msg.weight = float(weight_kg)
            
            reps = set_data.get("reps")
            if reps:
                set_msg.repetitions = int(reps)
            
            # Set type
            set_msg.set_type = get_set_type(set_data)
            
            # Message index
            set_msg.message_index = set_index
            
            # TODO: Map exercise names to FIT categories
            # For now, leave category unset (optional)
            
            builder.add(set_msg)
            
            # Advance time for next set
            current_time_ms += int(avg_time_per_set_ms)
            set_index += 1
    
    # 4. Lap Message
    lap = LapMessage()
    lap.timestamp = end_timestamp_ms
    lap.start_time = start_timestamp_ms
    lap.total_elapsed_time = total_duration_sec  # Seconds
    lap.total_timer_time = total_duration_sec  # Seconds
    builder.add(lap)
    
    # 5. Session Message
    session = SessionMessage()
    session.timestamp = end_timestamp_ms
    session.start_time = start_timestamp_ms
    session.total_elapsed_time = total_duration_sec  # Seconds
    session.total_timer_time = total_duration_sec  # Seconds
    session.sport = 15  # Strength training
    session.sub_sport = 20  # Generic strength training
    session.first_lap_index = 0
    session.num_laps = 1
    builder.add(session)
    
    # 6. Activity Message
    activity = ActivityMessage()
    activity.timestamp = end_timestamp_ms
    activity.total_timer_time = total_duration_sec  # Seconds
    activity.num_sessions = 1
    activity.type = 0  # Manual
    activity.event = 26  # Activity
    activity.event_type = 1  # Stop
    builder.add(activity)
    
    # 7. Event Message - Timer Stop
    event_stop = EventMessage()
    event_stop.timestamp = end_timestamp_ms
    event_stop.event = 0  # Timer
    event_stop.event_type = 4  # Stop_all
    builder.add(event_stop)
    
    # Build and write the FIT file
    fit_file = builder.build()
    fit_file.to_file(output_path)
    
    return output_path
