"""
API key authentication.

Simple authentication for personal use. All requests must include
a valid API key in the X-API-Key header.

Usage:
    from api.auth import require_api_key

    @router.get("/protected")
    def protected_route(api_key: str = Depends(require_api_key)):
        return {"message": "You're authenticated!"}
"""

import os
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

# API key header name
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key() -> str:
    """
    Get the API key from environment variable.

    Raises:
        RuntimeError: If API_KEY is not set
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError(
            "API_KEY environment variable is not set. "
            "Set it in your .env file or environment."
        )
    return api_key


def verify_api_key(api_key_header: str | None = Security(API_KEY_HEADER)) -> str:
    """
    Verify the API key from the request header.

    Args:
        api_key_header: The API key from the X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
        )

    expected_key = get_api_key()

    if api_key_header != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return api_key_header


# Dependency for requiring API key authentication
# Usage: def endpoint(api_key: RequireAPIKey): ...
RequireAPIKey = Annotated[str, Depends(verify_api_key)]
