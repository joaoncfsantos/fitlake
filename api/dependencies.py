"""
FastAPI dependency injection.

Provides reusable dependencies for database sessions and other shared resources.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db

# Type alias for database session dependency
# Usage: def endpoint(db: DbSession): ...
DbSession = Annotated[Session, Depends(get_db)]
