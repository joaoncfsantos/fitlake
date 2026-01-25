"""
Database setup and session management.

Uses SQLAlchemy ORM with SQLite. The design avoids database-specific
features to allow easy migration to PostgreSQL later.

Usage:
    from db import SessionLocal, init_db

    # Initialize tables on startup
    init_db()

    # Get a session
    with SessionLocal() as session:
        # ... use session ...
"""

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Database URL - defaults to SQLite file in project root
# To switch to PostgreSQL, change to: "postgresql://user:pass@localhost/fitlake"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitlake.db")

# SQLite-specific: check_same_thread is only needed for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Set SQL_ECHO=true to see queries
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Call this on application startup to ensure tables exist.
    """
    # Import all models here so they are registered with Base.metadata
    from db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Used with FastAPI's dependency injection:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...

    The session is automatically closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for getting a database session.

    Used in CLI and scripts:
        from db import get_db_session

        with get_db_session() as db:
            # ... use db ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
