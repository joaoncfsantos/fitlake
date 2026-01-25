#!/usr/bin/env python3
"""
Debug script to inspect FIT file contents using fitparse.
"""

import sys
from fitparse import FitFile
from datetime import datetime


def inspect_fit_file(fit_path: str):
    """Print details about a FIT file."""
    print(f"Inspecting: {fit_path}\n")
    
    fitfile = FitFile(fit_path)
    
    # Count messages by type
    msg_counts = {}
    messages_by_type = {}
    
    for record in fitfile.get_messages():
        msg_name = record.name
        if msg_name not in msg_counts:
            msg_counts[msg_name] = 0
            messages_by_type[msg_name] = []
        msg_counts[msg_name] += 1
        messages_by_type[msg_name].append(record)
    
    print("=" * 70)
    print("MESSAGE SUMMARY")
    print("=" * 70)
    for msg_name in sorted(msg_counts.keys()):
        print(f"{msg_name:20s}: {msg_counts[msg_name]} message(s)")
    
    # Show details for each type
    for msg_name in sorted(messages_by_type.keys()):
        messages = messages_by_type[msg_name]
        print(f"\n{'=' * 70}")
        print(f"{msg_name.upper()} ({len(messages)} messages)")
        print("=" * 70)
        
        for i, message in enumerate(messages):
            # Only show first 3 and last 2 if more than 5
            if len(messages) > 5 and i >= 3 and i < len(messages) - 2:
                if i == 3:
                    print(f"\n  ... {len(messages) - 5} more messages ...\n")
                continue
            
            print(f"\n  [{i+1}] {msg_name}:")
            
            for field in message.fields:
                value = field.value
                if value is not None:
                    units = f" {field.units}" if field.units else ""
                    
                    # Format timestamps nicely
                    if field.name in ['timestamp', 'start_time', 'time_created'] and isinstance(value, datetime):
                        print(f"    {field.name:25s}: {value.isoformat()}")
                    else:
                        print(f"    {field.name:25s}: {value}{units}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_fit.py <path/to/file.fit>")
        sys.exit(1)
    
    inspect_fit_file(sys.argv[1])
