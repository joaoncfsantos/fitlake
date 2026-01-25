# Hevy to Garmin Connect Import Guide

This guide explains how to import your Hevy strength training workouts to Garmin Connect.

## Overview

The system filters out cardio-only workouts from Hevy (workouts with only 1 exercise of type "cardio"), converts strength training workouts to FIT format, and uploads them to Garmin Connect.

## Requirements

- Python 3.11+
- All dependencies installed: `pip install -r requirements.txt`
- Hevy workout data synced locally
- Garmin Connect credentials configured

## Workflow

### Step 1: Sync Hevy Data

First, ensure you have the latest workout data from Hevy:

```bash
python cli.py hevy sync
```

This will:
- Fetch all workouts from Hevy API
- Fetch exercise templates (needed for filtering cardio exercises)
- Save to `data/exports/hevy_workouts_YYYYMMDD_HHMMSS.csv`

### Step 2: Filter Workouts (Optional)

To see which workouts will be imported (excluding cardio-only):

```bash
python cli.py hevy export-for-garmin
```

This creates a filtered CSV file with only strength training workouts. The filter excludes any workout that:
- Has exactly 1 exercise
- That exercise has primary_muscle_group = "cardio"

Example excluded workouts:
- Running sessions
- Cycling sessions
- Swimming sessions

### Step 3: Generate FIT File for One Workout (Testing)

Generate a FIT file for a specific workout to test:

```bash
python cli.py hevy generate-fit <workout_number>
```

Example:
```bash
python cli.py hevy generate-fit 1  # Generate FIT for most recent workout
```

The FIT file will be saved to `data/fit_files/<workout_title>_<date>.fit`

### Step 4: Upload FIT File to Garmin Connect

Upload the generated FIT file:

```bash
python cli.py garmin upload-fit data/fit_files/<filename>.fit
```

Example:
```bash
python cli.py garmin upload-fit data/fit_files/Leg_\(High_reps\)_2026-01-24.fit
```

You should see:
```
✓ Success! Activity uploaded to Garmin Connect.
Response: <Response [202]>
```

## FIT File Structure

The generated FIT files include:

### Messages
1. **File ID** - Identifies the file as an activity
2. **Event (Start)** - Timer start event
3. **Set Messages** - One for each set in the workout, containing:
   - Timestamp
   - Weight (in kg)
   - Repetitions
   - Duration (if available)
   - Set type (normal, warmup, failure, drop set)
4. **Lap Message** - Overall workout lap
5. **Session Message** - Workout session (sport type: Strength Training)
6. **Activity Message** - Activity summary
7. **Event (Stop)** - Timer stop event

### Set Types Mapping
- `normal` → FIT Active (1)
- `warmup` → FIT Warmup (2)
- `failure` → FIT Failure (3)
- `drop_set` → FIT Drop (4)
- Note: FIT type 0 = Rest (not used for working sets)

## Verification

After uploading, verify the workout appears in Garmin Connect:
1. Go to https://connect.garmin.com/modern/activities
2. Look for your uploaded workout
3. Check that sets, reps, and weights are displayed correctly

## Notes

- **DO NOT** upload all workouts at once initially - test with one first!
- FIT files are small (typically < 1KB per workout)
- The workout time is distributed evenly across all sets
- Exercise categories are not yet mapped to Garmin's exercise catalog (future improvement)
- Each set gets an incremental message index

## Troubleshooting

### "Configuration Error: HEVY_API_KEY not found"
- Add your Hevy API key to `.env` file
- Get it from https://hevy.com/settings?developer

### "Configuration Error: GARMIN_EMAIL not found"
- Add your Garmin credentials to `.env` file
- See: `python cli.py garmin auth`

### "Error generating FIT file"
- Ensure the workout has valid start_time and end_time
- Check that exercises have sets with data

### Upload fails with 4xx/5xx error
- Verify your Garmin credentials are correct
- Try logging in to Garmin Connect in a browser first
- Run `python cli.py garmin logout` and re-authenticate

### Activity shows incorrect duration
- This was fixed in the latest version
- Duration fields now correctly use seconds (not milliseconds)
- Regenerate the FIT file with: `python cli.py hevy generate-fit <n>`

### Sets show as "rest" type instead of "active"
- This was fixed in the latest version
- FIT type 1 = Active (working sets)
- FIT type 0 = Rest (between sets)
- Regenerate the FIT file with the corrected mapping

### Missing sets or incorrect set count
- Ensure the workout has valid set data (weight, reps, or duration)
- Check the FIT file with: `python debug_fit.py data/fit_files/workout.fit`
- Each set should have its own SetMessage

## Future Improvements

- [ ] Map Hevy exercise names to Garmin exercise categories
- [ ] Batch upload multiple workouts
- [ ] Skip already uploaded workouts (duplicate detection)
- [ ] Add REST periods between sets
- [ ] Include notes/descriptions in the activity
