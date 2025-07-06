import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config.settings import settings

# Configure logger
logger = logging.getLogger("api.auth")

# Define API key header schema
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def authenticate_token(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Authenticate API requests using API key

    Args:
        api_key: API key from request header

    Returns:
        The authenticated API key if valid

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        logger.warning("API key missing in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key: {api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    logger.debug(f"Authenticated API request with key: {api_key[:5]}...")
    return api_key
