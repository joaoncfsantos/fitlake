"""
FastAPI application initialization.

Run with:
    uvicorn api.main:app --reload

Or:
    python -m uvicorn api.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from db import init_db

from .routes import activities, workouts, sync, daily_stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Initializes the database on startup.
    """
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown: Nothing to clean up


app = FastAPI(
    title="FitLake API",
    description="API for fitness data from multiple platforms (Hevy, Strava, Garmin)",
    version="1.0.0",
    lifespan=lifespan,
)

load_dotenv()


# Include routers
app.include_router(activities.router, prefix="/api/v1", tags=["activities"])
app.include_router(workouts.router, prefix="/api/v1", tags=["workouts"])
app.include_router(sync.router, prefix="/api/v1", tags=["sync"])
app.include_router(daily_stats.router, prefix="/api/v1", tags=["daily-stats"])


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "fitlake-api"}


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "sqlite",
        "version": "1.0.0",
    }
