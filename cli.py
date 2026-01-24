#!/usr/bin/env python3
"""
Main CLI for fetching workouts from multiple fitness platforms.

Supported platforms:
  - Hevy (hevy.py)
"""

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

  hevy          Fetch workouts from Hevy (strength training)

COMMANDS:

  print [n]     Show the data structure of the nth workout/activity (default: 1)
                Displays both the original API response and the flattened version.

  all           Fetch all workouts/activities and export to a timestamped CSV file.

  <n>           Fetch and display the nth workout/activity directly.

  (Hevy only):
  templates     Fetch all exercise templates and save to data/exercise_templates.csv.
                This is a one-time setup command.

  muscles <n>   Analyze muscle group engagement for the nth workout.
                Shows weighted sets per muscle (primary=1, secondary=0.5).

  muscles-period <days>
                Analyze muscle group engagement for all workouts in the past
                N days. Aggregates data across multiple workouts.

EXAMPLES:

  Hevy:
    python cli.py hevy print        # Show structure of 1st Hevy workout
    python cli.py hevy print 25     # Show structure of 25th Hevy workout
    python cli.py hevy 5            # Fetch 5th Hevy workout
    python cli.py hevy all          # Export all Hevy workouts to CSV
    python cli.py hevy templates    # Fetch all exercise templates (one-time)
    python cli.py hevy muscles 1    # Analyze muscles for 1st workout
    python cli.py hevy muscles-period 7  # Analyze muscles for past 7 days


ENVIRONMENT VARIABLES:

  Hevy:
    HEVY_API_KEY          Your Hevy API key (from hevy.com/settings?developer)

""")


def handle_hevy(args: list[str]):
    """Handle Hevy-related commands."""
    try:
        api_key = hevy.get_api_key()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return
    
    if not args:
        print("Error: No command specified for Hevy.")
        print("Usage: python cli.py hevy <command>")
        print("Commands: print [n], all, <n>")
        return
    
    command = args[0]
    
    try:
        if command == "print":
            n = int(args[1]) if len(args) > 1 else 1
            hevy.print_data_structures(api_key, n)
        
        elif command == "all":
            workouts = hevy.fetch_all_workouts(api_key)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/exports/hevy_workouts_{timestamp}.csv"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            hevy.export_to_csv(workouts, filename)
        
        elif command == "templates":
            templates = hevy.fetch_all_exercise_templates(api_key)
            hevy.export_exercise_templates_to_csv(templates)
        
        elif command == "muscles":
            if len(args) < 2:
                print("Error: 'muscles' command requires a workout number.")
                print("Usage: python cli.py hevy muscles <n>")
                return
            n = int(args[1])
            muscle_totals, total_sets = hevy.analyze_workout_muscles(api_key, n)
            hevy.print_muscle_analysis(muscle_totals, total_sets)
        
        elif command == "muscles-period":
            if len(args) < 2:
                print("Error: 'muscles-period' command requires number of days.")
                print("Usage: python cli.py hevy muscles-period <days>")
                return
            days = int(args[1])
            muscle_totals, total_sets, workout_count = hevy.analyze_muscles_for_period(api_key, days)
            if workout_count > 0:
                hevy.print_muscle_analysis(muscle_totals, total_sets)
            else:
                print(f"No workouts found in the past {days} days.")
        
        else:
            # Assume it's a number - fetch nth workout
            n = int(command)
            hevy.print_data_structures(api_key, n)
    
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
