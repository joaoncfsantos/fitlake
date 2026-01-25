#!/usr/bin/env python3
"""
Main CLI entry point for FitLake.

This file serves as a thin wrapper that imports and runs the CLI
from the cli package. This maintains backward compatibility with
existing scripts that call `python cli.py`.

For the full implementation, see cli/main.py.
"""

from cli.main import main

if __name__ == "__main__":
    main()
