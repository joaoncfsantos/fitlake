"""
Database setup and session management.

Uses SQLAlchemy ORM with PostgreSQL.
"""

import os
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_database_url() -> str:
    """Get and validate the database URL from environment."""
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please set it to a valid PostgreSQL connection string."
        )
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


@lru_cache(maxsize=1)
def get_engine():
    """Lazily create and cache the database engine."""
    return create_engine(
        get_database_url(),
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )


@lru_cache(maxsize=1)
def get_session_local():
    """Lazily create and cache the session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    """Initialize the database by creating all tables."""
    from db import models  # noqa: F401
    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session."""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for getting a database session."""
    db = get_session_local()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Backwards compatibility aliases (optional, for existing code)
# These will only fail when actually accessed, not at import
class _LazyEngine:
    def __getattr__(self, name):
        return getattr(get_engine(), name)

class _LazySessionLocal:
    def __call__(self):
        return get_session_local()()

engine = _LazyEngine()
SessionLocal = _LazySessionLocal()