"""
FastAPI application package for FitLake.

Run with: uvicorn api.main:app --reload
"""

from .main import app

__all__ = ["app"]
