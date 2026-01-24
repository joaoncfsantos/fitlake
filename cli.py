#!/usr/bin/env python3
"""
Main CLI for fetching workouts from multiple fitness platforms.

Supported platforms:
  - Hevy (hevy.py) - Strength training
  - Strava (strava.py) - Cardio activities (running, cycling, etc.)
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

import platforms.hevy as hevy
import platforms.strava as strava

# Load environment variables
load_dotenv()


def print_help():
    """Print usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         FITLAKE CLI                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage: python cli.py <platform> <command> [options]

PLATFORMS:

  hevy          Strength training (Hevy)
  strava        Cardio activities (Strava - running, cycling, swimming, etc.)

SETUP COMMANDS:

  sync                Sync all data from the platform
  sync workouts       (Hevy) Sync workouts only
  sync templates      (Hevy) Sync exercise templates
  auth                (Strava) Show authentication setup instructions

INFO COMMANDS:

  schema              Show the data structure schema

DATA COMMANDS:

  workout <n>         (Hevy) Display the nth workout
  activity <n>        (Strava) Display the nth activity

ANALYSIS COMMANDS (Hevy):

  muscles <n>         Analyze muscle engagement for the nth workout
  muscles --days <n>  Analyze muscle engagement for the past N days
  recovery last       Find the most recent full recovery day
  recovery --days <n> Count recovery days in the past N days

ANALYSIS COMMANDS (Strava):

  stats               Show all-time activity statistics
  stats --days <n>    Show activity statistics for the past N days

EXAMPLES:

  # Hevy
  python cli.py hevy sync                 # Sync all Hevy data
  python cli.py hevy sync workouts        # Sync workouts only
  python cli.py hevy sync templates       # Sync exercise templates
  python cli.py hevy schema               # Show schema
  python cli.py hevy workout 5            # Show 5th workout
  python cli.py hevy muscles 1            # Analyze muscles for 1st workout
  python cli.py hevy muscles --days 7     # Analyze muscles for past week
  python cli.py hevy recovery last        # Find last recovery day
  python cli.py hevy recovery --days 14   # Recovery stats for past 2 weeks

  # Strava
  python cli.py strava auth               # Show authentication instructions
  python cli.py strava sync               # Sync all Strava activities
  python cli.py strava schema             # Show activity schema
  python cli.py strava activity 1         # Show most recent activity
  python cli.py strava stats              # Show all-time statistics
  python cli.py strava stats --days 30    # Show stats for past 30 days

ENVIRONMENT VARIABLES:

  Hevy:
    HEVY_API_KEY              Your Hevy API key (from hevy.com/settings?developer)

  Strava:
    STRAVA_CLIENT_ID          Your Strava API client ID
    STRAVA_CLIENT_SECRET      Your Strava API client secret
    STRAVA_REFRESH_TOKEN      Your Strava OAuth refresh token
    (Run 'python cli.py strava auth' for setup instructions)

""")


def handle_hevy(args: list[str]):
    """Handle Hevy-related commands."""
    if not args:
        print("Error: No command specified for Hevy.")
        print("Usage: python cli.py hevy <command>")
        print("Commands: sync, schema, workout <n>, muscles <n>")
        return
    
    command = args[0]
    
    # Commands that require API key
    if command == "sync":
        try:
            api_key = hevy.get_api_key()
        except ValueError as e:
            print(f"Configuration Error: {e}")
            return
        
        try:
            subcommand = args[1] if len(args) > 1 else None
            
            if subcommand is None:
                # Sync everything: workouts + templates
                print("Syncing all Hevy data...")
                workouts = hevy.fetch_all_workouts(api_key)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/exports/hevy_workouts_{timestamp}.csv"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                hevy.export_to_csv(workouts, filename)
                
                templates = hevy.fetch_all_exercise_templates(api_key)
                hevy.export_exercise_templates_to_csv(templates)
                print("\nAll Hevy data synced successfully.")
            
            elif subcommand == "workouts":
                workouts = hevy.fetch_all_workouts(api_key)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/exports/hevy_workouts_{timestamp}.csv"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                hevy.export_to_csv(workouts, filename)
            
            elif subcommand == "templates":
                templates = hevy.fetch_all_exercise_templates(api_key)
                hevy.export_exercise_templates_to_csv(templates)
            
            else:
                print(f"Error: Unknown sync target '{subcommand}'")
                print("Usage: python cli.py hevy sync [workouts|templates]")
        
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    # Commands that use local data (no API key required)
    if command == "schema":
        hevy.print_data_schema()
        return
    
    if command == "workout":
        try:
            if len(args) < 2:
                print("Error: 'workout' command requires a workout number.")
                print("Usage: python cli.py hevy workout <n>")
                return
            n = int(args[1])
            workout = hevy.get_nth_workout(n)
            if workout:
                print(json.dumps(workout, indent=2, default=str))
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    if command == "muscles":
        try:
            if len(args) >= 3 and args[1] == "--days":
                days = int(args[2])
                muscle_totals, total_sets, workout_count = hevy.analyze_muscles_for_period(days)
                if workout_count > 0:
                    hevy.print_muscle_analysis(muscle_totals, total_sets)
                else:
                    print(f"No workouts found in the past {days} days.")
            elif len(args) >= 2:
                n = int(args[1])
                muscle_totals, total_sets = hevy.analyze_workout_muscles(n)
                hevy.print_muscle_analysis(muscle_totals, total_sets)
            else:
                print("Error: 'muscles' command requires a workout number or --days flag.")
                print("Usage: python cli.py hevy muscles <n>")
                print("       python cli.py hevy muscles --days <n>")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    if command == "recovery":
        try:
            if len(args) >= 2 and args[1] == "last":
                print("Finding last recovery day...")
                date_str, days_ago = hevy.get_last_recovery_day()
                if date_str:
                    print(f"\nLast recovery day: {date_str} ({days_ago} day{'s' if days_ago != 1 else ''} ago)")
                else:
                    print("\nNo recovery day found in the past year!")
            elif len(args) >= 3 and args[1] == "--days":
                days = int(args[2])
                print(f"Analyzing recovery for the past {days} days...")
                recovery_count, workout_count, recovery_dates = hevy.count_recovery_days(days)
                hevy.print_recovery_analysis(recovery_count, workout_count, recovery_dates, days)
            else:
                print("Error: 'recovery' command requires 'last' or '--days <n>'.")
                print("Usage: python cli.py hevy recovery last")
                print("       python cli.py hevy recovery --days <n>")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    # Unknown command
    print(f"Error: Unknown command '{command}'")
    print("Use 'python cli.py help' for available commands.")


def handle_strava(args: list[str]):
    """Handle Strava-related commands."""
    if not args:
        print("Error: No command specified for Strava.")
        print("Usage: python cli.py strava <command>")
        print("Commands: auth, sync, schema, activity <n>, stats")
        return
    
    command = args[0]
    
    # Auth command (no credentials needed)
    if command == "auth":
        strava.print_auth_instructions()
        return
    
    # Schema command (no credentials needed)
    if command == "schema":
        strava.print_data_schema()
        return
    
    # Commands that require API credentials
    if command == "sync":
        try:
            print("Refreshing Strava access token...")
            access_token = strava.refresh_access_token()
            
            print("\nFetching athlete profile...")
            athlete = strava.fetch_athlete(access_token)
            print(f"  Logged in as: {athlete.get('firstname', '')} {athlete.get('lastname', '')}")
            
            activities = strava.fetch_all_activities(access_token)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/exports/strava_activities_{timestamp}.csv"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            strava.export_to_csv(activities, filename)
            
            print("\nStrava data synced successfully.")
            
        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        return
    
    # Commands that use local data (no API calls)
    if command == "activity":
        try:
            if len(args) < 2:
                print("Error: 'activity' command requires an activity number.")
                print("Usage: python cli.py strava activity <n>")
                return
            n = int(args[1])
            activity = strava.get_nth_activity(n)
            if activity:
                strava.print_activity_summary(activity)
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    if command == "stats":
        try:
            if len(args) >= 3 and args[1] == "--days":
                days = int(args[2])
                activities = strava.get_activities_since(days)
                if activities:
                    stats = strava.get_activity_stats(activities)
                    strava.print_activity_stats(stats, days)
                else:
                    print(f"No activities found in the past {days} days.")
            else:
                activities = strava.load_activities_from_csv()
                print(f"Loaded {len(activities)} activities from local data")
                stats = strava.get_activity_stats(activities)
                strava.print_activity_stats(stats)
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    # Unknown command
    print(f"Error: Unknown command '{command}'")
    print("Use 'python cli.py help' for available commands.")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    platform = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if platform == "hevy":
        handle_hevy(args)
    elif platform == "strava":
        handle_strava(args)
    elif platform in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"Unknown platform: {platform}")
        print("Supported platforms: hevy, strava")
        print("Use 'python cli.py help' for more information.")


if __name__ == "__main__":
    main()
