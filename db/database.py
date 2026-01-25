"""
Database setup and session management.

Uses SQLAlchemy ORM with PostgreSQL.

Usage:
    from db import SessionLocal, init_db

    init_db()
"""

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL","")

if DATABASE_URL.startswith("postgres://"):    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


engine = create_engine(
    DATABASE_URL,
    pool_size=5,           
    max_overflow=10,       
    pool_pre_ping=True,    
    pool_recycle=300,      
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
