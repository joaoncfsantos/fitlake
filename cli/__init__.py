"""
CLI package for FitLake.

The CLI is separate from the API and does not import FastAPI.
It uses the shared database layer (db/) and core services (core/).
"""

from .main import main

__all__ = ["main"]
