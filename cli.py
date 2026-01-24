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
import platforms.garmin as garmin

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
  garmin        Health & fitness data (Garmin Connect)

SETUP COMMANDS:

  sync                Sync all data from the platform
  sync workouts       (Hevy) Sync workouts only
  sync templates      (Hevy) Sync exercise templates
  sync activities     (Garmin) Sync activities only
  auth                Show authentication setup instructions
  logout              (Garmin) Clear saved authentication tokens

INFO COMMANDS:

  schema              Show the data structure schema

DATA COMMANDS:

  workout <n>         (Hevy) Display the nth workout
  activity <n>        (Strava/Garmin) Display the nth activity
  today               (Garmin) Show today's health summary
  sleep               (Garmin) Show last night's sleep data

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

  # Garmin
  python cli.py garmin auth               # Show authentication instructions
  python cli.py garmin sync               # Sync daily stats (past 30 days)
  python cli.py garmin sync --days 7      # Sync daily stats (past 7 days)
  python cli.py garmin sync activities    # Sync all activities
  python cli.py garmin schema             # Show data schema
  python cli.py garmin today              # Show today's health summary
  python cli.py garmin sleep              # Show last night's sleep data
  python cli.py garmin activity 1         # Show most recent activity
  python cli.py garmin logout             # Clear saved tokens

ENVIRONMENT VARIABLES:

  Hevy:
    HEVY_API_KEY              Your Hevy API key (from hevy.com/settings?developer)

  Strava:
    STRAVA_CLIENT_ID          Your Strava API client ID
    STRAVA_CLIENT_SECRET      Your Strava API client secret
    STRAVA_REFRESH_TOKEN      Your Strava OAuth refresh token
    (Run 'python cli.py strava auth' for setup instructions)

  Garmin:
    GARMIN_EMAIL              Your Garmin Connect email
    GARMIN_PASSWORD           Your Garmin Connect password
    (Run 'python cli.py garmin auth' for setup instructions)

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
            access_token = strava.get_access_token()
            
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
    
    # Activity command (fetches detailed activity from API for calories etc.)
    if command == "activity":
        try:
            if len(args) < 2:
                print("Error: 'activity' command requires an activity number.")
                print("Usage: python cli.py strava activity <n>")
                return
            n = int(args[1])
            
            access_token = strava.get_access_token()
            
            activity = strava.get_detailed_activity(n, access_token)
            if activity:
                strava.print_activity_summary(activity)
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        return
    
    # Commands that use local data (no API calls)
    
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

def handle_garmin(args: list[str]):
    """Handle Garmin-related commands."""
    from datetime import date, timedelta

    if not args:
        print("Error: No command specified for Garmin.")
        print("Usage: python cli.py garmin <command>")
        print("Commands: auth, sync, schema, today, sleep, activity <n>, logout")
        return

    command = args[0]

    # Auth command (no credentials needed)
    if command == "auth":
        garmin.print_auth_instructions()
        return

    # Schema command (no credentials needed)
    if command == "schema":
        garmin.print_data_schema()
        return

    # Logout command
    if command == "logout":
        garmin.clear_tokens()
        return

    # Commands that require authentication
    if command == "sync":
        try:
            client = garmin.get_client()

            subcommand = args[1] if len(args) > 1 else None

            # Parse --days flag
            days = 30  # default
            if len(args) >= 3 and args[1] == "--days":
                days = int(args[2])
                subcommand = None
            elif len(args) >= 4 and args[2] == "--days":
                days = int(args[3])

            if subcommand == "activities":
                # Sync activities only
                activities = garmin.fetch_all_activities(client)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/exports/garmin_activities_{timestamp}.csv"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                garmin.export_activities_to_csv(activities, filename)

            else:
                # Sync daily stats (default)
                print(f"\nSyncing Garmin daily stats for the past {days} days...")
                end_date = date.today()
                start_date = end_date - timedelta(days=days - 1)

                all_stats = []
                all_sleep = []
                current_date = start_date

                while current_date <= end_date:
                    print(f"  Fetching {current_date}...")

                    # Fetch daily stats
                    try:
                        stats = garmin.fetch_daily_stats(client, current_date)
                        if stats:
                            stats["date"] = current_date.isoformat()
                            all_stats.append(stats)
                    except Exception as e:
                        print(f"    Warning: Could not fetch stats: {e}")

                    # Fetch sleep data
                    try:
                        sleep = garmin.fetch_sleep_data(client, current_date)
                        if sleep:
                            sleep["date"] = current_date.isoformat()
                            all_sleep.append(sleep)
                    except Exception:
                        pass

                    current_date += timedelta(days=1)

                # Export to CSV
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs("data/exports", exist_ok=True)

                if all_stats:
                    stats_filename = f"data/exports/garmin_daily_stats_{timestamp}.csv"
                    garmin.export_daily_stats_to_csv(all_stats, stats_filename)

                if all_sleep:
                    sleep_filename = f"data/exports/garmin_sleep_{timestamp}.csv"
                    garmin.export_sleep_to_csv(all_sleep, sleep_filename)

                print(f"\nGarmin data synced successfully.")
                print(f"  Daily stats: {len(all_stats)} days")
                print(f"  Sleep data:  {len(all_sleep)} days")

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        return

    if command == "today":
        try:
            client = garmin.get_client()
            today = date.today()

            print(f"\nFetching today's health data...")

            # Fetch today's stats
            stats = garmin.fetch_daily_stats(client, today)
            if stats:
                stats["date"] = today.isoformat()
                garmin.print_daily_summary(stats)

            # Try to fetch sleep (last night)
            sleep = garmin.fetch_sleep_data(client, today)
            if sleep:
                garmin.print_sleep_summary(sleep)

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        return

    if command == "sleep":
        try:
            client = garmin.get_client()
            today = date.today()

            print(f"\nFetching sleep data...")
            sleep = garmin.fetch_sleep_data(client, today)

            if sleep:
                garmin.print_sleep_summary(sleep)
            else:
                print("No sleep data available for last night.")

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        return

    if command == "activity":
        try:
            if len(args) < 2:
                print("Error: 'activity' command requires an activity number.")
                print("Usage: python cli.py garmin activity <n>")
                return

            n = int(args[1])
            if n < 1:
                print("Error: Activity number must be >= 1")
                return

            client = garmin.get_client()

            print(f"\nFetching activity #{n}...")
            activities = garmin.fetch_activities(client, start=n - 1, limit=1)

            if activities:
                garmin.print_activity_summary(activities[0])
            else:
                print(f"Activity #{n} not found.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
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
    elif platform == "garmin":
        handle_garmin(args)
    elif platform in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"Unknown platform: {platform}")
        print("Supported platforms: hevy, strava, garmin")
        print("Use 'python cli.py help' for more information.")


if __name__ == "__main__":
    main()
