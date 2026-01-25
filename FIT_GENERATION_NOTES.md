# FIT File Generation - Technical Notes

## Issues Fixed

### Issue 1: Duration in Wrong Units
**Problem**: Duration was being passed in milliseconds instead of seconds
- Lap/Session/Activity messages showed ~60 seconds instead of ~2900 seconds

**Fix**: Convert timestamps to milliseconds for timestamp fields, but use seconds for duration fields
```python
start_timestamp_ms = datetime_to_fit_timestamp(start_time_str)  # milliseconds
total_duration_sec = total_duration_ms / 1000.0  # convert to seconds
lap.total_elapsed_time = total_duration_sec  # pass seconds
```

### Issue 2: Incorrect Set Type Mapping
**Problem**: Sets were showing as "rest" type instead of "active"
- Used `set_type = 0` which maps to "rest"

**Fix**: Use correct FIT set type values:
- 0 = Rest
- 1 = Active (working set)
- 2 = Warmup
- 3 = Failure
- 4 = Drop set

### Issue 3: Missing Set Durations
**Problem**: Sets didn't have individual durations specified

**Fix**: Estimate set duration based on reps (3 seconds per rep, minimum 30 seconds)
```python
set_duration_sec = max(30, reps * 3)
set_msg.duration = float(set_duration_sec)
```

## FIT File Structure

### Required Messages (in order)
1. **FileIdMessage** - Metadata about the file
   - `type = 4` (activity)
   - `manufacturer = 1` (Garmin)
   - `time_created` (Unix timestamp in milliseconds)

2. **EventMessage** (Start) - Timer start
   - `timestamp` (milliseconds)
   - `event = 0` (timer)
   - `event_type = 0` (start)

3. **SetMessage** (multiple) - One per set
   - `timestamp` (milliseconds)
   - `start_time` (milliseconds)
   - `duration` (seconds as float)
   - `weight` (kg as float)
   - `repetitions` (int)
   - `set_type` (int: 1 = active)
   - `message_index` (int, incremental)

4. **LapMessage** - Overall workout lap
   - `timestamp` (milliseconds)
   - `start_time` (milliseconds)
   - `total_elapsed_time` (seconds as float)
   - `total_timer_time` (seconds as float)

5. **SessionMessage** - Workout session
   - `timestamp` (milliseconds)
   - `start_time` (milliseconds)
   - `total_elapsed_time` (seconds as float)
   - `total_timer_time` (seconds as float)
   - `sport = 15` (strength training in FIT SDK, displays as "rowing" in fitparse)
   - `sub_sport = 20` (generic strength training)
   - `num_laps = 1`

6. **ActivityMessage** - Activity summary
   - `timestamp` (milliseconds)
   - `total_timer_time` (seconds as float)
   - `num_sessions = 1`
   - `type = 0` (manual)
   - `event = 26` (activity)
   - `event_type = 1` (stop)

7. **EventMessage** (Stop) - Timer stop
   - `timestamp` (milliseconds)
   - `event = 0` (timer)
   - `event_type = 4` (stop_all)

## Field Units

### Timestamp Fields
- **Input**: Unix timestamp in milliseconds
- **Fields**: `timestamp`, `start_time`, `time_created`
- **Library**: fit-tool automatically applies FIT epoch offset

### Duration Fields
- **Input**: Seconds as float
- **Fields**: `total_elapsed_time`, `total_timer_time`, `duration`
- **Storage**: Internally stored as milliseconds (scale=1000), but input is seconds

### Weight Fields
- **Input**: Kilograms as float
- **Field**: `weight`
- **Storage**: Internally scaled by 16 (scale=16)

## Validation

Use the debug script to inspect generated FIT files:
```bash
python debug_fit.py data/fit_files/workout.fit
```

Expected output for a valid strength training FIT file:
- **Duration**: Should match actual workout time (e.g., 2581.0 s for 43 minutes)
- **Sets**: Should match total number of sets in workout
- **Set type**: Should show "active" for normal working sets
- **Weight/reps**: Should match actual values from Hevy

## Garmin Connect Upload Response

Successful upload returns HTTP 202 (Accepted):
```json
{
    "summaryDTO": {
        "duration": 2581.0,
        "totalSets": 12,
        "activeSets": 12,
        "totalExerciseReps": 102
    }
}
```

## Known Limitations

1. **Exercise Categories**: Not mapped to Garmin's exercise catalog yet
2. **Rest Periods**: Not explicitly tracked between sets
3. **Notes**: Workout notes/descriptions not included
4. **Superset Indicator**: Not supported in basic FIT format
