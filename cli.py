#!/usr/bin/env python3
"""
Main CLI for fetching workouts from multiple fitness platforms.

Supported platforms:
  - Hevy (hevy.py)
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

import platforms.hevy as hevy

# Load environment variables
load_dotenv()


def print_help():
    """Print usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         WORKOUT FETCHER CLI                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage: python cli.py <platform> <command> [options]

PLATFORMS:

  hevy          Strength training (Hevy)

SETUP COMMANDS:

  sync                Sync all data from the platform (workouts + templates)
  sync workouts       Sync workouts only (exports to timestamped CSV)
  sync templates      (Hevy only) Sync exercise templates to data/exercise_templates.csv

INFO COMMANDS:

  schema              Show the data structure schema of workouts

DATA COMMANDS:

  workout <n>         Display the nth workout/activity

ANALYSIS COMMANDS:

  muscles <n>         Analyze muscle engagement for the nth workout
                      Shows weighted sets per muscle (primary=1, secondary=0.5)
  muscles --days <n>  Analyze muscle engagement for the past N days
                      Aggregates data across multiple workouts

  recovery last       Find the most recent full recovery day
  recovery --days <n> Count recovery days in the past N days

EXAMPLES:

  python cli.py hevy sync                 # Sync all Hevy data
  python cli.py hevy sync workouts        # Sync workouts only
  python cli.py hevy sync templates       # Sync exercise templates
  python cli.py hevy schema               # Show schema
  python cli.py hevy workout 5            # Show 5th workout
  python cli.py hevy muscles 1            # Analyze muscles for 1st workout
  python cli.py hevy muscles --days 7     # Analyze muscles for past week
  python cli.py hevy recovery last        # Find last recovery day
  python cli.py hevy recovery --days 14   # Recovery stats for past 2 weeks

ENVIRONMENT VARIABLES:

  Hevy:
    HEVY_API_KEY          Your Hevy API key (from hevy.com/settings?developer)

""")


def handle_hevy(args: list[str]):
    """Handle Hevy-related commands."""
    if not args:
        print("Error: No command specified for Hevy.")
        print("Usage: python cli.py hevy <command>")
        print("Commands: sync, schema, workout <n>, muscles <n>")
        return
    
    command = args[0]
    
    # Commands that don't require API key
    if command == "schema":
        hevy.print_data_schema()
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
    
    # All other commands require API key
    try:
        api_key = hevy.get_api_key()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return
    
    try:
        if command == "sync":
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
        
        elif command == "workout":
            if len(args) < 2:
                print("Error: 'workout' command requires a workout number.")
                print("Usage: python cli.py hevy workout <n>")
                return
            n = int(args[1])
            workout = hevy.fetch_nth_workout(api_key, n)
            if workout:
                print(json.dumps(workout, indent=2, default=str))
        
        elif command == "muscles":
            # Check for --days flag
            if len(args) >= 3 and args[1] == "--days":
                days = int(args[2])
                muscle_totals, total_sets, workout_count = hevy.analyze_muscles_for_period(api_key, days)
                if workout_count > 0:
                    hevy.print_muscle_analysis(muscle_totals, total_sets)
                else:
                    print(f"No workouts found in the past {days} days.")
            elif len(args) >= 2:
                n = int(args[1])
                muscle_totals, total_sets = hevy.analyze_workout_muscles(api_key, n)
                hevy.print_muscle_analysis(muscle_totals, total_sets)
            else:
                print("Error: 'muscles' command requires a workout number or --days flag.")
                print("Usage: python cli.py hevy muscles <n>")
                print("       python cli.py hevy muscles --days <n>")
        
        else:
            print(f"Error: Unknown command '{command}'")
            print("Use 'python cli.py help' for available commands.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    platform = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if platform == "hevy":
        handle_hevy(args)
    elif platform in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"Unknown platform: {platform}")
        print("Supported platforms: hevy")
        print("Use 'python cli.py help' for more information.")


if __name__ == "__main__":
    main()
