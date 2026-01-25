"""
Core domain logic for FitLake.

Contains shared services and business logic that can be used by
both the CLI and the API.
"""

from .services import sync_service

__all__ = ["sync_service"]
