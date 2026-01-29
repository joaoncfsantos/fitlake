import datetime
from db.models.daily_stats import DailyStats
from sqlalchemy import func
from sqlalchemy.orm import Session

def create_daily_stat(db: Session, daily_stat: DailyStats) -> DailyStats:
    """
    Create a new daily stat in the database.
    """
    db.add(daily_stat)
    db.commit()
    db.refresh(daily_stat)
    return daily_stat

def get_daily_stat_date(db: Session, platform: str, date: datetime) -> DailyStats:
    """
    Get a daily stat by platform and date.
    """
    return db.query(DailyStats).filter(
        DailyStats.platform == platform,
        func.date(DailyStats.date) == func.date(date)
    ).first()

def upsert_daily_stat(db: Session, daily_stat: DailyStats) -> DailyStats:
    """
    Create or update a daily stat based on platform and date.
    """
    existing = get_daily_stat_date(db, daily_stat.platform, daily_stat.date)
    if existing:
        # Delete existing daily stat
        db.delete(existing)
        db.flush()
    return create_daily_stat(db, daily_stat)